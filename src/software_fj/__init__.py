"""API pública del sistema de Software FJ."""

from .excepciones import (
    ErrorAplicacion,
    ErrorCalculoInconsistente,
    ErrorDuplicado,
    ErrorNoEncontrado,
    ErrorOperacionNoPermitida,
    ErrorReservaInvalida,
    ErrorServicioNoDisponible,
    ErrorValidacion,
)
from .gestor import GestorReservas
from .modelos import (
    Cliente,
    EstadoReserva,
    Reserva,
    Servicio,
    ServicioAlquilerEquipo,
    ServicioAsesoria,
    ServicioSala,
)

__all__ = [
    "Cliente",
    "ErrorAplicacion",
    "ErrorCalculoInconsistente",
    "ErrorDuplicado",
    "ErrorNoEncontrado",
    "ErrorOperacionNoPermitida",
    "ErrorReservaInvalida",
    "ErrorServicioNoDisponible",
    "ErrorValidacion",
    "EstadoReserva",
    "GestorReservas",
    "Reserva",
    "Servicio",
    "ServicioAlquilerEquipo",
    "ServicioAsesoria",
    "ServicioSala",
]
