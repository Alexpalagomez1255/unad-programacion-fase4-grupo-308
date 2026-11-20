"""Configuración centralizada del registro de eventos y errores."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .excepciones import ErrorAplicacion


logger = logging.getLogger("software_fj")


def configurar_logging(ruta: str | Path) -> Path:
    """Crea un log rotativo sin añadir dos manejadores para el mismo archivo."""

    ruta_log = Path(ruta)
    try:
        ruta_log.parent.mkdir(parents=True, exist_ok=True)
        ruta_resuelta = ruta_log.resolve()
        existe = any(
            isinstance(manejador, RotatingFileHandler)
            and Path(manejador.baseFilename).resolve() == ruta_resuelta
            for manejador in logger.handlers
        )
        if not existe:
            manejador = RotatingFileHandler(
                ruta_log,
                maxBytes=1_000_000,
                backupCount=3,
                encoding="utf-8",
            )
            manejador.setFormatter(
                logging.Formatter(
                    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                )
            )
            logger.addHandler(manejador)
    except OSError as exc:
        raise ErrorAplicacion(
            f"No fue posible crear el archivo de log {ruta_log}."
        ) from exc
    else:
        logger.info("Logging configurado | archivo=%s", ruta_log)
        return ruta_log
    finally:
        logger.setLevel(logging.DEBUG)
        logger.propagate = False


def cerrar_logging() -> None:
    """Libera los archivos abiertos por los manejadores del logger."""

    for manejador in list(logger.handlers):
        manejador.flush()
        manejador.close()
        logger.removeHandler(manejador)
