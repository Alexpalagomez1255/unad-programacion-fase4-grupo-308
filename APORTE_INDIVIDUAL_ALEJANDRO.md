# Aporte individual — Alejandro Palacios

**Actividad:** Fase 4 — Componente práctico: Prácticas simuladas

**Curso:** Programación 213023

**Grupo:** 308

**Fecha:** noviembre de 2026

## Repositorio

[https://github.com/Alexpalagomez1255/unad-programacion-fase4-grupo-308](https://github.com/Alexpalagomez1255/unad-programacion-fase4-grupo-308)

## Aportes realizados

- Diseño de la arquitectura orientada a objetos para clientes, servicios y
  reservas.
- Implementación de la clase abstracta `Servicio` y de los servicios de salas,
  alquiler de equipos y asesorías especializadas.
- Implementación de excepciones personalizadas, validaciones y encadenamiento
  de excepciones.
- Configuración del registro de eventos, advertencias, errores y trazas en
  archivos de log rotativos.
- Implementación de quince simulaciones válidas e inválidas que continúan su
  ejecución después de los errores controlados.
- Creación de treinta pruebas automatizadas con `unittest`.
- Generación de evidencia JSON reproducible y documentación de uso.
- Preparación del informe PDF correspondiente a este aporte individual.

## Verificación

- Simulaciones aprobadas: **15 de 15**.
- Pruebas automatizadas aprobadas: **30 de 30**.
- Niveles comprobados en el log: `INFO`, `WARNING` y `ERROR`.

Desde la raíz del repositorio se puede repetir la verificación con:

```bash
python3 simulaciones.py
python3 -m unittest discover -s tests -v
```

## Integración grupal

Este aporte deja una base funcional para el proyecto. El informe grupal se
preparará posteriormente, después de incorporar y validar los aportes de los
demás integrantes.
