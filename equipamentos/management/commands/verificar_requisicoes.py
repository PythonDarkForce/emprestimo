from django.core.management.base import BaseCommand
from equipamentos.tasks import verificar_requisicoes_proximas_vencimento, verificar_requisicoes_atrasadas


class Command(BaseCommand):
    help = 'Verifica requisições próximas do vencimento e atrasadas'

    def handle(self, *args, **kwargs):
        self.stdout.write('Verificando requisições...')

        verificar_requisicoes_proximas_vencimento()
        self.stdout.write(self.style.SUCCESS('✓ Verificação de vencimentos concluída'))

        verificar_requisicoes_atrasadas()
        self.stdout.write(self.style.SUCCESS('✓ Verificação de atrasos concluída'))

        self.stdout.write(self.style.SUCCESS('Verificação completa!'))
        
# Para executar periodicamente, adicione ao crontab:
# */30 * * * * cd /caminho/projeto && /caminho/venv/bin/python manage.py verificar_requisicoes