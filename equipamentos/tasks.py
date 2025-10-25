from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from equipamentos.models import Requisicao
from equipamentos.signals import enviar_notificacao_websocket


def verificar_requisicoes_proximas_vencimento():
    """Verificar requisições que estão próximas do vencimento"""
    amanha = timezone.now().date() + timedelta(days=1)

    requisicoes_proximas = Requisicao.objects.filter(
        estado='em_curso',
        data_fim_prevista=amanha
    )

    for req in requisicoes_proximas:
        user_group = f'user_{req.utilizador.id}'
        enviar_notificacao_websocket(
            user_group,
            'lembrete_devolucao',
            {
                'requisicao_id': req.id,
                'message': f'Lembre-se: requisição #{req.id} vence amanhã!',
                'dias_restantes': 1
            }
        )


def verificar_requisicoes_atrasadas():
    """Verificar requisições atrasadas"""
    hoje = timezone.now().date()

    requisicoes_atrasadas = Requisicao.objects.filter(
        estado='em_curso',
        data_fim_prevista__lt=hoje
    )

    for req in requisicoes_atrasadas:
        # Atualizar estado
        if req.estado != 'atrasada':
            req.estado = 'atrasada'
            req.save()

        # Notificar utilizador
        user_group = f'user_{req.utilizador.id}'
        enviar_notificacao_websocket(
            user_group,
            'requisicao_atrasada',
            {
                'requisicao_id': req.id,
                'message': f'ATENÇÃO: Requisição #{req.id} está atrasada!'
            }
        )

        # Notificar staff
        enviar_notificacao_websocket(
            'staff_notifications',
            'requisicao_atrasada',
            {
                'requisicao_id': req.id,
                'message': f'Requisição #{req.id} de {req.utilizador.get_full_name()} está atrasada!'
            }
        )