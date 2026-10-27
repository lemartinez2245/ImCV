"""Generación de fixtures de prueba para el pipeline de ingesta.

Todos los archivos se construyen de forma **100 % local**: los PDF con
``weasyprint`` (HTML → PDF) y los Word con ``python-docx``. Esto garantiza el
modo offline del proyecto y evita depender de binarios externos.
"""

from __future__ import annotations

from pathlib import Path

import docx
from weasyprint import HTML

__all__ = [
    "build_all",
    "build_corrupt_pdf",
    "build_docx",
    "build_empty_pdf",
    "build_generic_pdf",
    "build_linkedin_pdf",
]

# Contenido del PDF exportado de LinkedIn (en español, con la estructura típica
# de dos columnas / secciones de la red social).
_LINKEDIN_HTML = """
<html><head><meta charset="utf-8"><style>
body {{ font-family: sans-serif; }}
</style></head><body>
<h1>Ana García López</h1>
<p>Ingeniera de Software Senior</p>
<p>Madrid, España</p>
<p>ana.garcia@example.com</p>
<p>+34 600 123 456</p>
<p>linkedin.com/in/anagarcia-dev</p>
<p>github.com/anagarcia-dev</p>
<h2>Resumen</h2>
<p>Ingeniera de software con más de ocho años de experiencia construyendo
servicios distribuidos y plataformas de datos a escala.</p>
<h2>Aptitudes principales</h2>
<p>Python, LangGraph, TypeScript, Liderazgo de equipos, AWS</p>
<h2>Experiencia</h2>
<p>Ingeniera de Software Senior</p>
<p>Acme Corp</p>
<p>ene 2020 - Presente</p>
<ul>
<li>Lideré un equipo de cinco desarrolladores</li>
<li>Reduje la latencia del sistema en un 30%</li>
</ul>
<p>Desarrolladora Backend</p>
<p>Tech Solutions</p>
<p>2018 - 2020</p>
<ul>
<li>Diseñé APIs REST escalables</li>
</ul>
<h2>Educación</h2>
<p>Grado en Ingeniería Informática</p>
<p>Universidad Politécnica de Madrid</p>
<p>2014 - 2018</p>
<h2>Idiomas</h2>
<p>Español - Nativo</p>
<p>Inglés - Avanzado</p>
</body></html>
"""

# Contenido de un CV genérico en inglés, sin rastro de LinkedIn.
_GENERIC_HTML = """
<html><head><meta charset="utf-8"><style>
body {{ font-family: sans-serif; }}
</style></head><body>
<h1>John Smith</h1>
<p>Software Engineer</p>
<p>San Francisco, CA</p>
<p>john.smith@example.com</p>
<p>+1 555 987 6543</p>
<p>github.com/johnsmith-dev</p>
<h2>Summary</h2>
<p>Experienced software engineer focused on backend systems and developer tooling.</p>
<h2>Skills</h2>
<p>Python, JavaScript, Docker, Kubernetes</p>
<h2>Experience</h2>
<p>Senior Engineer</p>
<p>BigTech Inc</p>
<p>Jan 2020 - Present</p>
<ul>
<li>Led migration to microservices architecture</li>
</ul>
<p>Junior Engineer</p>
<p>StartupXYZ</p>
<p>2016 - 2019</p>
<ul>
<li>Built internal tooling in Python</li>
</ul>
<h2>Education</h2>
<p>B.S. Computer Science</p>
<p>Stanford University</p>
<p>2012 - 2016</p>
<h2>Languages</h2>
<p>English - Native</p>
<p>Spanish - Intermediate</p>
</body></html>
"""


def build_linkedin_pdf(path: Path) -> Path:
    """Genera un PDF estilo exportación de LinkedIn."""
    HTML(string=_LINKEDIN_HTML).write_pdf(path)
    return path


def build_generic_pdf(path: Path) -> Path:
    """Genera un PDF de CV genérico en inglés."""
    HTML(string=_GENERIC_HTML).write_pdf(path)
    return path


def build_empty_pdf(path: Path) -> Path:
    """Genera un PDF válido pero sin texto extraíble."""
    HTML(string="<html><body></body></html>").write_pdf(path)
    return path


def build_corrupt_pdf(path: Path) -> Path:
    """Genera un archivo con extensión ``.pdf`` pero contenido corrupto."""
    path.write_bytes(b"%PDF-1.4\n\x00\x01\x02esto no es un PDF valido\x00\xff")
    return path


def build_docx(path: Path) -> Path:
    """Genera un documento Word con estilos de encabezado y tablas."""
    document = docx.Document()

    document.add_heading("María Fernández Ruiz", level=1)
    document.add_paragraph("Data Scientist")
    document.add_paragraph("Bogotá, Colombia")
    document.add_paragraph("maria.fernandez@example.com")
    document.add_paragraph("linkedin.com/in/mariafernandez-dev")

    document.add_heading("Resumen", level=2)
    document.add_paragraph(
        "Científica de datos con experiencia en modelos de lenguaje y análisis predictivo."
    )

    document.add_heading("Habilidades", level=2)
    document.add_paragraph("Python, Pandas, Scikit-learn, SQL")

    document.add_heading("Experiencia", level=2)
    document.add_paragraph("Data Scientist")
    document.add_paragraph("DataCorp")
    document.add_paragraph("mar 2021 - Presente")
    document.add_paragraph("Desarrollé modelos de predicción de churn", style="List Bullet")
    document.add_paragraph("Automatice reportes semanales con Python", style="List Bullet")

    document.add_paragraph("Analista de Datos")
    document.add_paragraph("ConsultoraXYZ")
    document.add_paragraph("2019 - 2021")

    document.add_heading("Educación", level=2)
    document.add_paragraph("Maestría en Ciencia de Datos")
    document.add_paragraph("Universidad Nacional")
    document.add_paragraph("2017 - 2019")

    document.add_heading("Idiomas", level=2)
    # Tabla de idiomas para ejercitar el parser de tablas.
    table = document.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Español"
    table.rows[0].cells[1].text = "Nativo"
    row = table.add_row().cells
    row[0].text = "Inglés"
    row[1].text = "Avanzado"

    document.save(path)
    return path


def build_all(directory: Path) -> dict[str, Path]:
    """Construye todas las fixtures dentro de ``directory``.

    Returns:
        Mapping con nombre lógico → ruta del archivo generado.
    """
    directory.mkdir(parents=True, exist_ok=True)
    return {
        "linkedin": build_linkedin_pdf(directory / "sample_linkedin.pdf"),
        "generic": build_generic_pdf(directory / "sample_generic.pdf"),
        "empty": build_empty_pdf(directory / "sample_empty.pdf"),
        "corrupt": build_corrupt_pdf(directory / "sample_corrupt.pdf"),
        "docx": build_docx(directory / "sample_resume.docx"),
    }


if __name__ == "__main__":
    # Permite regenerar las fixtures estáticas: python -m tests.fixtures.build
    fixtures_dir = Path(__file__).parent
    built = build_all(fixtures_dir)
    for name, path in built.items():
        print(f"{name}: {path}")
