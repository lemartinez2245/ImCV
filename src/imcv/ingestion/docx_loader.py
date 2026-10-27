"""Cargador de documentos Word (``.docx``).

Segmenta el documento usando los estilos de encabezado de ``python-docx`` y las
tablas, y normaliza el resultado a un :class:`~imcv.models.CVModel`. Reutiliza
los mismos parsers de sección que los cargadores de PDF.
"""

from __future__ import annotations

from pathlib import Path

import docx
from docx.table import Table
from docx.text.paragraph import Paragraph

from imcv.exceptions import ExtractionError, ValidationError
from imcv.ingestion.base import DocumentLoader
from imcv.ingestion.section_parsers import (
    parse_certifications,
    parse_contact,
    parse_education,
    parse_experience,
    parse_languages,
    parse_projects,
    parse_skills,
)
from imcv.models import CVModel
from imcv.sections import CVSection, match_section

__all__ = ["DocxLoader"]


class DocxLoader(DocumentLoader):
    """Carga un CV desde un archivo Word ``.docx``."""

    def load(self, path: Path) -> CVModel:
        path = Path(path)

        try:
            document = docx.Document(path)
        except Exception as exc:  # noqa: BLE001 - python-docx lanza excepciones variadas
            raise ExtractionError(f"No se pudo abrir el documento Word: {path}") from exc

        # Recorrer el documento en orden, mezclando párrafos y tablas.
        ordered_lines = _iter_document_lines(document)

        if not any(line.strip() for line in ordered_lines):
            raise ExtractionError(f"El documento Word está vacío: {path}")

        sections = _segment_by_heading(ordered_lines)
        full_text = "\n".join(ordered_lines)
        lead_lines = [line for line in ordered_lines if line.strip()][:6]

        try:
            contact = parse_contact(lead_lines, full_text)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        return CVModel(
            contact=contact,
            summary=_first_line(sections.get(CVSection.SUMMARY, [])),
            experience=parse_experience(sections.get(CVSection.EXPERIENCE, [])),
            education=parse_education(sections.get(CVSection.EDUCATION, [])),
            skills=parse_skills(sections.get(CVSection.SKILLS, [])),
            languages=parse_languages(sections.get(CVSection.LANGUAGES, [])),
            certifications=parse_certifications(sections.get(CVSection.CERTIFICATIONS, [])),
            projects=parse_projects(sections.get(CVSection.PROJECTS, [])),
        )


def _iter_document_lines(document: docx.Document) -> list[str]:
    """Recorre párrafos y tablas del documento en orden, devolviendo líneas.

    El cuerpo del documento (``document.element.body``) contiene tanto
    párrafos como tablas en su orden real de aparición.
    """
    lines: list[str] = []
    body = document.element.body

    # Mapeamos los elementos del cuerpo a sus objetos de alto nivel.
    para_map = {p._element: p for p in document.paragraphs}
    table_map = {t._element: t for t in document.tables}

    for child in body.iterchildren():
        if child in para_map:
            para: Paragraph = para_map[child]
            lines.append(para.text)
        elif child in table_map:
            table: Table = table_map[child]
            lines.extend(_table_lines(table))

    return lines


def _table_lines(table: Table) -> list[str]:
    """Convierte una tabla en líneas de texto (una por fila, celdas unidas)."""
    lines: list[str] = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        # Unimos las celdas de la fila con " - " para facilitar su parsing.
        joined = " - ".join(c for c in cells if c)
        if joined:
            lines.append(joined)
    return lines


def _segment_by_heading(lines: list[str]) -> dict[CVSection, list[str]]:
    """Segmenta las líneas por encabezados de sección detectados.

    Distingue encabezados por estilo (Heading) y, de forma complementaria, por
    coincidencia de texto con el vocabulario multilingüe de secciones.
    """
    sections: dict[CVSection, list[str]] = {}
    current: CVSection | None = None

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        detected = match_section(stripped)
        if detected is not None and len(stripped) <= 40:
            current = detected
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(stripped)

    return sections


def _first_line(lines: list[str]) -> str | None:
    """Devuelve la primera línea no vacía o ``None``."""
    for line in lines:
        if line.strip():
            return line.strip()
    return None
