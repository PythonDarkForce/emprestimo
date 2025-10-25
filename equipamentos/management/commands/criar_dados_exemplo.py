# Comando para criar dados de exemplo
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from equipamentos.models import CategoriaEquipamento, Equipamento
from datetime import date
from decimal import Decimal


class Command(BaseCommand):
    help = 'Cria dados de exemplo para testar o sistema'

    def handle(self, *args, **kwargs):
        # Criar superusuário se não existir
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superusuário criado: admin/admin123'))

        # Criar utilizador normal
        if not User.objects.filter(username='joao').exists():
            User.objects.create_user('joao', 'joao@example.com', 'senha123', 
                                    first_name='João', last_name='Silva')
            self.stdout.write(self.style.SUCCESS('Utilizador criado: joao/senha123'))

        # Criar categorias
        categorias_data = [
            {'nome': 'Câmeras', 'descricao': 'Câmeras de fotografia e vídeo'},
            {'nome': 'Lentes', 'descricao': 'Lentes intercambiáveis'},
            {'nome': 'Iluminação', 'descricao': 'Equipamento de iluminação'},
            {'nome': 'Áudio', 'descricao': 'Microfones e gravadores de áudio'},
            {'nome': 'Estabilização', 'descricao': 'Tripés, gimbals e estabilizadores'},
            {'nome': 'Acessórios', 'descricao': 'Diversos acessórios'},
        ]

        categorias = {}
        for cat_data in categorias_data:
            cat, created = CategoriaEquipamento.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={'descricao': cat_data['descricao']}
            )
            categorias[cat_data['nome']] = cat
            if created:
                self.stdout.write(f'Categoria criada: {cat.nome}')

        # Criar equipamentos
        equipamentos_data = [
            {
                'categoria': 'Câmeras',
                'nome': 'Canon EOS R5',
                'marca': 'Canon',
                'modelo': 'EOS R5',
                'numero_serie': 'CR5-001',
                'codigo_interno': 'CAM-001',
                'descricao': 'Câmera mirrorless full-frame 45MP',
                'valor_estimado': Decimal('3500.00'),
            },
            {
                'categoria': 'Câmeras',
                'nome': 'Sony A7 IV',
                'marca': 'Sony',
                'modelo': 'A7 IV',
                'numero_serie': 'SA7-001',
                'codigo_interno': 'CAM-002',
                'descricao': 'Câmera mirrorless full-frame 33MP',
                'valor_estimado': Decimal('2800.00'),
            },
            {
                'categoria': 'Lentes',
                'nome': 'Canon RF 24-70mm f/2.8',
                'marca': 'Canon',
                'modelo': 'RF 24-70mm f/2.8 L IS USM',
                'numero_serie': 'RF2470-001',
                'codigo_interno': 'LENT-001',
                'descricao': 'Lente zoom standard profissional',
                'valor_estimado': Decimal('2200.00'),
            },
            {
                'categoria': 'Lentes',
                'nome': 'Sony FE 70-200mm f/2.8',
                'marca': 'Sony',
                'modelo': 'FE 70-200mm f/2.8 GM OSS',
                'numero_serie': 'SFE70200-001',
                'codigo_interno': 'LENT-002',
                'descricao': 'Lente telephoto profissional',
                'valor_estimado': Decimal('2600.00'),
            },
            {
                'categoria': 'Iluminação',
                'nome': 'Godox SL-60W',
                'marca': 'Godox',
                'modelo': 'SL-60W',
                'numero_serie': 'GX60-001',
                'codigo_interno': 'ILU-001',
                'descricao': 'LED contínuo 60W',
                'valor_estimado': Decimal('180.00'),
            },
            {
                'categoria': 'Áudio',
                'nome': 'Rode VideoMic Pro',
                'marca': 'Rode',
                'modelo': 'VideoMic Pro',
                'numero_serie': 'RVP-001',
                'codigo_interno': 'AUD-001',
                'descricao': 'Microfone shotgun para câmera',
                'valor_estimado': Decimal('220.00'),
            },
            {
                'categoria': 'Estabilização',
                'nome': 'DJI Ronin-S',
                'marca': 'DJI',
                'modelo': 'Ronin-S',
                'numero_serie': 'DRS-001',
                'codigo_interno': 'EST-001',
                'descricao': 'Gimbal de 3 eixos',
                'valor_estimado': Decimal('650.00'),
            },
        ]

        for eq_data in equipamentos_data:
            categoria = categorias[eq_data.pop('categoria')]
            eq, created = Equipamento.objects.get_or_create(
                codigo_interno=eq_data['codigo_interno'],
                defaults={
                    **eq_data,
                    'categoria': categoria,
                    'data_aquisicao': date(2023, 1, 15),
                    'estado': 'disponivel'
                }
            )
            if created:
                self.stdout.write(f'Equipamento criado: {eq.codigo_interno}')

        self.stdout.write(self.style.SUCCESS('Dados de exemplo criados com sucesso!'))