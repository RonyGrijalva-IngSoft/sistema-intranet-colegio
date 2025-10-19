import psycopg2
import os
from dotenv import load_dotenv

import datetime
import re

# Cargar variables de entorno desde un archivo .env si existe
load_dotenv()

# Variables de configuración de la base de datos (se pueden establecer en .env)
DB_HOST = os.getenv('DB_HOST', '')
DB_NAME = os.getenv('DB_NAME', '')
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PORT = int(os.getenv('DB_PORT', os.getenv('PORT', 5432)))

def registrar_grado(nombre, nivel, anio):

    if not nombre or not nombre.strip():
        print(f"Error: El nombre no puede estar vacio.")
        return 

    if not nivel or not nivel.strip():
        print(f"Error: El nivel no puede estar vacio.")
        return

    nivel = nivel.strip().lower() 
    
    if nivel not in ['inicial', 'primaria', 'secundaria']:
        print(f"Error: El nivel '{nivel}' no es válido. Debe ser 'inicial', 'primaria' o 'secundaria'.")
        return

    try:
        anio = int(anio)
        anio_actual = datetime.date.today().year
        
        if anio < anio_actual or anio > anio_actual+1:
            print(f"Error: El año '{anio}' es incorrecto.")
            return
            
    except ValueError:
        print(f"Error: El año '{anio}' debe ser un valor numerico.")
        return
    
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conexion.cursor()

        sql = """INSERT INTO Grado (Nombre, Nivel, Anio)
                 VALUES (%s, %s, %s)"""

        datos = (nombre, nivel, anio)

        cursor.execute(sql, datos)
        conexion.commit()

        print(f"Grado '{nombre} - {nivel}' registrado con exito.")

    except psycopg2.Error as err:
        print(f"Error al registrar el grado: {err}")

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()



def registrar_grado_trabajado(nombre, id_grado, id_tutor):

    if not nombre or not nombre.strip():
        print(f"Error: El nombre no puede estar vacio.")
        return 
    
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conexion.cursor()

        sql = """INSERT INTO Grado_trabajado
                 (nombre, IdGrado, IdTutor)
                 VALUES (%s, %s, %s)"""

        datos = (nombre, id_grado, id_tutor)

        cursor.execute(sql, datos)
        conexion.commit()

        print(f"Grado trabajado '{nombre}' registrado con éxito.")

    except psycopg2.Error as err:
        print(f"Error al registrar el grado trabajado: {err}")

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()


def asignar_tutor_a_salon(id_tutor, id_grado_trabajado):
    conexion = None
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conexion.cursor()

        sql = """UPDATE grado_trabajado
                 SET IdTutor = %s
                 WHERE IdGrado_trabajado = %s"""
        
        datos = (id_tutor, id_grado_trabajado)

        cursor.execute(sql, datos)

        row_count = cursor.rowcount
        conexion.commit()

        if row_count > 0:
            print(f"Exito: Tutor (Profesor ID: {id_tutor}) asignado al Salon (Grado_Trabajado ID: {id_grado_trabajado}).")
        else:
            print(f"Aviso: No se encontro el salon con ID {id_grado_trabajado}. No se hizo ningun cambio.")

    except psycopg2.Error as err:
        if err.pgcode == '23503': 
             print(f"Error: No se pudo asignar. El profesor con ID {id_tutor} no existe.")
        else:
            print(f"Error al asignar el tutor: {err}")
        if conexion:
            conexion.rollback() 
    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()


def registrar_alumno(codigo_ugel, nombres, apellidos, edad, dni, id_grado_trabajado, id_padre):

    try:
        codigo_ugel_int = int(codigo_ugel)
        if codigo_ugel_int <= 0:
            print(f"Error: El Codigo UGEL '{codigo_ugel}' no es valido.")
            return
    except ValueError:
        print(f"Error: El Codigo UGEL '{codigo_ugel}' debe ser un valor numerico.")
        return

    if not nombres or not nombres.strip():
        print("Error: El campo 'Nombres' no puede estar vacio.")
        return

    if not apellidos or not apellidos.strip():
        print("Error: El campo 'Apellidos' no puede estar vacio.")
        return

    try:
        edad_int = int(edad)
        if not (3 <= edad_int <= 100):
            print(f"Error: La edad '{edad_int}' no es valida.")
            return
    except ValueError:
        print(f"Error: La edad '{edad}' debe ser un valor numerico.")
        return

    dni_limpio = str(dni).strip()
    if not dni_limpio.isdigit() or len(dni_limpio) != 8:
        print(f"Error: El DNI '{dni}' no es valido.")
        return
    
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=5432
        )

        cursor = conexion.cursor()

        sql = """INSERT INTO Alumno
                 (CodigoUGEL, Nombres, Apellidos, Edad, DNI, IdGrado_trabajado, IdPadre)
                 VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING IdAlumno"""

        datos_alumno = (codigo_ugel, nombres, apellidos, edad, dni, id_grado_trabajado, id_padre)

        cursor.execute(sql, datos_alumno)
        id_nuevo = cursor.fetchone()[0]
        conexion.commit()

        print(f"Alumno '{nombres} {apellidos}' registrado con exito. ID: {id_nuevo}")

    except psycopg2.Error as err:
        print(f"Error al registrar alumno: {err}")

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()



def registrar_profesor(nombres, apellidos, dni, correo, contrasena, telefono):
    if not nombres or not nombres.strip():
        print("Error: El campo 'Nombres' no puede estar vacio.")
        return

    if not apellidos or not apellidos.strip():
        print("Error: El campo 'Apellidos' no puede estar vacio.")
        return
    
    dni_limpio = str(dni).strip()
    if not dni_limpio.isdigit() or len(dni_limpio) != 8:
        print(f"Error: El DNI '{dni}' no es valido.")
        return
    
    correo_limpio = correo.strip()
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not correo_limpio or not re.match(email_regex, correo_limpio):
        print(f"Error: El correo '{correo}' no tiene un formato valido.")
        return
    
    if not contrasena or len(contrasena) < 8:
        print("Error: La contraseña no puede estar vacia y debe tener al menos 8 caracteres.")
        return
    
    telefono = str(telefono).strip()
    if not telefono.isdigit():
        print("Error: El telefono no es valido. Debe contener solo numeros.")
        return
    if len(telefono) != 9:
        print("Error: El telefono no es valido. Debe tener exactamente 9 digitos.")
        return    
    if not telefono.startswith('9'):
        print("Error: El celular no es valido. Los numeros de celular en Peru deben empezar con 9.")
        return
    
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        sql = """INSERT INTO Profesor
                 (Nombres, Apellidos, DNI, Correo, Contraseña, Telefono)
                 VALUES (%s, %s, %s, %s, %s, %s)"""

        datos_profesor = (nombres, apellidos, dni, correo, contrasena, telefono)

        cursor.execute(sql, datos_profesor)
        conexion.commit()

        print(f"Profesor '{nombres} {apellidos}' registrado con exito.")

    except psycopg2.Error as err:
        print(f"Error al registrar profesor: {err}")

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()


def registrar_padre(nombres, apellidos, dni, telefono):
    if not nombres or not nombres.strip():
        print("Error: El campo 'Nombres' no puede estar vacio.")
        return

    if not apellidos or not apellidos.strip():
        print("Error: El campo 'Apellidos' no puede estar vacio.")
        return
    
    dni_limpio = str(dni).strip()
    if not dni_limpio.isdigit() or len(dni_limpio) != 8:
        print(f"Error: El DNI '{dni}' no es valido.")
        return
    
    telefono = str(telefono).strip()
    if not telefono.isdigit():
        print("Error: El telefono no es valido. Debe contener solo numeros.")
        return
    if len(telefono) != 9:
        print("Error: El telefono no es valido. Debe tener exactamente 9 digitos.")
        return    
    if not telefono.startswith('9'):
        print("Error: El celular no es valido. Los numeros de celular en Peru deben empezar con 9.")
        return
    
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        sql = """INSERT INTO Padre
                 (Nombres, Apellidos, DNI, Telefono)
                 VALUES (%s, %s, %s, %s)"""

        datos_padre = (nombres, apellidos, dni, telefono)

        cursor.execute(sql, datos_padre)
        conexion.commit()

        print(f"Padre/Madre '{nombres} {apellidos}' registrado con exito.")

    except psycopg2.Error as err:
        print(f"Error al registrar padre: {err}")

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()


def registrar_asignatura(area, nombre, cant_horas, id_grado):

    if not nombre or not nombre.strip():
        print("Error: El campo 'Nombre' no puede estar vacio.")
        return
    
    if not area or not area.strip():
        print("Error: El campo 'Area' no puede estar vacio.")
        return
    
    try:
        cant_horas = int(cant_horas)
        if not (1 <= cant_horas <= 10):
            print("Error: La cantidad de horases valida.")
            return
    except ValueError:
        print("Error: La cantidad de horas debe ser un valor numerico.")
        return
    
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        sql = """INSERT INTO Asignatura (Area, Nombre, Cant_horas, IdGrado)
                 VALUES (%s, %s, %s, %s)"""

        datos = (area, nombre, cant_horas, id_grado)

        cursor.execute(sql, datos)
        conexion.commit()

        print(f"Asignatura '{nombre}' registrada con exito.")

    except psycopg2.Error as err:
        print(f"Error al registrar la asignatura: {err}")

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()


def registrar_asignatura_trabajada(id_grado_trabajado, id_profesor, id_asignatura):
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        sql = """INSERT INTO Asignatura_trabajada (IdGrado_trabajado, IdProfesor, IdAsignatura)
                 VALUES (%s, %s, %s)"""

        datos = (id_grado_trabajado, id_profesor, id_asignatura)

        cursor.execute(sql, datos)
        conexion.commit()

        print(f"Asignatura asignada al profesor en la clase Id:{id_grado_trabajado} con éxito.")

    except psycopg2.Error as err:
        print(f"Error al registrar la asignatura trabajada: {err}")

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()




def registrar_nota_simple(id_alumno, id_asignatura_trabajada, calificacion, nombre_nota,bimestre):

    try:
        calificacion = float(calificacion)
        if not (0 <= calificacion <= 20):
            print("Error: La calificacion no es valida.")
            return
    except ValueError:
        print("Error: La calificacion debe ser un valor numerico.")
        return
    
    if not nombre_nota or not nombre_nota.strip():
        print("Error: El campo 'Nombre' no puede estar vacio.")
        return
    
    try:
        bimestre = int(bimestre)
        if not (1 <= bimestre <= 4):
            print("Error: El bimestre no es valido.")
            return
    except ValueError:
        print("Error: El bimestre debe ser un valor numerico.")
        return

    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        sql = """INSERT INTO Nota (IdAlumno, IdAsignatura_trabajada, Calificacion, Nombre, Bimestre)
                 VALUES (%s, %s, %s, %s, %s)"""

        datos = (id_alumno, id_asignatura_trabajada, calificacion, nombre_nota, bimestre)

        cursor.execute(sql, datos)
        conexion.commit()

        print(f"Nota '{nombre_nota}' ({calificacion}) registrada con exito para el alumno ID:{id_alumno}.")

    except psycopg2.Error as e:
        print(f"Error al registrar la nota: {e}")

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()



def obtener_notas_de_bimestre(id_alumno, id_asignatura_trabajada, bimestre):

    try:
        bimestre = int(bimestre)
        if not (1 <= bimestre <= 4):
            print("Error: El bimestre no es valido.")
            return
    except ValueError:
        print("Error: El bimestre debe ser un valor numerico.")
        return

    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        sql = """
            SELECT Nombre, Calificacion
            FROM Nota
            WHERE IdAlumno = %s AND IdAsignatura_trabajada = %s AND Bimestre = %s
            ORDER BY IdNota;
        """

        cursor.execute(sql, (id_alumno, id_asignatura_trabajada, bimestre))
        
        return cursor.fetchall()

    except psycopg2.Error as e:
        print(f"Error al consultar las notas: {e}")
        return None

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()



def actualizar_detalle_boleta(id_boleta, id_asignatura_trabajada, bimestre, promedio_bimestral):

    try:
        bimestre = int(bimestre)
        if not (1 <= bimestre <= 4):
            print("Error: El bimestre no es valido.")
            return
    except ValueError:
        print("Error: El bimestre debe ser un valor numerico.")
        return
    
    try:
        promedio_bimestral = float(promedio_bimestral)
        if not (0 <= promedio_bimestral <= 20):
            print("Error: El promedio bimestral no es valido.")
            return
    except ValueError:
        print("Error: El promedio bimestral debe ser un valor numerico.")
        return

    conexion = None
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        cursor.execute("SELECT IdBoleta_Detalle FROM Boleta_Detalle WHERE IdBoleta = %s AND IdAsignatura_trabajada = %s", (id_boleta, id_asignatura_trabajada))
        resultado_detalle = cursor.fetchone()

        columna_bimestre = f"Nota_{bimestre}B"

        if resultado_detalle:
            id_boleta_detalle = resultado_detalle[0]
            sql = f"UPDATE Boleta_Detalle SET {columna_bimestre} = %s WHERE IdBoleta_Detalle = %s"
            cursor.execute(sql, (promedio_bimestral, id_boleta_detalle))
        else:
            sql = f"INSERT INTO Boleta_Detalle (IdBoleta, IdAsignatura_trabajada, {columna_bimestre}) VALUES (%s, %s, %s) RETURNING IdBoleta_Detalle"
            cursor.execute(sql, (id_boleta, id_asignatura_trabajada, promedio_bimestral))
            id_boleta_detalle = cursor.fetchone()[0]
        
        print(f"Promedio del bimestre {bimestre} registrado en el detalle de la boleta.")

        sql_promedio_asignatura = """
            UPDATE Boleta_Detalle SET Nota_Final = (
                (COALESCE(Nota_1B, 0) + COALESCE(Nota_2B, 0) + COALESCE(Nota_3B, 0) + COALESCE(Nota_4B, 0)) /
                (CASE WHEN Nota_1B IS NOT NULL THEN 1 ELSE 0 END +
                 CASE WHEN Nota_2B IS NOT NULL THEN 1 ELSE 0 END +
                 CASE WHEN Nota_3B IS NOT NULL THEN 1 ELSE 0 END +
                 CASE WHEN Nota_4B IS NOT NULL THEN 1 ELSE 0 END)
            ) WHERE IdBoleta_Detalle = %s
        """
        cursor.execute(sql_promedio_asignatura, (id_boleta_detalle,))
        print("Promedio final de la asignatura recalculado.")

        conexion.commit()
        print("Detalle de boleta actualizado con exito")

    except psycopg2.Error as e:
        print(f"Error al actualizar el detalle de la boleta: {e}")
        if conexion:
            conexion.rollback()
            print("Cambios revertidos.")
    finally:
        if conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()



def crear_boleta_vacia(id_alumno):
    conexion = None
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        anio_actual = datetime.date.today().year

        sql_verificar = "SELECT IdBoleta FROM Boleta WHERE IdAlumno = %s AND Anio = %s"
        cursor.execute(sql_verificar, (id_alumno, anio_actual))
        boleta_existente = cursor.fetchone()

        if boleta_existente:
            id_boleta = boleta_existente[0]
            print(f"La boleta para el alumno ID:{id_alumno} ya existe para el año {anio_actual}. ID de Boleta: {id_boleta}")
            return id_boleta

        cursor.execute("SELECT IdGrado_trabajado FROM Alumno WHERE IdAlumno = %s", (id_alumno,))
        resultado_grado = cursor.fetchone()
        if not resultado_grado:
            print(f"Error: No se encontro el alumno con ID:{id_alumno}")
            return None
        id_grado_trabajado = resultado_grado[0]

        cursor.execute("SELECT IdTutor FROM Grado_trabajado WHERE IdGrado_trabajado = %s", (id_grado_trabajado,))
        resultado_tutor = cursor.fetchone()
        if not resultado_tutor:
            print(f"Error: No se encontro un tutor para el grado trabajado ID:{id_grado_trabajado}")
            return None
        id_tutor = resultado_tutor[0]

        sql_crear = """
            INSERT INTO Boleta (IdAlumno, IdGrado_trabajado, IdTutor, Anio, Fecha_Emision)
            VALUES (%s, %s, %s, %s, %s) RETURNING IdBoleta
        """
        datos_boleta = (id_alumno, id_grado_trabajado, id_tutor, anio_actual, datetime.date.today())
        
        cursor.execute(sql_crear, datos_boleta)
        id_nueva_boleta = cursor.fetchone()[0]
        
        conexion.commit()
        
        print(f"Boleta vacia creada con exito para el alumno ID:{id_alumno}. ID de Boleta: {id_nueva_boleta}")
        return id_nueva_boleta

    except psycopg2.Error as e:
        print(f"Error al crear la boleta: {e}")
        if conexion:
            conexion.rollback()
        return None
    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()




def obtener_notas_finales_alumno(id_alumno):

    notas_finales = []
    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        sql = """
            SELECT
                asignatura.Nombre,
                detalle.Nota_Final
            FROM
                Boleta_Detalle AS detalle
            JOIN
                Boleta AS boleta ON detalle.IdBoleta = boleta.IdBoleta
            JOIN
                Asignatura_trabajada AS at ON detalle.IdAsignatura_trabajada = at.IdAsignatura_trabajada
            JOIN
                Asignatura AS asignatura ON at.IdAsignatura = asignatura.IdAsignatura
            WHERE
                boleta.IdAlumno = %s AND detalle.Nota_Final IS NOT NULL
            ORDER BY
                asignatura.Nombre;
        """

        cursor.execute(sql, (id_alumno,))
        notas_finales = cursor.fetchall()
        return notas_finales

    except psycopg2.Error as e:
        print(f"Error al consultar las notas finales: {e}")
        return None  

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()




def actualizar_boleta_con_promedio_final(id_boleta, promedio_final):

    try:
        promedio_final = float(promedio_final)
        if not (0 <= promedio_final <= 20):
            print("Error: El promedio final no es valido.")
            return
    except ValueError:
        print("Error: El promedio final debe ser un valor numerico.")
        return
    conexion = None

    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        sql = "UPDATE Boleta SET Promedio_Final_General = %s WHERE IdBoleta = %s"

        cursor.execute(sql, (promedio_final, id_boleta))

        conexion.commit()

        if cursor.rowcount > 0:
            print(f"Promedio general de la boleta ID:{id_boleta} actualizado a {promedio_final:.2f} con exito.")
        else:
            print(f" No se encontro la boleta con ID:{id_boleta}. No se realizaron cambios.")

    except psycopg2.Error as e:
        print(f"Error al actualizar la boleta: {e}")
        if conexion:
            conexion.rollback()
    finally:
        if conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()

def obtener_promedio_final_alumno(id_alumno):

    try:
        conexion = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conexion.cursor()

        anio_actual = datetime.date.today().year

        sql = """
            SELECT Promedio_Final_General
            FROM Boleta
            WHERE IdAlumno = %s AND Anio = %s;
        """

        cursor.execute(sql, (id_alumno, anio_actual))
        
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]
        else:
            return None

    except psycopg2.Error as e:
        print(f"Error al consultar el promedio final: {e}")
        return None 

    finally:
        if 'conexion' in locals() and conexion and getattr(conexion, 'closed', 1) == 0:
            cursor.close()
            conexion.close()

##registrar_grado("Primer Grado", "Primaria", 2025)

##registrar_profesor("Ana", "Gomez", "12345678", "ana.g@mail.com", "profepass", "987654321")
#registrar_profesor("Profesor2", "Test", "12445678", "profesor2@mail.com", "profepass2", "987644321")
#registrar_profesor("Profesor3", "Test", "12445688", "profesor3@mail.com", "profepass3", "987644311")

##registrar_padre("Luis", "Solano", "87654321", "999888777")

#registrar_grado_trabajado("Sección A", 1, 1)

#registrar_asignatura("Matemáticas", "Aritmética", 10, 1)
#registrar_asignatura("Comunicacion", "Literatura", 10, 1)
#registrar_asignatura("Matematica", "Geometria", 10, 1)

#registrar_asignatura_trabajada(1, 1, 1)
#registrar_asignatura_trabajada(1, 2, 2)
#registrar_asignatura_trabajada(1, 3, 3)

##asignar_tutor_a_salon(1, 1)

#registrar_alumno(12345, "Alumno", "Test1", 10, "78945612", 1, 1)
#registrar_alumno(12345, "Alumno", "Test2", 10, "78945712", 1, 1)


"""registrar_nota_simple(
    id_alumno=1,
    id_asignatura_trabajada=1,
    calificacion=17.5,
    nombre_nota="Nota1",
    bimestre=1
)
registrar_nota_simple(
    id_alumno=1,
    id_asignatura_trabajada=2,
    calificacion=17.4,
    nombre_nota="Nota2",
    bimestre=1
)
registrar_nota_simple(
    id_alumno=1,
    id_asignatura_trabajada=3,
    calificacion=17.3,
    nombre_nota="Nota3",
    bimestre=1
)
registrar_nota_simple(
    id_alumno=1,
    id_asignatura_trabajada=1,
    calificacion=17.5,
    nombre_nota="Nota8",
    bimestre=1
)
registrar_nota_simple(
    id_alumno=1,
    id_asignatura_trabajada=2,
    calificacion=17.5,
    nombre_nota="Nota9",
    bimestre=1
)
registrar_nota_simple(
    id_alumno=1,
    id_asignatura_trabajada=3,
    calificacion=17.5,
    nombre_nota="Nota10",
    bimestre=1
)
registrar_nota_simple(
    id_alumno=1,
    id_asignatura_trabajada=1,
    calificacion=17.3,
    nombre_nota="Nota4",
    bimestre=2
)
registrar_nota_simple(
    id_alumno=1,
    id_asignatura_trabajada=2,
    calificacion=17.2,
    nombre_nota="Nota5",
    bimestre=2
)
registrar_nota_simple(
    id_alumno=1,
    id_asignatura_trabajada=3,
    calificacion=17.2,
    nombre_nota="Nota6",
    bimestre=2
)
registrar_nota_simple(
    id_alumno=2,
    id_asignatura_trabajada=1,
    calificacion=17.4,
    nombre_nota="Nota1",
    bimestre=1
)
registrar_nota_simple(
    id_alumno=2,
    id_asignatura_trabajada=2,
    calificacion=10.5,
    nombre_nota="Nota2",
    bimestre=1
)
registrar_nota_simple(
    id_alumno=2,
    id_asignatura_trabajada=3,
    calificacion=16.4,
    nombre_nota="Nota2",
    bimestre=1
)"""

#id_de_la_boleta = crear_boleta_vacia(1)
#id_de_la_boleta = crear_boleta_vacia(2)

"""actualizar_detalle_boleta(
    id_boleta=1,
    id_asignatura_trabajada=1,
    bimestre=1,
    promedio_bimestral=18
)
actualizar_detalle_boleta(
    id_boleta=1,
    id_asignatura_trabajada=2,
    bimestre=1,
    promedio_bimestral=16
)
actualizar_detalle_boleta(
    id_boleta=1,
    id_asignatura_trabajada=3,
    bimestre=1,
    promedio_bimestral=14
)
actualizar_detalle_boleta(
    id_boleta=1,
    id_asignatura_trabajada=2,
    bimestre=2,
    promedio_bimestral=14
)"""

##actualizar_boleta_con_promedio_final(1,16)


"""notas_asignatura1_bimestre1=obtener_notas_de_bimestre(1,1,1)
notas_asignatura2_bimestre1=obtener_notas_de_bimestre(1,2,1)
notas_asignatura3_bimestre1=obtener_notas_de_bimestre(1,3,1)
print("Notas del estudiante1 del bimestre 1:")
print(notas_asignatura1_bimestre1)
print(notas_asignatura2_bimestre1)
print(notas_asignatura3_bimestre1)"""

"""notasfinales=obtener_notas_finales_alumno(1)
print("Notas finales del estudiante1:")
print(notasfinales)"""

notafinal = obtener_promedio_final_alumno(1)
print("Promedio final del estudiante1:")
print(notafinal)