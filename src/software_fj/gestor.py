"""Gestor en memoria de clientes, servicios y reservas."""

from __future__ import annotations

from typing import TypeVar

from .configuracion_logs import logger
from .excepciones import ErrorAplicacion, ErrorDuplicado, ErrorNoEncontrado
from .modelos import Cliente, Reserva, Servicio


T = TypeVar("T", Cliente, Servicio, Reserva)


class GestorReservas:
    """Mantiene listas internas sin utilizar un motor de base de datos."""

    def __init__(self) -> None:
        self._clientes: dict[str, Cliente] = {}
        self._servicios: dict[str, Servicio] = {}
        self._reservas: dict[str, Reserva] = {}

    @staticmethod
    def _registrar(coleccion: dict[str, T], entidad: T, tipo: str) -> None:
        try:
            if entidad.codigo in coleccion:
                raise ErrorDuplicado(
                    f"Ya existe {tipo} con código {entidad.codigo}."
                )
            coleccion[entidad.codigo] = entidad
        except ErrorAplicacion:
            logger.warning(
                "Registro rechazado | tipo=%s | codigo=%s",
                tipo,
                entidad.codigo,
                exc_info=True,
            )
            raise
        else:
            logger.info(
                "Entidad registrada | tipo=%s | codigo=%s", tipo, entidad.codigo
            )
        finally:
            logger.debug(
                "Intento de registro finalizado | tipo=%s | total=%d",
                tipo,
                len(coleccion),
            )

    @staticmethod
    def _buscar(coleccion: dict[str, T], codigo: str, tipo: str) -> T:
        codigo_normalizado = str(codigo).strip().upper()
        try:
            return coleccion[codigo_normalizado]
        except KeyError as exc:
            logger.warning(
                "Entidad no encontrada | tipo=%s | codigo=%s",
                tipo,
                codigo_normalizado,
            )
            raise ErrorNoEncontrado(
                f"No existe {tipo} con código {codigo_normalizado}."
            ) from exc

    def registrar_cliente(self, cliente: Cliente) -> None:
        self._registrar(self._clientes, cliente, "un cliente")

    def registrar_servicio(self, servicio: Servicio) -> None:
        self._registrar(self._servicios, servicio, "un servicio")

    def buscar_cliente(self, codigo: str) -> Cliente:
        return self._buscar(self._clientes, codigo, "un cliente")

    def buscar_servicio(self, codigo: str) -> Servicio:
        return self._buscar(self._servicios, codigo, "un servicio")

    def buscar_reserva(self, codigo: str) -> Reserva:
        return self._buscar(self._reservas, codigo, "una reserva")

    def crear_reserva(
        self,
        codigo: str,
        codigo_cliente: str,
        codigo_servicio: str,
        duracion,
        *,
        impuesto=0,
        descuento=0,
        **parametros,
    ) -> Reserva:
        try:
            cliente = self.buscar_cliente(codigo_cliente)
            servicio = self.buscar_servicio(codigo_servicio)
            reserva = Reserva(
                codigo,
                cliente,
                servicio,
                duracion,
                impuesto=impuesto,
                descuento=descuento,
                **parametros,
            )
            self._registrar(self._reservas, reserva, "una reserva")
        except ErrorAplicacion:
            logger.error(
                "Creación de reserva rechazada | reserva=%s | cliente=%s | servicio=%s",
                codigo,
                codigo_cliente,
                codigo_servicio,
                exc_info=True,
            )
            raise
        else:
            logger.info(
                "Reserva creada | reserva=%s | total=%s", reserva.codigo, reserva.total
            )
            return reserva
        finally:
            logger.debug(
                "Creación de reserva finalizada | codigo=%s | total_reservas=%d",
                codigo,
                len(self._reservas),
            )

    def listar_clientes(self) -> tuple[Cliente, ...]:
        return tuple(self._clientes.values())

    def listar_servicios(self) -> tuple[Servicio, ...]:
        return tuple(self._servicios.values())

    def listar_reservas(self) -> tuple[Reserva, ...]:
        return tuple(self._reservas.values())
