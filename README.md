# Sistema Integral de Gestión de Clientes Servicios y Reservas

Proyecto colaborativo de la Fase 4 del curso Programación 213023 de la
Universidad Nacional Abierta y a Distancia. Grupo 308.

## Aporte individual de Alejandro Palacios

Este repositorio contiene el aporte individual inicial de **Alejandro
Palacios** al proyecto del grupo 308. El trabajo incluye la arquitectura del
dominio, las excepciones personalizadas, el registro de eventos y errores, las
simulaciones válidas e inválidas, las pruebas automatizadas, las evidencias y
el informe individual.

Repositorio del proyecto:
[Alexpalagomez1255/unad-programacion-fase4-grupo-308](https://github.com/Alexpalagomez1255/unad-programacion-fase4-grupo-308)
El informe grupal se preparará posteriormente, cuando se integren y validen
los aportes de los demás integrantes.

La aplicación implementa el Ejercicio 1 del Anexo 3 para la empresa Software
FJ. Gestiona clientes, servicios y reservas en memoria, sin bases de datos. Los
únicos archivos persistentes son el log de eventos y la evidencia JSON de las
simulaciones.

## Funcionalidades

- Registro y búsqueda de clientes con encapsulación y validaciones.
- Clase abstracta `Servicio` y tres implementaciones polimórficas:
  - reservas de salas;
  - alquiler de equipos;
  - asesorías especializadas.
- Creación, confirmación, procesamiento y cancelación de reservas.
- Cálculo de costos con duración, impuestos, descuentos y parámetros
  opcionales específicos de cada servicio.
- Excepciones personalizadas y encadenamiento con `raise ... from ...`.
- Uso de `try/except`, `try/except/else` y `try/finally`.
- Logs rotativos para eventos correctos, rechazos y errores.
- Quince simulaciones válidas e inválidas que continúan después de cada error.
- Pruebas automatizadas con la biblioteca estándar `unittest`.

## Requisitos

- Python 3.11 o posterior.
- No se requieren paquetes externos.

## Ejecución

Desde la raíz del repositorio:

```bash
python3 simulaciones.py
python3 -m unittest discover -s tests -v
```

La primera orden genera:

- `logs/software_fj.log`, con los eventos y errores de la ejecución;
- `evidencias/resultados_simulaciones.json`, con el resultado de los quince
  casos.

## Estructura

```text
src/software_fj/           Código del dominio y configuración de logs
tests/                     Pruebas automatizadas
evidencias/                Resultados reproducibles de las simulaciones
output/pdf/                Informe del aporte individual
simulaciones.py            Ejecutor secuencial de casos válidos e inválidos
```

## Trabajo colaborativo

Se recomienda que cada integrante cree una rama con el formato
`nombre/tarea`, por ejemplo `alejandro/excepciones`. Cada cambio debe incluir
commits descriptivos y llegar a `master` mediante un pull request revisado por
otro integrante. Los issues pueden utilizarse para distribuir clientes,
servicios, reservas, pruebas y documentación.

Repositorio del proyecto:
[Alexpalagomez1255/unad-programacion-fase4-grupo-308](https://github.com/Alexpalagomez1255/unad-programacion-fase4-grupo-308)
