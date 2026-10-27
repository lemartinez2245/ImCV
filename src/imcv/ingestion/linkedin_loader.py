"""Cargador de PDF exportado desde LinkedIn.

Reutiliza la lógica del :class:`~imcv.ingestion.generic_pdf_loader.GenericPdfLoader`
ya que el PDF de LinkedIn comparte la estructura de secciones (aprovechando el
vocabulario multilingüe). Se especializa en la extracción del encabezado de
contacto típico de la exportación de LinkedIn.
"""

from __future__ import annotations

from pathlib import Path

from imcv.exceptions import ExtractionError, ValidationError
from imcv.ingestion.generic_pdf_loader import GenericPdfLoader, _first_line, _lead_lines
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

__all__ = ["LinkedInPdfLoader"]


class LinkedInPdfLoader(GenericPdfLoader):
    """Carga un CV desde un PDF exportado del perfil de LinkedIn.

    La exportación de LinkedIn prioriza el formato de dos columnas o de sección
    lateral con contacto/aptitudes y cuerpo con experiencia/educación. Al ser
    compatible con la segmentación multilingüe, la lógica principal se hereda del
    cargador genérico.
    """

    def load(self, path: Path) -> CVModel:
        path = Path(path)

        doc_lines = extract_lines(path)
        if not doc_lines.full_text.strip():
            raise ExtractionError(f"No se pudo extraer texto del PDF de LinkedIn: {path}")

        sections = segment_sections(doc_lines)
        lead_lines = _lead_lines(doc_lines)

        try:
            contact = parse_contact(lead_lines, doc_lines.full_text)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        # En la exportación de LinkedIn el "resumen" suele aparecer tras el
        # nombre; si no hay sección dedicada, se omite.
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
