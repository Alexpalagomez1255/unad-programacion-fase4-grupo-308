"""Entidades y servicios orientados a objetos del sistema Software FJ."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
import re
from typing import Any

from .configuracion_logs import logger
from .excepciones import (
    ErrorCalculoInconsistente,
    ErrorOperacionNoPermitida,
    ErrorReservaInvalida,
    ErrorServicioNoDisponible,
    ErrorValidacion,
)


CENTAVOS = Decimal("0.01")
PATRON_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def texto_requerido(valor: Any, campo: str) -> str:
    """Normaliza un texto obligatorio."""

    normalizado = str(valor).strip()
    if not normalizado:
        raise ErrorValidacion(f"{campo} es obligatorio.")
    return normalizado


def decimal_no_negativo(
    valor: Any,
    campo: str,
    *,
    permitir_cero: bool = True,
) -> Decimal:
    """Convierte a Decimal y encadena el error original de conversión."""

    try:
        numero = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError, AttributeError) as exc:
        logger.warning("Dato numérico inválido | campo=%s | valor=%r", campo, valor)
        raise ErrorValidacion(f"{campo} debe ser un número válido.") from exc
    else:
        if not numero.is_finite():
            raise ErrorValidacion(f"{campo} debe ser un número finito.")
        if numero < 0 or (numero == 0 and not permitir_cero):
            condicion = "mayor que cero" if not permitir_cero else "cero o mayor"
            raise ErrorValidacion(f"{campo} debe ser {condicion}.")
        return numero.quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    finally:
        logger.debug("Validación numérica finalizada | campo=%s", campo)


def entero_positivo(valor: Any, campo: str) -> int:
    """Valida enteros positivos y evita aceptar valores booleanos."""

    if isinstance(valor, bool):
        raise ErrorValidacion(f"{campo} debe ser un número entero positivo.")
    try:
        numero = int(str(valor).strip())
    except (TypeError, ValueError, AttributeError) as exc:
        raise ErrorValidacion(
            f"{campo} debe ser un número entero positivo."
        ) from exc
    if numero <= 0 or str(valor).strip() not in (str(numero), f"+{numero}"):
        raise ErrorValidacion(f"{campo} debe ser un número entero positivo.")
    return numero


def porcentaje(valor: Any, campo: str) -> Decimal:
    """Valida un porcentaje entre cero y cien."""

    numero = decimal_no_negativo(valor, campo)
    if numero > Decimal("100"):
        raise ErrorValidacion(f"{campo} no puede superar 100 por ciento.")
    return numero


class EntidadSistema(ABC):
    """Clase abstracta para las entidades identificables del sistema."""

    def __init__(self, codigo: str) -> None:
        self._codigo = texto_requerido(codigo, "El código").upper()

    @property
    def codigo(self) -> str:
        return self._codigo

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible de la entidad."""


class Cliente(EntidadSistema):
    """Cliente con datos personales encapsulados y validados."""

    def __init__(self, codigo: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(codigo)
        self._nombre = texto_requerido(nombre, "El nombre del cliente")
        correo_normalizado = texto_requerido(correo, "El correo").lower()
        if not PATRON_CORREO.fullmatch(correo_normalizado):
            raise ErrorValidacion("El correo del cliente no tiene un formato válido.")
        self._correo = correo_normalizado
        telefono_normalizado = re.sub(r"[\s()+-]", "", str(telefono))
        if not telefono_normalizado.isdigit() or not 7 <= len(telefono_normalizado) <= 15:
            raise ErrorValidacion("El teléfono debe contener entre 7 y 15 dígitos.")
        self._telefono = telefono_normalizado

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def correo(self) -> str:
        return self._correo

    @property
    def telefono(self) -> str:
        return self._telefono

    def describir(self) -> str:
        return f"Cliente {self.codigo}: {self.nombre} ({self.correo})"


class Servicio(EntidadSistema, ABC):
    """Contrato polimórfico de todos los servicios ofrecidos por Software FJ."""

    def __init__(self, codigo: str, nombre: str, disponible: bool = True) -> None:
        super().__init__(codigo)
        self._nombre = texto_requerido(nombre, "El nombre del servicio")
        if not isinstance(disponible, bool):
            raise ErrorValidacion("La disponibilidad debe ser verdadera o falsa.")
        self._disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    def cambiar_disponibilidad(self, disponible: bool) -> None:
        if not isinstance(disponible, bool):
            raise ErrorValidacion("La disponibilidad debe ser verdadera o falsa.")
        self._disponible = disponible
        logger.info(
            "Disponibilidad modificada | servicio=%s | disponible=%s",
            self.codigo,
            disponible,
        )

    @abstractmethod
    def validar_parametros(self, duracion: Decimal, **parametros: Any) -> None:
        """Valida duración y parámetros particulares del servicio."""

    @abstractmethod
    def _calcular_subtotal(self, duracion: Decimal, **parametros: Any) -> Decimal:
        """Calcula el subtotal específico del servicio concreto."""

    def calcular_costo(
        self,
        duracion: Any,
        impuesto: Any = 0,
        descuento: Any = 0,
        **parametros: Any,
    ) -> Decimal:
        """Simula sobrecarga con impuestos, descuentos y parámetros opcionales."""

        if not self.disponible:
            raise ErrorServicioNoDisponible(
                f"El servicio {self.codigo} no está disponible."
            )
        duracion_decimal = decimal_no_negativo(
            duracion, "La duración", permitir_cero=False
        )
        impuesto_decimal = porcentaje(impuesto, "El impuesto")
        descuento_decimal = porcentaje(descuento, "El descuento")
        self.validar_parametros(duracion_decimal, **parametros)
        subtotal = self._calcular_subtotal(duracion_decimal, **parametros)
        if not subtotal.is_finite() or subtotal <= 0:
            raise ErrorCalculoInconsistente(
                f"El servicio {self.codigo} produjo un subtotal inválido."
            )
        con_descuento = subtotal * (Decimal("100") - descuento_decimal) / Decimal("100")
        total = con_descuento * (Decimal("100") + impuesto_decimal) / Decimal("100")
        return total.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


class ServicioSala(Servicio):
    """Reserva de sala cobrada por hora y limitada por capacidad."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        precio_hora: Any,
        capacidad: Any,
        maximo_horas: Any = 8,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, disponible)
        self.precio_hora = decimal_no_negativo(
            precio_hora, "El precio por hora", permitir_cero=False
        )
        self.capacidad = entero_positivo(capacidad, "La capacidad")
        self.maximo_horas = decimal_no_negativo(
            maximo_horas, "El máximo de horas", permitir_cero=False
        )

    def validar_parametros(self, duracion: Decimal, **parametros: Any) -> None:
        participantes = entero_positivo(
            parametros.get("participantes"), "Los participantes"
        )
        if duracion > self.maximo_horas:
            raise ErrorReservaInvalida(
                f"La sala admite máximo {self.maximo_horas} horas."
            )
        if participantes > self.capacidad:
            raise ErrorReservaInvalida(
                f"La sala admite máximo {self.capacidad} participantes."
            )

    def _calcular_subtotal(self, duracion: Decimal, **parametros: Any) -> Decimal:
        return (self.precio_hora * duracion).quantize(CENTAVOS)

    def describir(self) -> str:
        return (
            f"Sala {self.nombre}: capacidad {self.capacidad}, "
            f"COP {self.precio_hora} por hora"
        )


class ServicioAlquilerEquipo(Servicio):
    """Alquiler de equipos cobrado por día, unidad y depósito."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        precio_dia: Any,
        unidades_disponibles: Any,
        deposito_porcentaje: Any = 10,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, disponible)
        self.precio_dia = decimal_no_negativo(
            precio_dia, "El precio por día", permitir_cero=False
        )
        self.unidades_disponibles = entero_positivo(
            unidades_disponibles, "Las unidades disponibles"
        )
        self.deposito_porcentaje = porcentaje(
            deposito_porcentaje, "El porcentaje de depósito"
        )

    def validar_parametros(self, duracion: Decimal, **parametros: Any) -> None:
        cantidad = entero_positivo(parametros.get("cantidad"), "La cantidad")
        if cantidad > self.unidades_disponibles:
            raise ErrorReservaInvalida(
                f"Solo hay {self.unidades_disponibles} unidades disponibles."
            )
        if duracion != duracion.to_integral_value():
            raise ErrorReservaInvalida("El alquiler debe expresarse en días completos.")

    def _calcular_subtotal(self, duracion: Decimal, **parametros: Any) -> Decimal:
        cantidad = Decimal(entero_positivo(parametros.get("cantidad"), "La cantidad"))
        alquiler = self.precio_dia * duracion * cantidad
        deposito = alquiler * self.deposito_porcentaje / Decimal("100")
        return (alquiler + deposito).quantize(CENTAVOS)

    def describir(self) -> str:
        return (
            f"Equipo {self.nombre}: {self.unidades_disponibles} unidades, "
            f"COP {self.precio_dia} por día"
        )


class ServicioAsesoria(Servicio):
    """Asesoría especializada por hora, presencial o virtual."""

    MODALIDADES = {"presencial", "virtual"}

    def __init__(
        self,
        codigo: str,
        nombre: str,
        especialista: str,
        precio_hora: Any,
        minimo_horas: Any = 1,
        maximo_horas: Any = 6,
        disponible: bool = True,
    ) -> None:
        super().__init__(codigo, nombre, disponible)
        self.especialista = texto_requerido(especialista, "El especialista")
        self.precio_hora = decimal_no_negativo(
            precio_hora, "El precio por hora", permitir_cero=False
        )
        self.minimo_horas = decimal_no_negativo(
            minimo_horas, "El mínimo de horas", permitir_cero=False
        )
        self.maximo_horas = decimal_no_negativo(
            maximo_horas, "El máximo de horas", permitir_cero=False
        )
        if self.minimo_horas > self.maximo_horas:
            raise ErrorValidacion(
                "El mínimo de horas no puede superar el máximo de horas."
            )

    def validar_parametros(self, duracion: Decimal, **parametros: Any) -> None:
        modalidad = texto_requerido(
            parametros.get("modalidad", ""), "La modalidad"
        ).lower()
        if modalidad not in self.MODALIDADES:
            raise ErrorReservaInvalida(
                "La modalidad debe ser presencial o virtual."
            )
        if not self.minimo_horas <= duracion <= self.maximo_horas:
            raise ErrorReservaInvalida(
                f"La asesoría debe durar entre {self.minimo_horas} y "
                f"{self.maximo_horas} horas."
            )

    def _calcular_subtotal(self, duracion: Decimal, **parametros: Any) -> Decimal:
        return (self.precio_hora * duracion).quantize(CENTAVOS)

    def describir(self) -> str:
        return (
            f"Asesoría {self.nombre} con {self.especialista}: "
            f"COP {self.precio_hora} por hora"
        )


class EstadoReserva(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    PROCESADA = "procesada"
    CANCELADA = "cancelada"


class Reserva(EntidadSistema):
    """Integra cliente, servicio, duración, costo y ciclo de vida."""

    def __init__(
        self,
        codigo: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: Any,
        *,
        impuesto: Any = 0,
        descuento: Any = 0,
        **parametros: Any,
    ) -> None:
        super().__init__(codigo)
        if not isinstance(cliente, Cliente):
            raise ErrorValidacion("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ErrorValidacion("La reserva requiere un servicio válido.")
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = decimal_no_negativo(
            duracion, "La duración", permitir_cero=False
        )
        self.impuesto = porcentaje(impuesto, "El impuesto")
        self.descuento = porcentaje(descuento, "El descuento")
        self.parametros = dict(parametros)
        # La validación y el cálculo previos impiden almacenar reservas imposibles.
        self.total = servicio.calcular_costo(
            self.duracion,
            self.impuesto,
            self.descuento,
            **self.parametros,
        )
        self.estado = EstadoReserva.PENDIENTE

    def confirmar(self) -> Decimal:
        try:
            if self.estado is not EstadoReserva.PENDIENTE:
                raise ErrorOperacionNoPermitida(
                    "Solo una reserva pendiente puede confirmarse."
                )
            if not self.servicio.disponible:
                raise ErrorServicioNoDisponible(
                    f"El servicio {self.servicio.codigo} dejó de estar disponible."
                )
            self.total = self.servicio.calcular_costo(
                self.duracion,
                self.impuesto,
                self.descuento,
                **self.parametros,
            )
            self.estado = EstadoReserva.CONFIRMADA
        except (ErrorReservaInvalida, ErrorOperacionNoPermitida, ErrorServicioNoDisponible):
            logger.error("No fue posible confirmar la reserva %s", self.codigo, exc_info=True)
            raise
        else:
            logger.info(
                "Reserva confirmada | reserva=%s | cliente=%s | total=%s",
                self.codigo,
                self.cliente.codigo,
                self.total,
            )
            return self.total
        finally:
            logger.debug(
                "Intento de confirmación finalizado | reserva=%s | estado=%s",
                self.codigo,
                self.estado.value,
            )

    def procesar(self) -> None:
        if self.estado is not EstadoReserva.CONFIRMADA:
            raise ErrorOperacionNoPermitida(
                "Solo una reserva confirmada puede procesarse."
            )
        self.estado = EstadoReserva.PROCESADA
        logger.info("Reserva procesada | reserva=%s", self.codigo)

    def cancelar(self) -> None:
        if self.estado in (EstadoReserva.PROCESADA, EstadoReserva.CANCELADA):
            raise ErrorOperacionNoPermitida(
                f"No se puede cancelar una reserva {self.estado.value}."
            )
        self.estado = EstadoReserva.CANCELADA
        logger.info("Reserva cancelada | reserva=%s", self.codigo)

    def describir(self) -> str:
        return (
            f"Reserva {self.codigo}: {self.cliente.nombre}, {self.servicio.nombre}, "
            f"estado {self.estado.value}, total COP {self.total}"
        )
