"""
Signals para enviar notificações em tempo real
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Requisicao, Equipamento
from django.utils import timezone


def enviar_notificacao_websocket(group_name, event_type, data):
    """Helper para enviar notificações via WebSocket"""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': event_type,
            **data
        }
    )


@receiver(post_save, sender=Requisicao)
def requisicao_criada_ou_atualizada(sender, instance, created, **kwargs):
    """Signal quando requisição é criada ou atualizada"""

    if created:
        # Notificar staff sobre nova requisição
        enviar_notificacao_websocket(
            'staff_notifications',
            'nova_requisicao',
            {
                'requisicao_id': instance.id,
                'utilizador': instance.utilizador.get_full_name() or instance.utilizador.username,
                'message': f'Nova requisição #{instance.id} de {instance.utilizador.get_full_name() or instance.utilizador.username}'
            }
        )

        # Atualizar lista de requisições
        enviar_notificacao_websocket(
            'requisicoes_updates',
            'requisicao_update',
            {
                'requisicao_id': instance.id,
                'estado': instance.estado,
                'action': 'created'
            }
        )

    else:
        # Verificar se o estado mudou
        try:
            old_instance = Requisicao.objects.get(pk=instance.pk)
        except Requisicao.DoesNotExist:
            return

        # Prevenir loops infinitos - verificar se realmente mudou
        if hasattr(instance, '_skip_signal'):
            return

        if old_instance.estado != instance.estado:
            # Notificar utilizador sobre mudança de estado
            user_group = f'user_{instance.utilizador.id}'

            if instance.estado == 'aprovada':
                enviar_notificacao_websocket(
                    user_group,
                    'requisicao_aprovada',
                    {
                        'requisicao_id': instance.id,
                        'message': f'Sua requisição #{instance.id} foi aprovada!'
                    }
                )

            elif instance.estado == 'rejeitada':
                enviar_notificacao_websocket(
                    user_group,
                    'requisicao_rejeitada',
                    {
                        'requisicao_id': instance.id,
                        'message': f'Sua requisição #{instance.id} foi rejeitada.',
                        'motivo': instance.observacoes_aprovacao or ''
                    }
                )

            elif instance.estado == 'em_curso':
                enviar_notificacao_websocket(
                    user_group,
                    'equipamento_entregue',
                    {
                        'requisicao_id': instance.id,
                        'message': f'Equipamento da requisição #{instance.id} foi entregue!'
                    }
                )

            # Atualizar lista de requisições
            enviar_notificacao_websocket(
                'requisicoes_updates',
                'requisicao_update',
                {
                    'requisicao_id': instance.id,
                    'estado': instance.estado,
                    'action': 'updated'
                }
            )


@receiver(post_save, sender=Equipamento)
def equipamento_atualizado(sender, instance, created, **kwargs):
    """Signal quando equipamento é atualizado"""

    if not created:
        # Notificar sobre mudança de estado do equipamento
        enviar_notificacao_websocket(
            'equipamentos_updates',
            'equipamento_update',
            {
                'equipamento_id': instance.id,
                'estado': instance.estado,
                'codigo_interno': instance.codigo_interno
            }
        )