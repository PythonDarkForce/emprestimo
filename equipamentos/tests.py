from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
from .models import Equipamento, Requisicao, CategoriaEquipamento
from .services import processar_devolucao


class ProcessarDevolucaoTestCase(TransactionTestCase):
    """Test cases for processar_devolucao service"""

    def setUp(self):
        """Set up test data"""
        # Create users
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.staff_user = User.objects.create_user(username='staffuser', password='testpass', is_staff=True)
        
        # Create category
        self.categoria = CategoriaEquipamento.objects.create(
            nome='Câmeras',
            descricao='Câmeras de vídeo'
        )
        
        # Create equipment
        self.equipamento1 = Equipamento.objects.create(
            categoria=self.categoria,
            nome='Câmera Sony',
            marca='Sony',
            modelo='A7III',
            numero_serie='SN001',
            codigo_interno='CAM001',
            estado='emprestado',
            valor_estimado=2000.00,
            data_aquisicao=timezone.now().date()
        )
        
        self.equipamento2 = Equipamento.objects.create(
            categoria=self.categoria,
            nome='Lente 50mm',
            marca='Sony',
            modelo='FE 50mm',
            numero_serie='SN002',
            codigo_interno='LEN001',
            estado='emprestado',
            valor_estimado=500.00,
            data_aquisicao=timezone.now().date()
        )
        
        # Create requisition
        self.requisicao = Requisicao.objects.create(
            utilizador=self.user,
            data_inicio_prevista=timezone.now().date(),
            data_fim_prevista=timezone.now().date() + timedelta(days=7),
            motivo='Projeto de teste',
            estado='em_curso',
            data_entrega_real=timezone.now()
        )
        self.requisicao.equipamentos.add(self.equipamento1, self.equipamento2)

    @patch('equipamentos.services.devolucao.async_to_sync')
    def test_processar_devolucao_sucesso(self, mock_async):
        """Test successful return processing"""
        # Mock WebSocket
        mock_channel_layer = MagicMock()
        mock_async.return_value = MagicMock()
        
        resultado = processar_devolucao(
            emprestimo_id=self.requisicao.id,
            observacao='Equipamento em bom estado',
            operador=self.staff_user
        )
        
        # Verify result
        self.assertTrue(resultado['devolucao_efetivada'])
        self.assertEqual(resultado['emprestimo'].id, self.requisicao.id)
        self.assertIn('sucesso', resultado['mensagem'].lower())
        
        # Verify requisition updated
        self.requisicao.refresh_from_db()
        self.assertEqual(self.requisicao.estado, 'concluida')
        self.assertIsNotNone(self.requisicao.data_devolucao_real)
        self.assertEqual(self.requisicao.observacoes_devolucao, 'Equipamento em bom estado')
        
        # Verify equipment availability
        self.equipamento1.refresh_from_db()
        self.equipamento2.refresh_from_db()
        self.assertEqual(self.equipamento1.estado, 'disponivel')
        self.assertEqual(self.equipamento2.estado, 'disponivel')

    @patch('equipamentos.services.devolucao.async_to_sync')
    def test_processar_devolucao_idempotente(self, mock_async):
        """Test idempotent behavior - already returned"""
        # First return
        processar_devolucao(emprestimo_id=self.requisicao.id)
        
        # Second return (should be idempotent)
        resultado = processar_devolucao(emprestimo_id=self.requisicao.id)
        
        # Verify idempotency
        self.assertFalse(resultado['devolucao_efetivada'])
        self.assertIn('já foi devolvido', resultado['mensagem'].lower())

    def test_processar_devolucao_emprestimo_nao_existe(self):
        """Test return processing for non-existent loan"""
        resultado = processar_devolucao(emprestimo_id=99999)
        
        # Verify result
        self.assertFalse(resultado['devolucao_efetivada'])
        self.assertIsNone(resultado['emprestimo'])
        self.assertIn('não encontrado', resultado['mensagem'].lower())

    @patch('equipamentos.services.devolucao.async_to_sync')
    def test_processar_devolucao_com_data_customizada(self, mock_async):
        """Test return processing with custom date"""
        data_customizada = timezone.now() - timedelta(days=1)
        
        resultado = processar_devolucao(
            emprestimo_id=self.requisicao.id,
            data_devolucao=data_customizada
        )
        
        # Verify custom date
        self.assertTrue(resultado['devolucao_efetivada'])
        self.requisicao.refresh_from_db()
        self.assertEqual(self.requisicao.data_devolucao_real, data_customizada)

    @patch('equipamentos.services.devolucao.async_to_sync')
    def test_processar_devolucao_emite_evento_websocket(self, mock_async):
        """Test that WebSocket event is emitted"""
        mock_group_send = MagicMock()
        mock_async.return_value = mock_group_send
        
        with patch('equipamentos.services.devolucao.get_channel_layer') as mock_channel:
            mock_channel.return_value = MagicMock()
            
            resultado = processar_devolucao(emprestimo_id=self.requisicao.id)
            
            # Verify WebSocket event was sent
            self.assertTrue(resultado['devolucao_efetivada'])
            mock_async.assert_called()


class APIDevolucaoTestCase(TestCase):
    """Test cases for API endpoint"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.staff_user = User.objects.create_user(username='staffuser', password='testpass', is_staff=True)
        
        # Create category
        self.categoria = CategoriaEquipamento.objects.create(
            nome='Câmeras',
            descricao='Câmeras de vídeo'
        )
        
        # Create equipment
        self.equipamento = Equipamento.objects.create(
            categoria=self.categoria,
            nome='Câmera Sony',
            marca='Sony',
            modelo='A7III',
            numero_serie='SN001',
            codigo_interno='CAM001',
            estado='emprestado',
            valor_estimado=2000.00,
            data_aquisicao=timezone.now().date()
        )
        
        # Create requisition
        self.requisicao = Requisicao.objects.create(
            utilizador=self.user,
            data_inicio_prevista=timezone.now().date(),
            data_fim_prevista=timezone.now().date() + timedelta(days=7),
            motivo='Projeto de teste',
            estado='em_curso',
            data_entrega_real=timezone.now()
        )
        self.requisicao.equipamentos.add(self.equipamento)

    @patch('equipamentos.services.devolucao.async_to_sync')
    def test_api_devolucao_requer_staff(self, mock_async):
        """Test that API requires staff permission"""
        # Login as regular user
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.post(f'/api/emprestimos/{self.requisicao.id}/devolver/')
        
        # Should redirect to login or return forbidden
        self.assertNotEqual(response.status_code, 200)

    @patch('equipamentos.services.devolucao.async_to_sync')
    def test_api_devolucao_sucesso(self, mock_async):
        """Test successful API call"""
        # Login as staff
        self.client.login(username='staffuser', password='testpass')
        
        response = self.client.post(
            f'/api/emprestimos/{self.requisicao.id}/devolver/',
            data='{"observacao": "Tudo OK"}',
            content_type='application/json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('emprestimo', data)
        self.assertEqual(data['emprestimo']['estado'], 'concluida')

    @patch('equipamentos.services.devolucao.async_to_sync')
    def test_api_devolucao_sem_body(self, mock_async):
        """Test API call without request body"""
        # Login as staff
        self.client.login(username='staffuser', password='testpass')
        
        response = self.client.post(f'/api/emprestimos/{self.requisicao.id}/devolver/')
        
        # Should still work
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    def test_api_devolucao_emprestimo_invalido(self):
        """Test API call with invalid loan ID"""
        # Login as staff
        self.client.login(username='staffuser', password='testpass')
        
        response = self.client.post('/api/emprestimos/99999/devolver/')
        
        # Should return error
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])


class IntegrationTestCase(TransactionTestCase):
    """Integration tests for the complete flow"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create users
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.staff_user = User.objects.create_user(username='staffuser', password='testpass', is_staff=True)
        
        # Create category
        self.categoria = CategoriaEquipamento.objects.create(
            nome='Câmeras',
            descricao='Câmeras de vídeo'
        )
        
        # Create equipment
        self.equipamento = Equipamento.objects.create(
            categoria=self.categoria,
            nome='Câmera Sony',
            marca='Sony',
            modelo='A7III',
            numero_serie='SN001',
            codigo_interno='CAM001',
            estado='disponivel',
            valor_estimado=2000.00,
            data_aquisicao=timezone.now().date()
        )

    @patch('equipamentos.services.devolucao.async_to_sync')
    def test_fluxo_completo_emprestimo_devolucao(self, mock_async):
        """Test complete loan and return flow"""
        # Create loan
        requisicao = Requisicao.objects.create(
            utilizador=self.user,
            data_inicio_prevista=timezone.now().date(),
            data_fim_prevista=timezone.now().date() + timedelta(days=7),
            motivo='Projeto de teste',
            estado='em_curso',
            data_entrega_real=timezone.now()
        )
        requisicao.equipamentos.add(self.equipamento)
        
        # Update equipment state
        self.equipamento.estado = 'emprestado'
        self.equipamento.save()
        
        # Process return
        self.client.login(username='staffuser', password='testpass')
        response = self.client.post(
            f'/api/emprestimos/{requisicao.id}/devolver/',
            data='{"observacao": "Equipamento devolvido em perfeito estado"}',
            content_type='application/json'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Verify loan state
        requisicao.refresh_from_db()
        self.assertEqual(requisicao.estado, 'concluida')
        self.assertIsNotNone(requisicao.data_devolucao_real)
        
        # Verify equipment available again
        self.equipamento.refresh_from_db()
        self.assertEqual(self.equipamento.estado, 'disponivel')

