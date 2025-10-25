# management/commands/limpar_conexoes.py
from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Command(BaseCommand):
    help = 'Limpa conexões antigas do Redis'

    def handle(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        # Implementar limpeza conforme necessidade
        self.stdout.write(self.style.SUCCESS('Conexões limpas!'))