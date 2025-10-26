"""
WebSocket routing configuration
"""

from django.urls import re_path
from equipamentos import consumers

websocket_urlpatterns = [
    re_path(r'ws/notificacoes/$', consumers.NotificacoesConsumer.as_asgi()),
    re_path(r'ws/requisicoes/$', consumers.RequisicoesConsumer.as_asgi()),
    re_path(r'ws/equipamentos/$', consumers.EquipamentosConsumer.as_asgi()),
    re_path(r'ws/emprestimos/$', consumers.EmprestimosConsumer.as_asgi()),
]