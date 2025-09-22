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
  - f 
- **Arquitectura de Software: Microservicios**

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
- **Facilidad de pruebas y despliegue:** Django integra un framework de testing y se despliega fácilmente en entornos cloud. React puede hospedarse en plataformas de despliegue continuo (CI/CD) que se integran bien con GitHub.
