"""Detección multilingüe de secciones de un CV.

Los documentos de entrada pueden estar en español o inglés. Este módulo define
un vocabulario canónico de secciones y sus sinónimos, de modo que el pipeline de
ingesta pueda segmentar el documento sea cual sea el idioma.
"""

from __future__ import annotations

from enum import StrEnum

__all__ = ["SECTION_KEYWORDS", "CVSection", "match_section"]


class CVSection(StrEnum):
    """Secciones canónicas de un CV."""

    CONTACT = "contact"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    LANGUAGES = "languages"
    CERTIFICATIONS = "certifications"
    PROJECTS = "projects"
    REFERENCES = "references"


# Cada sección canónica tiene una lista de sinónimos (en minúsculas) que se
# comparan contra el encabezado detectado en el documento.
SECTION_KEYWORDS: dict[CVSection, tuple[str, ...]] = {
    CVSection.CONTACT: (
        "contact",
        "contacto",
        "personal info",
        "personal information",
        "datos personales",
        "información personal",
        "perfil",
        "profile",
        "about",
        "acerca de",
    ),
    CVSection.SUMMARY: (
        "summary",
        "resumen",
        "professional summary",
        "perfil profesional",
        "about me",
        "sobre mí",
        "about me.",
        "acerca de mí",
        "description",
        "descripción",
        "objetivo",
        "objective",
        "professional profile",
    ),
    CVSection.EXPERIENCE: (
        "experience",
        "experiencia",
        "work experience",
        "experiencia laboral",
        "work history",
        "historial laboral",
        "employment",
        "empleo",
        "professional experience",
        "experiencia profesional",
        "experience history",
        "trayectoria",
        "career",
        "trayectoria profesional",
    ),
    CVSection.EDUCATION: (
        "education",
        "educación",
        "formación",
        "academic background",
        "formación académica",
        "education and training",
        "educación y formación",
        "academics",
        "studies",
        "estudios",
        "qualifications",
        "cualificaciones",
    ),
    CVSection.SKILLS: (
        "skills",
        "habilidades",
        "aptitudes",
        "top skills",
        "aptitudes principales",
        "competencias",
        "core competencies",
        "technical skills",
        "habilidades técnicas",
        "skills & abilities",
        "habilidades y aptitudes",
        "abilities",
        "capabilities",
    ),
    CVSection.LANGUAGES: (
        "languages",
        "idiomas",
        "language",
        "idioma",
        "language skills",
        "competencias lingüísticas",
    ),
    CVSection.CERTIFICATIONS: (
        "certifications",
        "certificaciones",
        "licenses & certifications",
        "licencias y certificaciones",
        "courses",
        "cursos",
        "licenses",
        "licencias",
        "certificates",
        "certificados",
    ),
    CVSection.PROJECTS: (
        "projects",
        "proyectos",
        "personal projects",
        "proyectos personales",
        "selected projects",
        "proyectos destacados",
    ),
    CVSection.REFERENCES: (
        "references",
        "referencias",
        "recommendations",
        "recomendaciones",
    ),
}


def _normalize_header(header: str) -> str:
    """Normaliza un encabezado para compararlo con el vocabulario."""
    return " ".join(header.strip().lower().split())


def match_section(header: str) -> CVSection | None:
    """Intenta asociar un encabezado de texto a una :class:`CVSection`.

    El encabezado se normaliza (minúsculas, sin puntuación final) y se busca
    coincidencia exacta o por contenido contra el vocabulario multilingüe.

    Returns:
        La sección detectada o ``None`` si el encabezado no corresponde a
        ninguna sección conocida.
    """
    normalized = _normalize_header(header).rstrip(":.·•-–—")
    if not normalized:
        return None

    for section, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            if normalized == keyword:
                return section

    # Coincidencia parcial: el encabezado contiene la palabra clave.
    for section, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized or normalized in keyword:
                return section

    return None
