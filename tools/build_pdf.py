"""Genera el informe del aporte individual de Alejandro Palacios."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = Path(__file__).resolve().parents[1]
RESULTADOS = BASE_DIR / "evidencias" / "resultados_simulaciones.json"
OUTPUT = (
    BASE_DIR
    / "output"
    / "pdf"
    / "Aporte_Individual_Fase_4_Alejandro_Palacios.pdf"
)

AZUL = colors.HexColor("#17365D")
AZUL_CLARO = colors.HexColor("#EAF2F8")
GRIS = colors.HexColor("#D9D9D9")
ROJO = colors.HexColor("#9C0006")

FUENTES = Path("/usr/share/fonts/truetype/noto")
pdfmetrics.registerFont(TTFont("NotoSans", str(FUENTES / "NotoSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("NotoSans-Bold", str(FUENTES / "NotoSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("NotoSans-Italic", str(FUENTES / "NotoSans-Italic.ttf")))
pdfmetrics.registerFont(
    TTFont("NotoSans-BoldItalic", str(FUENTES / "NotoSans-BoldItalic.ttf"))
)
pdfmetrics.registerFontFamily(
    "NotoSans",
    normal="NotoSans",
    bold="NotoSans-Bold",
    italic="NotoSans-Italic",
    boldItalic="NotoSans-BoldItalic",
)


def estilos_documento():
    base = getSampleStyleSheet()
    return {
        "titulo_portada": ParagraphStyle(
            "TituloPortada",
            parent=base["Title"],
            fontName="NotoSans-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=14,
        ),
        "subtitulo": ParagraphStyle(
            "Subtitulo",
            parent=base["Normal"],
            fontName="NotoSans-Bold",
            fontSize=13,
            leading=17,
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="NotoSans-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.black,
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="NotoSans-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.black,
            spaceBefore=8,
            spaceAfter=7,
        ),
        "cuerpo": ParagraphStyle(
            "Cuerpo",
            parent=base["BodyText"],
            fontName="NotoSans",
            fontSize=11,
            leading=17,
            alignment=TA_JUSTIFY,
            firstLineIndent=0.45 * inch,
            spaceAfter=9,
        ),
        "sin_sangria": ParagraphStyle(
            "SinSangria",
            parent=base["BodyText"],
            fontName="NotoSans",
            fontSize=11,
            leading=16,
            alignment=TA_LEFT,
            spaceAfter=8,
        ),
        "centro": ParagraphStyle(
            "Centro",
            parent=base["Normal"],
            fontName="NotoSans",
            fontSize=10.5,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "marcador": ParagraphStyle(
            "Marcador",
            parent=base["Normal"],
            fontName="NotoSans-Bold",
            fontSize=11,
            leading=15,
            textColor=ROJO,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "lista": ParagraphStyle(
            "Lista",
            parent=base["BodyText"],
            fontName="NotoSans",
            fontSize=10.5,
            leading=15,
            leftIndent=18,
            firstLineIndent=-9,
            bulletIndent=6,
            spaceAfter=5,
        ),
        "referencia": ParagraphStyle(
            "Referencia",
            parent=base["BodyText"],
            fontName="NotoSans",
            fontSize=10.5,
            leading=20,
            leftIndent=0.45 * inch,
            firstLineIndent=-0.45 * inch,
            spaceAfter=6,
        ),
        "tabla": ParagraphStyle(
            "Tabla",
            parent=base["Normal"],
            fontName="NotoSans",
            fontSize=8.3,
            leading=10.2,
            alignment=TA_LEFT,
        ),
        "tabla_centro": ParagraphStyle(
            "TablaCentro",
            parent=base["Normal"],
            fontName="NotoSans",
            fontSize=8.3,
            leading=10.2,
            alignment=TA_CENTER,
        ),
        "tabla_header": ParagraphStyle(
            "TablaHeader",
            parent=base["Normal"],
            fontName="NotoSans-Bold",
            fontSize=8.5,
            leading=10.5,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
    }


def agregar_pie(canvas, documento):
    canvas.saveState()
    canvas.setFont("NotoSans", 8)
    canvas.setFillColor(colors.HexColor("#333333"))
    canvas.drawString(
        documento.leftMargin,
        0.42 * inch,
        "Programación 213023   Grupo 308",
    )
    canvas.drawRightString(
        letter[0] - documento.rightMargin,
        0.42 * inch,
        str(documento.page),
    )
    canvas.restoreState()


def portada_sin_pie(canvas, documento):
    """La portada académica no muestra numeración ni texto de pie."""

    return None


def p(texto, estilo):
    return Paragraph(texto, estilo)


def lista(textos, estilos):
    return [p(f"• {texto}", estilos["lista"]) for texto in textos]


def tabla(datos, anchos, estilos, *, repetir=True):
    filas = []
    for indice, fila in enumerate(datos):
        estilo = estilos["tabla_header"] if indice == 0 else estilos["tabla"]
        filas.append(
            [
                p(str(valor), estilos["tabla_centro"] if columna in (0, 1, len(fila) - 1) and indice else estilo)
                for columna, valor in enumerate(fila)
            ]
        )
    objeto = Table(
        filas,
        colWidths=anchos,
        repeatRows=1 if repetir else 0,
        hAlign="CENTER",
    )
    comandos = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, GRIS),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for indice in range(2, len(filas), 2):
        comandos.append(("BACKGROUND", (0, indice), (-1, indice), AZUL_CLARO))
    objeto.setStyle(TableStyle(comandos))
    return objeto


def construir() -> Path:
    if not RESULTADOS.exists():
        raise FileNotFoundError("Ejecute simulaciones.py antes de construir el PDF.")
    resultados = json.loads(RESULTADOS.read_text(encoding="utf-8"))
    if resultados["fallidas"]:
        raise RuntimeError("No se construye el informe con simulaciones fallidas.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    estilos = estilos_documento()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.9 * inch,
        title="Aporte individual Fase 4 Software FJ",
        author="Alejandro Palacios",
        subject="Excepciones logs y simulaciones del sistema de reservas",
    )
    historia = []

    # Portada
    historia.extend(
        [
            Spacer(1, 0.12 * inch),
            p("UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA", estilos["subtitulo"]),
            Spacer(1, 0.38 * inch),
            p("Fase 4 Componente práctico Prácticas simuladas", estilos["titulo_portada"]),
            p(
                "Sistema Integral de Gestión de Clientes Servicios y Reservas",
                estilos["subtitulo"],
            ),
            p("Informe de aporte individual", estilos["centro"]),
            Spacer(1, 0.28 * inch),
            p("Alejandro Palacios", estilos["centro"]),
            Spacer(1, 0.32 * inch),
            p("Grupo 308", estilos["centro"]),
            p("Curso Programación 213023", estilos["centro"]),
            p("Programa de Ingeniería de Sistemas", estilos["centro"]),
            p("Escuela de Ciencias Básicas Tecnología e Ingeniería", estilos["centro"]),
            Spacer(1, 0.24 * inch),
            p("Noviembre de 2026", estilos["centro"]),
            PageBreak(),
        ]
    )

    # Introducción
    historia.extend(
        [
            p("Introducción", estilos["h1"]),
            p(
                "Este informe presenta el aporte individual de Alejandro Palacios al "
                "desarrollo del Sistema Integral de Gestión de Clientes, Servicios y "
                "Reservas propuesto en el Anexo 3 para la empresa "
                "Software FJ. La aplicación administra objetos y listas en memoria, sin "
                "utilizar una base de datos, y registra en archivos únicamente los eventos "
                "y errores relevantes (Universidad Nacional Abierta y a Distancia [UNAD], "
                "2026a).",
                estilos["cuerpo"],
            ),
            p(
                "La solución aplica abstracción, herencia, polimorfismo y encapsulación. "
                "Una clase abstracta define el contrato común de los servicios, y las "
                "reservas de salas, el alquiler de equipos y las asesorías especializadas "
                "sobrescriben la validación y el cálculo de costos según sus propias reglas. "
                "Los métodos permiten incluir impuestos, descuentos y parámetros opcionales.",
                estilos["cuerpo"],
            ),
            p(
                "El manejo de errores se implementó mediante excepciones personalizadas, "
                "bloques try, except, else y finally, y encadenamiento de excepciones. "
                "Quince simulaciones verifican registros correctos e incorrectos, servicios "
                "no disponibles, reservas inválidas y transiciones de estado. El objetivo es "
                "que un error controlado quede documentado sin detener las operaciones "
                "posteriores, de acuerdo con las prácticas descritas en el tutorial oficial "
                "de Python (Van Rossum & Drake, 2024).",
                estilos["cuerpo"],
            ),
            p("Objetivo del aporte", estilos["h2"]),
            p(
                "Preparar una base funcional y verificable de la aplicación orientada a "
                "objetos que gestione clientes, "
                "servicios y reservas de forma estable, registre los eventos operativos y "
                "controle datos inválidos u operaciones no permitidas sin interrumpir la "
                "ejecución general.",
                estilos["sin_sangria"],
            ),
            PageBreak(),
        ]
    )

    # GitHub
    historia.extend(
        [
            p("Enlace del repositorio en GitHub", estilos["h1"]),
            p(
                "Repositorio del proyecto",
                estilos["h2"],
            ),
            p(
                '<link href="https://github.com/Alexpalagomez1255/unad-programacion-fase4-grupo-308" '
                'color="#17365D"><u>https://github.com/Alexpalagomez1255/'
                "unad-programacion-fase4-grupo-308</u></link>",
                estilos["sin_sangria"],
            ),
            p(
                "El repositorio fue creado porque el enlace suministrado en el curso "
                "redirigía a la página principal de GitHub y no a un proyecto específico. "
                "Este espacio permite centralizar el código, las pruebas y las evidencias "
                "del grupo 308. Allí se incorpora el aporte individual documentado en este "
                "informe.",
                estilos["cuerpo"],
            ),
            p("Alcance del aporte individual", estilos["h2"]),
            *lista(
                [
                    "Diseño del dominio con clientes, servicios polimórficos y reservas.",
                    "Implementación de excepciones personalizadas y validaciones de negocio.",
                    "Configuración de logs para eventos exitosos, advertencias y errores.",
                    "Creación de quince simulaciones válidas e inválidas con continuidad.",
                    "Creación de treinta pruebas automatizadas y evidencia reproducible.",
                    "Documentación de ejecución y preparación del presente informe individual.",
                ],
                estilos,
            ),
            p("Integración posterior", estilos["h2"]),
            p(
                "El reporte grupal se elaborará después de recibir, integrar y verificar "
                "los aportes de los demás integrantes del grupo.",
                estilos["sin_sangria"],
            ),
            PageBreak(),
        ]
    )

    # Diseño y excepciones
    historia.extend(
        [
            p("Diseño orientado a objetos y manejo de excepciones", estilos["h1"]),
            p(
                "El gestor mantiene tres colecciones internas: clientes, servicios y "
                "reservas. Cliente encapsula el nombre, correo y teléfono. Servicio es una "
                "clase abstracta, y cada clase concreta valida sus parámetros y calcula el "
                "subtotal de forma polimórfica. Reserva integra el cliente, el servicio, la "
                "duración, el costo y los estados pendiente, confirmada, procesada y "
                "cancelada.",
                estilos["cuerpo"],
            ),
            tabla(
                [
                    ["Componente", "Responsabilidad"],
                    ["Cliente", "Validar y encapsular los datos personales"],
                    ["ServicioSala", "Validar horas, participantes y capacidad"],
                    ["ServicioAlquilerEquipo", "Validar días, cantidad, stock y depósito"],
                    ["ServicioAsesoria", "Validar duración, especialista y modalidad"],
                    ["Reserva", "Calcular el total y controlar las transiciones de estado"],
                    ["GestorReservas", "Registrar y buscar objetos en colecciones internas"],
                ],
                [1.9 * inch, 4.7 * inch],
                estilos,
            ),
            Spacer(1, 0.14 * inch),
            p("Excepciones personalizadas", estilos["h2"]),
            tabla(
                [
                    ["Excepción", "Situación controlada"],
                    ["ErrorValidacion", "Datos vacíos, formatos erróneos o valores fuera de rango"],
                    ["ErrorDuplicado", "Código de cliente, servicio o reserva ya registrado"],
                    ["ErrorNoEncontrado", "Entidad inexistente; conserva el KeyError original"],
                    ["ErrorServicioNoDisponible", "Intento de reservar o confirmar un servicio inactivo"],
                    ["ErrorReservaInvalida", "Capacidad, duración, modalidad o stock incompatibles"],
                    ["ErrorOperacionNoPermitida", "Transición incompatible con el estado de la reserva"],
                    ["ErrorCalculoInconsistente", "Costo no finito, negativo o igual a cero"],
                ],
                [2.15 * inch, 4.45 * inch],
                estilos,
            ),
            PageBreak(),
        ]
    )

    # Simulaciones
    filas_simulaciones = [["Caso", "Tipo", "Operación", "Resultado"]]
    for resultado in resultados["resultados"]:
        filas_simulaciones.append(
            [
                resultado["numero"],
                resultado["tipo"].capitalize(),
                resultado["nombre"],
                "Aprobada" if resultado["aprobado"] else "Fallida",
            ]
        )
    historia.extend(
        [
            p("Simulaciones válidas e inválidas", estilos["h1"]),
            p(
                f"Se ejecutaron {resultados['total']} operaciones secuenciales. Las "
                f"{resultados['aprobadas']} produjeron el resultado esperado. Una operación "
                "inválida solo se considera aprobada cuando el sistema captura la excepción "
                "prevista, registra el evento y continúa con el caso siguiente.",
                estilos["cuerpo"],
            ),
            tabla(
                filas_simulaciones,
                [0.48 * inch, 0.72 * inch, 4.55 * inch, 0.85 * inch],
                estilos,
            ),
            Spacer(1, 0.14 * inch),
            p("Resultado de las pruebas automatizadas", estilos["h2"]),
            p(
                "La suite contiene 30 pruebas y finalizó sin fallos. Cubre validaciones, "
                "cálculos polimórficos, impuestos, descuentos, capacidad de salas, stock de "
                "equipos, modalidades de asesoría, disponibilidad, ciclo de vida de las "
                "reservas, encadenamiento de errores, continuidad y escritura del log.",
                estilos["sin_sangria"],
            ),
            PageBreak(),
        ]
    )

    # Conclusiones
    conclusiones = [
        "La clase abstracta Servicio permite que las salas, los equipos y las asesorías "
        "compartan una interfaz común sin perder sus reglas particulares de validación y costo.",
        "Las excepciones personalizadas distinguen errores de entrada, disponibilidad, "
        "búsqueda, estado y cálculo. El encadenamiento conserva la causa técnica cuando una "
        "conversión o consulta falla.",
        "Los logs registran operaciones exitosas, advertencias, errores y trazas. Las quince "
        "simulaciones confirmaron que una operación inválida no detiene las operaciones posteriores.",
        "Las treinta pruebas automatizadas respaldan las reglas principales del aporte "
        "individual y ofrecen una línea base para integrar posteriormente el trabajo de "
        "los demás integrantes sin alterar el comportamiento ya verificado.",
    ]
    historia.extend([p("Conclusiones", estilos["h1"]), *lista(conclusiones, estilos), PageBreak()])

    # Referencias
    referencias = [
        "Cuevas Álvarez, A. (2016). <i>Python 3 curso práctico</i>. RA-MA Editorial. "
        "https://elibro-net.bibliotecavirtual.unad.edu.co/es/ereader/unad/106404?page=373",
        "Romano, F., Baka, B., & Phillips, D. (2019). <i>Getting started with Python "
        "Understand key data structures and use Python in object-oriented programming</i>. "
        "Packt Publishing.",
        "Silva, F. D. (2025). <i>Basics of using GitHub</i> [Objeto virtual de información]. "
        "Repositorio Institucional UNAD. https://repository.unad.edu.co/handle/10596/75882",
        "Universidad Nacional Abierta y a Distancia. (2026a). <i>Anexo 3 Problema a "
        "desarrollar Fase 4</i> [Anexo de la actividad].",
        "Universidad Nacional Abierta y a Distancia. (2026b). <i>Guía para el desarrollo "
        "del componente práctico Fase 4 Prácticas simuladas</i> [Guía de aprendizaje].",
        "Van Rossum, G., & Drake, F. L., Jr. (2024). <i>El tutorial de Python</i>. Python "
        "Software Foundation. https://docs.python.org/es/3.12/tutorial/errors.html",
        "Zambrano, J. P. (2025). <i>Introducción al uso de GitHub</i> [Objeto virtual de "
        "información]. Repositorio Institucional UNAD. "
        "https://repository.unad.edu.co/handle/10596/75876",
    ]
    historia.append(p("Referencias", estilos["h1"]))
    historia.extend(p(referencia, estilos["referencia"]) for referencia in referencias)
    historia.append(Spacer(1, 0.15 * inch))
    historia.append(p("Integración grupal posterior", estilos["h2"]))
    historia.extend(
        lista(
            [
                "Recibir y revisar los aportes de los demás integrantes.",
                "Integrar los cambios mediante ramas y pull requests.",
                "Actualizar las pruebas y evidencias después de la integración.",
                "Preparar el documento grupal con los datos completos del equipo y del tutor.",
            ],
            estilos,
        )
    )

    doc.build(historia, onFirstPage=portada_sin_pie, onLaterPages=agregar_pie)
    return OUTPUT


if __name__ == "__main__":
    print(construir())
