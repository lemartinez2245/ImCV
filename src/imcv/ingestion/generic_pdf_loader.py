"""Cargador de PDF genérico de CV.

Extrae el texto con ``pymupdf``, segmenta las secciones con el vocabulario
multilingüe y las convierte en un :class:`~imcv.models.CVModel` validado.
"""

from __future__ import annotations

from pathlib import Path

from imcv.exceptions import ExtractionError, ValidationError
from imcv.ingestion.base import DocumentLoader
from imcv.ingestion.pdf_parser import extract_lines, segment_sections
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
from imcv.sections import CVSection

__all__ = ["GenericPdfLoader"]


class GenericPdfLoader(DocumentLoader):
    """Carga un CV desde un PDF de formato estándar."""

    def load(self, path: Path) -> CVModel:
        path = Path(path)

        doc_lines = extract_lines(path)
        if not doc_lines.full_text.strip():
            raise ExtractionError(f"No se pudo extraer texto del PDF: {path}")

        sections = segment_sections(doc_lines)

        # Líneas iniciales del documento para nombre/titular (antes de cualquier
        # encabezado de sección).
        lead_lines = _lead_lines(doc_lines)

        try:
            contact = parse_contact(lead_lines, doc_lines.full_text)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        cv = CVModel(
            contact=contact,
            summary=_first_line(sections.get(CVSection.SUMMARY, [])),
            experience=parse_experience(sections.get(CVSection.EXPERIENCE, [])),
            education=parse_education(sections.get(CVSection.EDUCATION, [])),
            skills=parse_skills(sections.get(CVSection.SKILLS, [])),
            languages=parse_languages(sections.get(CVSection.LANGUAGES, [])),
            certifications=parse_certifications(sections.get(CVSection.CERTIFICATIONS, [])),
            projects=parse_projects(sections.get(CVSection.PROJECTS, [])),
        )
        return cv


def _first_line(lines: list[str]) -> str | None:
    """Devuelve la primera línea no vacía o ``None``."""
    for line in lines:
        if line.strip():
            return line.strip()
    return None


def _lead_lines(doc_lines: object) -> list[str]:
    """Devuelve las primeras líneas significativas del documento.

    Útiles para localizar el nombre y el titular profesional, que suelen estar
    en el encabezado antes de cualquier sección.
    """
    lines = getattr(doc_lines, "non_empty_lines", [])
    return lines[:6]
