# backend/apps/libretas/apps.py
from django.apps import AppConfig

class LibretasConfig(AppConfig):
    name = "apps.libretas"
    verbose_name = "Módulo de Libretas"

    def ready(self):
        # Inyección simple de DataPort (Excel local).
        # Si migras a MySQL/DataPort real en S2, cambia aquí.
        from .services import excel_adapter
        excel_adapter.dataport = excel_adapter.ExcelDataPort()
