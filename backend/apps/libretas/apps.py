from django.apps import AppConfig

class LibretasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.libretas"

    def ready(self):
        # elimina o comenta esto si lo tienes:
        # from .services import excel_adapter
        # excel_adapter.dataport = excel_adapter.ExcelDataPort()
        pass
