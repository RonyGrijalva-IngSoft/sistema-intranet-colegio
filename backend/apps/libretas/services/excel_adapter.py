# backend/apps/libretas/services/excel_adapter.py
"""
DataPort local (S1): lee un Excel "dummy" o entrega datos de ejemplo si no hay ruta.
En S2 podrás mapear columnas reales por Hoja1, etc.
"""
import os
from typing import List, Dict, Any, Optional

try:
    from openpyxl import load_workbook
except Exception:
    load_workbook = None  # Tests se encargan de instalar openpyxl.

dataport = None  # Será inyectado en apps.LibretasConfig.ready()

class ExcelDataPort:
    def __init__(self, path_env_var: str = "LIBRETAS_DATA_EXCEL_PATH"):
        self.path_env_var = path_env_var

    def _get_path(self) -> Optional[str]:
        path = os.environ.get(self.path_env_var)
        return path if path and os.path.exists(path) else None

    def alumnos_por_seccion_y_curso(self, seccion_id: int, curso_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retorna lista mínima de alumnos con nota bimestral "dummy" para S1.
        En S2 incorporaremos lectura real desde Excel (Hoja1) o MySQL.
        """
        path = self._get_path()
        if path and load_workbook:
            # Ejemplo mínimo: lee la primera hoja y arma filas {alumnoId, alumno, nota_num}
            wb = load_workbook(path, data_only=True)
            ws = wb.active
            filas = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                # Ajusta a tu layout real. Aquí asumimos: A=alumno, B=nota
                alumno = (row[0] or "").strip() if row[0] else "Alumno"
                nota = float(row[1] or 14)
                filas.append({
                    "alumnoId": f"ALU-{alumno[:3].upper()}",
                    "alumno": alumno,
                    "nota_num": nota,
                })
            return filas

        # Fallback de ejemplo si no hay Excel:
        return [
            {"alumnoId": "ALU-001", "alumno": "Arias Espinoza Lian Junior", "nota_num": 12.6},
            {"alumnoId": "ALU-002", "alumno": "Carreño Cuarta Mathias Rene", "nota_num": 13.3},
            {"alumnoId": "ALU-003", "alumno": "Veliz Briceño Maria Jesus", "nota_num": 16.9},
        ]
