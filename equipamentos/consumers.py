"""
WebSocket Consumers para comunicação em tempo real
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Requisicao, Equipamento


class NotificacoesConsumer(AsyncWebsocketConsumer):
    """Consumer para notificações em tempo real"""

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        # Grupo de notificações do utilizador
        self.user_group_name = f'user_{self.user.id}'

        # Entrar no grupo
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        # Adicionar utilizador à lista de online
        await self.channel_layer.group_send(
            'staff_notifications',
            {
                'type': 'user_online',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )

        # Se for staff, entrar no grupo de staff
        if self.user.is_staff:
            await self.channel_layer.group_add(
                'staff_notifications',
                self.channel_name
            )

        await self.accept()

        # Enviar mensagem de confirmação
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectado ao sistema de notificações'
        }))

    async def disconnect(self, close_code):

        # Remover da lista de online
        await self.channel_layer.group_send(
            'staff_notifications',
            {
                'type': 'user_offline',
                'user_id': self.user.id
            }
        )

        # Sair dos grupos
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

        if self.user.is_staff:
            await self.channel_layer.group_discard(
                'staff_notifications',
                self.channel_name
            )

    async def receive(self, text_data):
        """Receber mensagens do cliente"""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'timestamp': data.get('timestamp')
            }))

    # Handlers para diferentes tipos de notificações
    async def nova_requisicao(self, event):
        """Notificar staff sobre nova requisição"""
        await self.send(text_data=json.dumps({
            'type': 'nova_requisicao',
            'requisicao_id': event['requisicao_id'],
            'utilizador': event['utilizador'],
            'message': event['message']
        }))

    async def requisicao_aprovada(self, event):
        """Notificar utilizador que requisição foi aprovada"""
        await self.send(text_data=json.dumps({
            'type': 'requisicao_aprovada',
            'requisicao_id': event['requisicao_id'],
            'message': event['message']
        }))

    async def requisicao_rejeitada(self, event):
        """Notificar utilizador que requisição foi rejeitada"""
        await self.send(text_data=json.dumps({
            'type': 'requisicao_rejeitada',
            'requisicao_id': event['requisicao_id'],
            'message': event['message'],
            'motivo': event.get('motivo', '')
        }))

    async def equipamento_entregue(self, event):
        """Notificar que equipamento foi entregue"""
        await self.send(text_data=json.dumps({
            'type': 'equipamento_entregue',
            'requisicao_id': event['requisicao_id'],
            'message': event['message']
        }))

    async def lembrete_devolucao(self, event):
        """Lembrete de devolução próxima"""
        await self.send(text_data=json.dumps({
            'type': 'lembrete_devolucao',
            'requisicao_id': event['requisicao_id'],
            'message': event['message'],
            'dias_restantes': event.get('dias_restantes', 0)
        }))

    async def requisicao_atrasada(self, event):
        """Alerta de requisição atrasada"""
        await self.send(text_data=json.dumps({
            'type': 'requisicao_atrasada',
            'requisicao_id': event['requisicao_id'],
            'message': event['message']
        }))


class RequisicoesConsumer(AsyncWebsocketConsumer):
    """Consumer para atualizações de requisições em tempo real"""

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        # Grupo geral de requisições
        self.room_group_name = 'requisicoes_updates'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def requisicao_update(self, event):
        """Enviar atualização de requisição"""
        await self.send(text_data=json.dumps({
            'type': 'requisicao_update',
            'requisicao_id': event['requisicao_id'],
            'estado': event['estado'],
            'action': event['action']
        }))


class EquipamentosConsumer(AsyncWebsocketConsumer):
    """Consumer para atualizações de equipamentos em tempo real"""

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = 'equipamentos_updates'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def equipamento_update(self, event):
        """Enviar atualização de estado de equipamento"""
        await self.send(text_data=json.dumps({
            'type': 'equipamento_update',
            'equipamento_id': event['equipamento_id'],
            'estado': event['estado'],
            'codigo_interno': event['codigo_interno']
        }))


class EmprestimosConsumer(AsyncWebsocketConsumer):
    """Consumer para atualizações de empréstimos em tempo real"""

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        self.room_group_name = 'emprestimos'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def emprestimo_update(self, event):
        """Enviar atualização de empréstimo"""
        await self.send(text_data=json.dumps({
            'type': event.get('type', 'emprestimo.updated'),
            'id': event.get('id'),
            'status': event.get('status'),
            'data_devolucao': event.get('data_devolucao'),
            'item_ids': event.get('item_ids', [])
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.requisicao_id = self.scope['url_route']['kwargs']['requisicao_id']
        self.room_group_name = f'chat_requisicao_{self.requisicao_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.scope['user'].username,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))