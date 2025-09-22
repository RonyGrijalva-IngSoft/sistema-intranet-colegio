# Sistema Intranet Colegio

## Descripción del Proyecto
Sistema web para centralizar y automatizar la información académica del colegio "IEP Cristo Redentor".  
El objetivo principal es facilitar la gestión académica y reducir el trabajo manual de docentes y tutores, brindando a la dirección un control seguro y ágil de la información.

### Funcionalidades Clave
- Gestión de usuarios con roles diferenciados (Directora, Tutor, Polidocente, Alumno).
- Registro y consolidación de notas, incluyendo cálculo automático de promedios y conversión de calificaciones numéricas a letras.
- Generación de libretas bimestrales en PDF, con plantillas para inicial, primaria y secundaria.
- Acceso multi-dispositivo, permitiendo el uso desde computadoras y dispositivos móviles.

## Decisiones de Diseño
- **Base de Datos: MySQL**
  - **Comunidad y soporte:** Al ser uno de los SGBD más usados a nivel mundial, MySQL cuenta con amplia documentación, foros y herramientas de administración.
  - **Compatibilidad con el modelo de datos diseñado:** El proyecto define un modelo relacional con múltiples tablas interconectadas (Alumno, Profesor, Sección, Curso, Nota, Asistencia, etc.). MySQL, al ser un SGBD relacional ampliamente utilizado, soporta perfectamente el uso de claves primarias, foráneas, restricciones de integridad y consultas SQL complejas.
  - **Rendimiento y concurrencia:** Entre los requerimientos no funcionales se especifica la necesidad de gestionar múltiples usuarios simultáneamente (directora, tutores, polidocentes y alumnos) sin retrasos en operaciones como registro de asistencia o notas. MySQL está optimizado para operaciones de lectura y/o escritura intensivas y soporta motores de almacenamiento que manejan transacciones y concurrencia de forma eficiente.
  - **Seguridad de la información académica:** El sistema debe garantizar autenticación segura y confidencialidad de los datos personales de alumnos y docentes. MySQL permite implementar usuarios con roles diferenciados, lo cual se ajusta al modelo de permisos planteado (directora, tutor, polidocente, alumno). Además, admite encriptación y copias de seguridad periódicas.
  - **Escalabilidad y futuro crecimiento:** El proyecto contempla la escalabilidad como un requisito clave, ya que en fases futuras se integrará acceso web para alumnos y padres. MySQL es altamente escalable y puede adaptarse a un mayor volumen de usuarios y transacciones, soportando despliegues locales y en la nube.

## Lenguaje Seleccionado: Python y Javascript
Justificación:
- **Curva de aprendizaje:** Python es conocido por su sintaxis clara y sencilla, mientras que JavaScript es el estándar de la web, ambos son fáciles de aprender para el equipo.
- **Soporte de comunidad:** Ambos cuentan con comunidades enormes, abundante documentación y librerías, lo que facilita resolver problemas y encontrar ejemplos.
- **Compatibilidad con los requisitos:** Se integran bien con MySQL, funcionan en distintos entornos (local, nube) y permiten cubrir tanto el backend (Python) como el frontend (JavaScript) del sistema de intranet.
- **Facilidad de pruebas y despliegue:** Hay herramientas nativas y librerías (pytest, Jest, etc.) que facilitan pruebas automatizadas, y se despliegan sin problemas en diferentes servicios.

## Frameworks: Django y React.js
Justificación:
- **Curva de aprendizaje:** Django trae muchos componentes listos (autenticación, ORM, administración), lo que reduce la complejidad, mientras que React tiene una estructura por componentes clara y bien documentada.
- **Soporte de comunidad:** Ambos frameworks tienen ecosistemas maduros, documentación extensa y foros activos.
- **Compatibilidad con los requisitos:** Django facilita la gestión de usuarios, generación de PDFs y conexión con MySQL, y React permite crear interfaces dinámicas y adaptables a dispositivos móviles y de escritorio.
- **Facilidad de pruebas y despliegue:** Django integra un framework de testing y se despliega fácilmente en entornos cloud. React puede hospedarse en plataformas de despliegue continuo (CI/CD) que se integran bien con GitHub, permitiendo que las pruebas se ejecuten automáticamente y que el sistema se despliegue de forma ágil y segura en la nube.

## Arquitectura de Software

El sistema se implementa siguiendo una **arquitectura de 4 capas**, que permite una separación clara de responsabilidades y facilita el mantenimiento, escalabilidad y evolución del proyecto. Las capas definidas son:

- **Capa de Presentación**: Encargada de la interfaz gráfica y la interacción con el usuario. Se desarrolla con React.js, permitiendo una experiencia dinámica y adaptable a distintos dispositivos.
- **Capa de Lógica de Negocio**: Contiene las reglas del sistema, procesamiento de datos y validaciones. Se implementa con Django, facilitando la organización de funcionalidades por módulos.
- **Capa de Acceso a Datos**: Intermedia entre la lógica de negocio y la base de datos, gestionando consultas, inserciones y actualizaciones mediante el ORM de Django.
- **Capa de Persistencia**: Responsable del almacenamiento físico de la información. Se utiliza MySQL como sistema gestor de base de datos relacional, garantizando integridad y eficiencia.

Esta arquitectura fue seleccionada por su claridad estructural, compatibilidad con el stack tecnológico elegido, y su capacidad para distribuir responsabilidades entre los miembros del equipo. Además, permite incorporar futuras funcionalidades como autenticación avanzada, control de acceso por roles y despliegue en contenedores sin comprometer la estabilidad del sistema.
