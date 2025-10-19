from typing import Protocol, List, Dict, Any

class IDataPort(Protocol):
    def alumnos_por_seccion(self, seccion_id: int) -> List[Dict[str, Any]]:
        """Debe devolver lista de alumnos: [{id:int, apellidos:str, nombres:str}, ...]"""
        ...

    def cursos_de_grado(self, grado: int) -> List[Dict[str, Any]]:
        """Debe devolver lista de cursos: [{id:int, nombre:str}, ...]"""
        ...

    def notas_de_curso(self, grado: int, seccion_id: int, curso_id: int) -> Dict[int, Dict[str, float]]:
        """
        Debe devolver diccionario:
        { alumno_id: {"B1":float,"B2":float,"B3":float,"B4":float} }
        """
        ...
