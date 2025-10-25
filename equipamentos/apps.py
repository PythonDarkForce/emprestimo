"""
App configuration for equipamentos
"""

from django.apps import AppConfig


class EquipamentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'equipamentos'
    verbose_name = 'Gestão de Equipamentos'

    def ready(self):
        import equipamentos.signals  # Importar signals quando app estiver pronto

"""
Este ficheiro:

**Configura a aplicação Django** com:

1. **default_auto_field** - Define o tipo de campo para chaves primárias (BigAutoField)

2. **name** - Nome da aplicação (`equipamentos`)

3. **verbose_name** - Nome legível que aparece no Django Admin

4. **ready()** - Método executado quando a app está pronta
   - **CRÍTICO**: Importa `equipamentos.signals` para registrar os signals
   - Sem isto, as notificações WebSocket **NÃO funcionam**!

**Importante**: 
- Coloque este ficheiro em `equipamentos/apps.py`
- O método `ready()` é chamado automaticamente pelo Django
- Garante que os signals sejam registrados antes do sistema iniciar

**Fluxo:**
```
Django inicia
    ↓
apps.py → ready()
    ↓
signals.py é importado
    ↓
@receiver decorators registram os signals
    ↓
Sistema pronto para enviar notificações!
"""