from django.apps import AppConfig

class LibretasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "libretas"

    def ready(self):
        try:
            from .services.pdf_bimestral import set_data_port
            from .services.excel_adapter import ExcelAdapter

            RUTA = r"C:\Users\Katherine\sistema-intranet-colegio\backend\REGISTRO AUXILIAR 6TO.xlsx"
            HOJA = "Hoja1"
            COLS = {
                "id": "ID",         # ← AJUSTAREMOS ESTOS NOMBRES cuando me pases tus cabeceras
                "apellidos": "APELLIDOS",
                "nombres": "NOMBRES",
                "curso_id": "CURSO_ID",
                "b1": "B1",
                "b2": "B2",
                "b3": "B3",
                "b4": "B4",
            }

            set_data_port(ExcelAdapter(RUTA, HOJA, cols_override=COLS))
        except Exception:
            # No bloquees arranque si falta algo fuera de esta rama
            pass
