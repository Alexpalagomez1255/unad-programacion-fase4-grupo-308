"""Excepciones de dominio controladas por la aplicación."""


class ErrorAplicacion(Exception):
    """Clase base para errores previstos que no deben detener el sistema."""


class ErrorValidacion(ErrorAplicacion):
    """Un dato de entrada no cumple las reglas del dominio."""


class ErrorDuplicado(ErrorAplicacion):
    """Ya existe una entidad con el mismo código."""


class ErrorNoEncontrado(ErrorAplicacion):
    """No se encontró la entidad solicitada."""


class ErrorServicioNoDisponible(ErrorAplicacion):
    """El servicio existe, pero no admite reservas en este momento."""


class ErrorReservaInvalida(ErrorAplicacion):
    """Los datos de una reserva son incompatibles con el servicio."""


class ErrorOperacionNoPermitida(ErrorAplicacion):
    """El estado actual no permite ejecutar la operación solicitada."""


class ErrorCalculoInconsistente(ErrorAplicacion):
    """El cálculo produjo un importe inválido o inesperado."""
