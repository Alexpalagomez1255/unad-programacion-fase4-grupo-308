"""Ejecuta operaciones válidas e inválidas sin interrumpir la aplicación."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Callable


BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "src"))

from software_fj import (  # noqa: E402
    Cliente,
    ErrorAplicacion,
    ErrorDuplicado,
    ErrorOperacionNoPermitida,
    ErrorReservaInvalida,
    ErrorServicioNoDisponible,
    ErrorValidacion,
    GestorReservas,
    ServicioAlquilerEquipo,
    ServicioAsesoria,
    ServicioSala,
)
from software_fj.configuracion_logs import (  # noqa: E402
    cerrar_logging,
    configurar_logging,
    logger,
)


@dataclass(frozen=True)
class ResultadoSimulacion:
    numero: int
    nombre: str
    tipo: str
    aprobado: bool
    detalle: str


def ejecutar_valida(
    numero: int,
    nombre: str,
    accion: Callable[[], object],
) -> ResultadoSimulacion:
    try:
        resultado = accion()
    except Exception as exc:
        logger.exception("Simulación válida falló | caso=%s", nombre)
        return ResultadoSimulacion(numero, nombre, "válida", False, str(exc))
    else:
        detalle = resultado.describir() if hasattr(resultado, "describir") else str(resultado)
        logger.info("Simulación válida aprobada | caso=%s", nombre)
        return ResultadoSimulacion(numero, nombre, "válida", True, detalle)
    finally:
        logger.debug("Simulación finalizada | caso=%s", nombre)


def ejecutar_invalida(
    numero: int,
    nombre: str,
    error_esperado: type[ErrorAplicacion],
    accion: Callable[[], object],
) -> ResultadoSimulacion:
    try:
        accion()
    except error_esperado as exc:
        logger.info(
            "Simulación inválida controlada | caso=%s | error=%s",
            nombre,
            exc.__class__.__name__,
        )
        return ResultadoSimulacion(
            numero,
            nombre,
            "inválida",
            True,
            f"{exc.__class__.__name__}: {exc}",
        )
    except Exception as exc:
        logger.exception("Excepción distinta a la esperada | caso=%s", nombre)
        return ResultadoSimulacion(
            numero,
            nombre,
            "inválida",
            False,
            f"Se esperaba {error_esperado.__name__}; ocurrió {type(exc).__name__}: {exc}",
        )
    else:
        return ResultadoSimulacion(
            numero,
            nombre,
            "inválida",
            False,
            f"No se produjo {error_esperado.__name__}.",
        )
    finally:
        logger.debug("Simulación finalizada | caso=%s", nombre)


def crear_y_completar_reserva(gestor: GestorReservas, *args, **kwargs):
    reserva = gestor.crear_reserva(*args, **kwargs)
    reserva.confirmar()
    reserva.procesar()
    return reserva


def ejecutar_simulaciones() -> list[ResultadoSimulacion]:
    gestor = GestorReservas()
    resultados: list[ResultadoSimulacion] = []

    resultados.append(
        ejecutar_valida(
            1,
            "Registrar cliente válido",
            lambda: (
                cliente := Cliente("CLI-001", "Ana Torres", "ana@example.com", "3001234567"),
                gestor.registrar_cliente(cliente),
                cliente,
            )[-1],
        )
    )
    resultados.append(
        ejecutar_invalida(
            2,
            "Rechazar cliente con correo inválido",
            ErrorValidacion,
            lambda: Cliente("CLI-002", "Luis", "correo-invalido", "3001234568"),
        )
    )
    resultados.append(
        ejecutar_invalida(
            3,
            "Rechazar cliente duplicado",
            ErrorDuplicado,
            lambda: gestor.registrar_cliente(
                Cliente("cli-001", "Otro nombre", "otro@example.com", "3001234569")
            ),
        )
    )

    sala = ServicioSala("SER-SALA", "Sala Ejecutiva", "85000", 12, 8)
    equipo = ServicioAlquilerEquipo("SER-EQP", "Portátil", "120000", 5, 10)
    asesoria = ServicioAsesoria(
        "SER-ASE", "Arquitectura de software", "Laura Gómez", "150000", 1, 6
    )

    resultados.append(
        ejecutar_valida(
            4,
            "Crear servicio de sala",
            lambda: (gestor.registrar_servicio(sala), sala)[-1],
        )
    )
    resultados.append(
        ejecutar_valida(
            5,
            "Crear servicio de alquiler de equipos",
            lambda: (gestor.registrar_servicio(equipo), equipo)[-1],
        )
    )
    resultados.append(
        ejecutar_invalida(
            6,
            "Rechazar servicio con tarifa negativa",
            ErrorValidacion,
            lambda: ServicioAsesoria(
                "SER-MAL", "Servicio incorrecto", "Especialista", "-1"
            ),
        )
    )
    resultados.append(
        ejecutar_valida(
            7,
            "Crear servicio de asesoría",
            lambda: (gestor.registrar_servicio(asesoria), asesoria)[-1],
        )
    )
    resultados.append(
        ejecutar_valida(
            8,
            "Completar reserva de sala",
            lambda: crear_y_completar_reserva(
                gestor,
                "RES-001",
                "CLI-001",
                "SER-SALA",
                3,
                impuesto=19,
                descuento=5,
                participantes=8,
            ),
        )
    )
    resultados.append(
        ejecutar_invalida(
            9,
            "Rechazar reserva que supera la capacidad de la sala",
            ErrorReservaInvalida,
            lambda: gestor.crear_reserva(
                "RES-002",
                "CLI-001",
                "SER-SALA",
                2,
                participantes=20,
            ),
        )
    )

    equipo.cambiar_disponibilidad(False)
    resultados.append(
        ejecutar_invalida(
            10,
            "Controlar servicio no disponible",
            ErrorServicioNoDisponible,
            lambda: gestor.crear_reserva(
                "RES-003",
                "CLI-001",
                "SER-EQP",
                2,
                cantidad=1,
            ),
        )
    )
    equipo.cambiar_disponibilidad(True)
    resultados.append(
        ejecutar_valida(
            11,
            "Completar alquiler de equipos",
            lambda: crear_y_completar_reserva(
                gestor,
                "RES-004",
                "CLI-001",
                "SER-EQP",
                2,
                cantidad=2,
            ),
        )
    )
    resultados.append(
        ejecutar_invalida(
            12,
            "Rechazar alquiler por falta de unidades",
            ErrorReservaInvalida,
            lambda: gestor.crear_reserva(
                "RES-005",
                "CLI-001",
                "SER-EQP",
                1,
                cantidad=10,
            ),
        )
    )
    resultados.append(
        ejecutar_valida(
            13,
            "Completar asesoría con descuento e impuesto",
            lambda: crear_y_completar_reserva(
                gestor,
                "RES-006",
                "CLI-001",
                "SER-ASE",
                2,
                impuesto=19,
                descuento=10,
                modalidad="virtual",
            ),
        )
    )

    def crear_y_cancelar():
        reserva = gestor.crear_reserva(
            "RES-007",
            "CLI-001",
            "SER-ASE",
            1,
            modalidad="presencial",
        )
        reserva.cancelar()
        return reserva

    reserva_cancelada = None

    def caso_cancelacion():
        nonlocal reserva_cancelada
        reserva_cancelada = crear_y_cancelar()
        return reserva_cancelada

    resultados.append(
        ejecutar_valida(14, "Cancelar una reserva pendiente", caso_cancelacion)
    )
    resultados.append(
        ejecutar_invalida(
            15,
            "Rechazar procesamiento de una reserva cancelada",
            ErrorOperacionNoPermitida,
            lambda: reserva_cancelada.procesar(),
        )
    )

    # Una operación final confirma que los errores no dañaron el gestor.
    if len(gestor.listar_reservas()) != 4:
        resultados.append(
            ResultadoSimulacion(
                16,
                "Verificar continuidad del gestor",
                "válida",
                False,
                f"Se esperaban 4 reservas almacenadas y hay {len(gestor.listar_reservas())}.",
            )
        )
    return resultados


def guardar_resultados(resultados: list[ResultadoSimulacion]) -> Path:
    ruta = BASE_DIR / "evidencias" / "resultados_simulaciones.json"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    contenido = {
        "proyecto": "Sistema Integral de Gestión de Clientes, Servicios y Reservas",
        "generado_en": datetime.now().astimezone().isoformat(timespec="seconds"),
        "total": len(resultados),
        "aprobadas": sum(resultado.aprobado for resultado in resultados),
        "fallidas": sum(not resultado.aprobado for resultado in resultados),
        "resultados": [asdict(resultado) for resultado in resultados],
    }
    ruta.write_text(
        json.dumps(contenido, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    logger.info(
        "Evidencia guardada | ruta=%s | aprobadas=%d | fallidas=%d",
        ruta,
        contenido["aprobadas"],
        contenido["fallidas"],
    )
    return ruta


def main() -> int:
    configurar_logging(BASE_DIR / "logs" / "software_fj.log")
    try:
        resultados = ejecutar_simulaciones()
        ruta = guardar_resultados(resultados)
        for resultado in resultados:
            estado = "APROBADA" if resultado.aprobado else "FALLIDA"
            print(
                f"{resultado.numero:02d}. [{estado}] {resultado.tipo}: "
                f"{resultado.nombre} -> {resultado.detalle}"
            )
        print(f"\nEvidencia: {ruta}")
        return 0 if all(resultado.aprobado for resultado in resultados) else 1
    finally:
        cerrar_logging()


if __name__ == "__main__":
    raise SystemExit(main())
