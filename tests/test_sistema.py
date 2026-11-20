"""Pruebas automatizadas del sistema de Software FJ."""

from decimal import Decimal
from pathlib import Path
import logging
import sys
import tempfile
import unittest


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR / "src"))

from software_fj import (  # noqa: E402
    Cliente,
    ErrorDuplicado,
    ErrorNoEncontrado,
    ErrorOperacionNoPermitida,
    ErrorReservaInvalida,
    ErrorServicioNoDisponible,
    ErrorValidacion,
    EstadoReserva,
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
from software_fj.modelos import decimal_no_negativo  # noqa: E402


class ValidacionTests(unittest.TestCase):
    def test_decimal_redondea_centavos(self) -> None:
        self.assertEqual(decimal_no_negativo("12.345", "Valor"), Decimal("12.35"))

    def test_decimal_rechaza_texto_y_encadena_causa(self) -> None:
        with self.assertRaises(ErrorValidacion) as contexto:
            decimal_no_negativo("texto", "Valor")
        self.assertIsNotNone(contexto.exception.__cause__)

    def test_decimal_rechaza_nan_infinito_y_negativo(self) -> None:
        for valor in ("NaN", "Infinity", "-1"):
            with self.subTest(valor=valor):
                with self.assertRaises(ErrorValidacion):
                    decimal_no_negativo(valor, "Valor")

    def test_cliente_normaliza_datos(self) -> None:
        cliente = Cliente(" cli-1 ", " Ana ", " ANA@EXAMPLE.COM ", "+57 300-123-4567")
        self.assertEqual(cliente.codigo, "CLI-1")
        self.assertEqual(cliente.nombre, "Ana")
        self.assertEqual(cliente.correo, "ana@example.com")
        self.assertEqual(cliente.telefono, "573001234567")

    def test_cliente_rechaza_correo_invalido(self) -> None:
        with self.assertRaises(ErrorValidacion):
            Cliente("C-1", "Ana", "sin-arroba", "3001234567")

    def test_cliente_rechaza_telefono_invalido(self) -> None:
        for telefono in ("123", "abc3001234"):
            with self.subTest(telefono=telefono):
                with self.assertRaises(ErrorValidacion):
                    Cliente("C-1", "Ana", "ana@example.com", telefono)


class ServicioTests(unittest.TestCase):
    def test_sala_calcula_impuesto_y_descuento(self) -> None:
        sala = ServicioSala("S-1", "Sala", "100", 10)
        total = sala.calcular_costo(2, impuesto=19, descuento=10, participantes=5)
        self.assertEqual(total, Decimal("214.20"))

    def test_sala_rechaza_capacidad(self) -> None:
        sala = ServicioSala("S-1", "Sala", "100", 5)
        with self.assertRaises(ErrorReservaInvalida):
            sala.calcular_costo(1, participantes=6)

    def test_sala_rechaza_duracion_maxima(self) -> None:
        sala = ServicioSala("S-1", "Sala", "100", 5, maximo_horas=4)
        with self.assertRaises(ErrorReservaInvalida):
            sala.calcular_costo(5, participantes=2)

    def test_equipo_incluye_deposito(self) -> None:
        equipo = ServicioAlquilerEquipo("E-1", "Portátil", "100", 3, 10)
        self.assertEqual(equipo.calcular_costo(2, cantidad=2), Decimal("440.00"))

    def test_equipo_rechaza_stock_insuficiente(self) -> None:
        equipo = ServicioAlquilerEquipo("E-1", "Portátil", "100", 3)
        with self.assertRaises(ErrorReservaInvalida):
            equipo.calcular_costo(1, cantidad=4)

    def test_equipo_rechaza_dia_fraccionario(self) -> None:
        equipo = ServicioAlquilerEquipo("E-1", "Portátil", "100", 3)
        with self.assertRaises(ErrorReservaInvalida):
            equipo.calcular_costo("1.5", cantidad=1)

    def test_asesoria_valida_modalidad(self) -> None:
        asesoria = ServicioAsesoria("A-1", "Python", "Laura", "100")
        self.assertEqual(
            asesoria.calcular_costo(2, modalidad="virtual"), Decimal("200.00")
        )

    def test_asesoria_rechaza_modalidad(self) -> None:
        asesoria = ServicioAsesoria("A-1", "Python", "Laura", "100")
        with self.assertRaises(ErrorReservaInvalida):
            asesoria.calcular_costo(2, modalidad="telepática")

    def test_servicio_no_disponible(self) -> None:
        sala = ServicioSala("S-1", "Sala", "100", 5, disponible=False)
        with self.assertRaises(ErrorServicioNoDisponible):
            sala.calcular_costo(1, participantes=2)

    def test_porcentaje_no_supera_cien(self) -> None:
        sala = ServicioSala("S-1", "Sala", "100", 5)
        with self.assertRaises(ErrorValidacion):
            sala.calcular_costo(1, descuento=101, participantes=2)


class GestorReservaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gestor = GestorReservas()
        self.cliente = Cliente("C-1", "Ana", "ana@example.com", "3001234567")
        self.sala = ServicioSala("S-1", "Sala", "100", 5)
        self.gestor.registrar_cliente(self.cliente)
        self.gestor.registrar_servicio(self.sala)

    def test_registra_y_busca_cliente(self) -> None:
        self.assertIs(self.gestor.buscar_cliente("c-1"), self.cliente)

    def test_rechaza_cliente_duplicado(self) -> None:
        with self.assertRaises(ErrorDuplicado):
            self.gestor.registrar_cliente(
                Cliente("c-1", "Otra", "otra@example.com", "3001234568")
            )

    def test_no_encontrado_encadena_key_error(self) -> None:
        with self.assertRaises(ErrorNoEncontrado) as contexto:
            self.gestor.buscar_servicio("NO-EXISTE")
        self.assertIsInstance(contexto.exception.__cause__, KeyError)

    def test_crea_reserva_valida(self) -> None:
        reserva = self.gestor.crear_reserva(
            "R-1", "C-1", "S-1", 2, participantes=3
        )
        self.assertEqual(reserva.total, Decimal("200.00"))
        self.assertEqual(reserva.estado, EstadoReserva.PENDIENTE)

    def test_no_almacena_reserva_invalida(self) -> None:
        with self.assertRaises(ErrorReservaInvalida):
            self.gestor.crear_reserva(
                "R-1", "C-1", "S-1", 2, participantes=10
            )
        self.assertEqual(self.gestor.listar_reservas(), ())

    def test_confirma_y_procesa_reserva(self) -> None:
        reserva = self.gestor.crear_reserva(
            "R-1", "C-1", "S-1", 2, participantes=3
        )
        reserva.confirmar()
        reserva.procesar()
        self.assertEqual(reserva.estado, EstadoReserva.PROCESADA)

    def test_cancela_reserva_pendiente(self) -> None:
        reserva = self.gestor.crear_reserva(
            "R-1", "C-1", "S-1", 2, participantes=3
        )
        reserva.cancelar()
        self.assertEqual(reserva.estado, EstadoReserva.CANCELADA)

    def test_no_procesa_reserva_cancelada(self) -> None:
        reserva = self.gestor.crear_reserva(
            "R-1", "C-1", "S-1", 2, participantes=3
        )
        reserva.cancelar()
        with self.assertRaises(ErrorOperacionNoPermitida):
            reserva.procesar()

    def test_no_cancela_reserva_procesada(self) -> None:
        reserva = self.gestor.crear_reserva(
            "R-1", "C-1", "S-1", 2, participantes=3
        )
        reserva.confirmar()
        reserva.procesar()
        with self.assertRaises(ErrorOperacionNoPermitida):
            reserva.cancelar()

    def test_no_confirma_dos_veces(self) -> None:
        reserva = self.gestor.crear_reserva(
            "R-1", "C-1", "S-1", 2, participantes=3
        )
        reserva.confirmar()
        with self.assertRaises(ErrorOperacionNoPermitida):
            reserva.confirmar()

    def test_cambio_disponibilidad_antes_de_confirmar(self) -> None:
        reserva = self.gestor.crear_reserva(
            "R-1", "C-1", "S-1", 2, participantes=3
        )
        self.sala.cambiar_disponibilidad(False)
        with self.assertRaises(ErrorServicioNoDisponible):
            reserva.confirmar()

    def test_continua_despues_de_error(self) -> None:
        with self.assertRaises(ErrorReservaInvalida):
            self.gestor.crear_reserva(
                "R-MAL", "C-1", "S-1", 2, participantes=99
            )
        reserva = self.gestor.crear_reserva(
            "R-BIEN", "C-1", "S-1", 1, participantes=2
        )
        self.assertEqual(reserva.codigo, "R-BIEN")


class LoggingTests(unittest.TestCase):
    def tearDown(self) -> None:
        cerrar_logging()

    def test_log_registra_evento_y_error(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "software_fj.log"
            configurar_logging(ruta)
            gestor = GestorReservas()
            gestor.registrar_cliente(
                Cliente("C-1", "Ana", "ana@example.com", "3001234567")
            )
            with self.assertRaises(ErrorNoEncontrado):
                gestor.buscar_servicio("S-404")
            for manejador in logger.handlers:
                manejador.flush()
            contenido = ruta.read_text(encoding="utf-8")
            self.assertIn("Entidad registrada", contenido)
            self.assertIn("Entidad no encontrada", contenido)
            self.assertIn("INFO", contenido)
            self.assertIn("WARNING", contenido)

    def test_no_duplica_manejador(self) -> None:
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "software_fj.log"
            configurar_logging(ruta)
            configurar_logging(ruta)
            archivos = [
                manejador
                for manejador in logger.handlers
                if isinstance(manejador, logging.FileHandler)
            ]
            self.assertEqual(len(archivos), 1)


if __name__ == "__main__":
    unittest.main()
