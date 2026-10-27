"""Parsers heurísticos para convertir líneas de texto en objetos del modelo.

Cada función recibe las líneas de una sección ya segmentada y devuelve los
objetos correspondientes de :mod:`imcv.models`. Se apoyan en el normalizador de
fechas multilingüe de :mod:`imcv.dates`.
"""

from __future__ import annotations

import re

from imcv.dates import is_present_marker, parse_flexible_date
from imcv.ingestion.utils import extract_emails, extract_links, extract_phone
from imcv.models import (
    Certification,
    ContactInfo,
    Education,
    Experience,
    Language,
    ProficiencyLevel,
    Project,
    Skill,
)

__all__ = [
    "parse_certifications",
    "parse_contact",
    "parse_education",
    "parse_experience",
    "parse_languages",
    "parse_projects",
    "parse_skills",
]

# Token de fecha: "Jan 2020", "mayo 2019", "2020", "2020-05".
_DATE_TOKEN = (
    r"(?:[A-Za-záéíóúñ]{3,9}\.?\s+de\s+|[A-Za-záéíóúñ]{3,9}\.?\s+)?\d{4}(?:\s*[-/]\s*\d{1,2})?"
)

# Rango de fechas completo en una línea, p. ej. "Jan 2020 - Present" o
# "2019 – 2022" o "mayo 2018 to agosto 2020".
_DATE_RANGE_RE = re.compile(
    rf"^\s*({_DATE_TOKEN})\s*(?:[-–—]|\bto\b)\s*"
    rf"({_DATE_TOKEN}|present|presente|actualidad|current|hoy)\s*$",
    re.IGNORECASE,
)

# Viñetas habituales.
_BULLET_RE = re.compile(r"^\s*[-–—•*·▪◦]\s*")

# Nivel de idioma en español e inglés.
_LANGUAGE_LEVELS: dict[str, ProficiencyLevel] = {
    "native": ProficiencyLevel.NATIVE,
    "nativo": ProficiencyLevel.NATIVE,
    "nativa": ProficiencyLevel.NATIVE,
    "bilingual": ProficiencyLevel.NATIVE,
    "bilingüe": ProficiencyLevel.NATIVE,
    "native speaker": ProficiencyLevel.NATIVE,
    "fluent": ProficiencyLevel.ADVANCED,
    "fluido": ProficiencyLevel.ADVANCED,
    "avanzado": ProficiencyLevel.ADVANCED,
    "avanzada": ProficiencyLevel.ADVANCED,
    "advanced": ProficiencyLevel.ADVANCED,
    "intermediate": ProficiencyLevel.INTERMEDIATE,
    "intermedio": ProficiencyLevel.INTERMEDIATE,
    "intermedia": ProficiencyLevel.INTERMEDIATE,
    "basic": ProficiencyLevel.BASIC,
    "basico": ProficiencyLevel.BASIC,
    "básico": ProficiencyLevel.BASIC,
    "basica": ProficiencyLevel.BASIC,
    "básica": ProficiencyLevel.BASIC,
}


def _strip_bullet(line: str) -> str:
    """Elimina la viñeta inicial de una línea si la tiene."""
    return _BULLET_RE.sub("", line).strip()


def parse_date_range(line: str) -> tuple[str, str | None, bool] | None:
    """Interpreta una línea como rango de fechas.

    Returns:
        ``(start, end, is_current)`` donde ``end`` puede ser ``None`` cuando el
        rango indica actualidad, o ``None`` si la línea no es un rango de fechas.
    """
    match = _DATE_RANGE_RE.match(line)
    if not match:
        return None

    start_raw, end_raw = match.group(1), match.group(2)
    start = parse_flexible_date(start_raw)

    if is_present_marker(end_raw):
        return (start.isoformat(), None, True)

    end = parse_flexible_date(end_raw)
    return (start.isoformat(), end.isoformat() if end else None, False)


def _looks_like_date_range(line: str) -> bool:
    """Indica si una línea parece un rango de fechas (sin fallar al parsear)."""
    try:
        return parse_date_range(line) is not None
    except ValueError:
        return False


def parse_experience(lines: list[str]) -> list[Experience]:
    """Parsea la sección de experiencia laboral.

    Cada entrada se delimita por una línea de rango de fechas. Las líneas justo
    antes (hasta dos) forman la cabecera ``role`` y ``company``; las posteriores
    hasta la cabecera siguiente forman la descripción y los logros.
    """
    date_positions = [i for i, line in enumerate(lines) if _looks_like_date_range(line)]
    experiences: list[Experience] = []

    for idx, date_idx in enumerate(date_positions):
        header_start = _header_start(lines, date_positions, idx)
        header_lines = [lines[i] for i in range(header_start, date_idx) if lines[i].strip()]

        role = (
            header_lines[-2]
            if len(header_lines) >= 2
            else (header_lines[0] if header_lines else "")
        )
        company = header_lines[-1] if len(header_lines) >= 2 else ""
        if not role:
            continue

        start, end, is_current = parse_date_range(lines[date_idx])  # type: ignore[misc]

        body_end = _body_end(lines, date_positions, idx)
        body_lines = [lines[i] for i in range(date_idx + 1, body_end) if lines[i].strip()]
        description, achievements = _split_body(body_lines)

        experiences.append(
            Experience(
                role=role,
                company=company or role,
                start_date=start,
                end_date=end,
                is_current=is_current,
                description=description,
                achievements=achievements,
            )
        )

    return experiences


def _header_start(lines: list[str], date_positions: list[int], idx: int) -> int:
    """Índice donde comienza la cabecera (role/company) de la entrada ``idx``.

    Retrocede desde la línea de fechas hasta 2 líneas no vacías, sin cruzar la
    fecha de la entrada anterior.
    """
    date_idx = date_positions[idx]
    lower_bound = date_positions[idx - 1] + 1 if idx > 0 else 0
    count = 0
    start = date_idx
    for i in range(date_idx - 1, lower_bound - 1, -1):
        if lines[i].strip():
            count += 1
            start = i
            if count == 2:
                break
    return start


def _body_end(lines: list[str], date_positions: list[int], idx: int) -> int:
    """Índice donde termina el cuerpo de la entrada ``idx``.

    El cuerpo termina donde comienza la cabecera de la siguiente entrada (las
    últimas 1-2 líneas no vacías antes de la siguiente fecha).
    """
    if idx + 1 >= len(date_positions):
        return len(lines)
    next_date = date_positions[idx + 1]
    current_date = date_positions[idx]
    count = 0
    for i in range(next_date - 1, current_date, -1):
        if lines[i].strip():
            count += 1
            if count == 2:
                return i
    return next_date


def _split_body(body_lines: list[str]) -> tuple[str | None, list[str]]:
    """Separa el cuerpo de una experiencia en ``description`` y ``achievements``.

    - Si hay líneas con viñeta explícita, esas son los logros y una línea inicial
      sin viñeta puede ser la descripción.
    - Sin viñetas explícitas, varias líneas se consideran logros y una única
      línea se trata como descripción.
    """
    stripped = [_strip_bullet(line) for line in body_lines if _strip_bullet(line)]
    if not stripped:
        return None, []

    explicit = [
        _strip_bullet(line) for line in body_lines if _is_bullet(line) and _strip_bullet(line)
    ]
    if explicit:
        lead = [line for line in body_lines if not _is_bullet(line) and line.strip()]
        description = _strip_bullet(lead[0]) if lead else None
        return description, explicit

    # Sin viñetas explícitas (se pierden al extraer de PDF/DOCX), en un CV el
    # contenido bajo un puesto son logros: se tratan todas las líneas como tales.
    return None, stripped


def _is_bullet(line: str) -> bool:
    """Indica si una línea comienza con viñeta."""
    return bool(_BULLET_RE.match(line))


def parse_education(lines: list[str]) -> list[Education]:
    """Parsea la sección de formación académica.

    Sigue la misma estrategia que experiencia: las entradas se delimitan por
    rangos de fechas y la cabecera contiene ``degree`` e ``institution``.
    """
    date_positions = [i for i, line in enumerate(lines) if _looks_like_date_range(line)]
    educations: list[Education] = []

    for idx, date_idx in enumerate(date_positions):
        header_start = _header_start(lines, date_positions, idx)
        header_lines = [lines[i] for i in range(header_start, date_idx) if lines[i].strip()]

        degree = (
            header_lines[-2]
            if len(header_lines) >= 2
            else (header_lines[0] if header_lines else "")
        )
        institution = header_lines[-1] if len(header_lines) >= 2 else ""
        if not degree:
            continue

        start, end, _ = parse_date_range(lines[date_idx])  # type: ignore[misc]

        body_end = _body_end(lines, date_positions, idx)
        body_lines = [lines[i] for i in range(date_idx + 1, body_end) if lines[i].strip()]
        description = " ".join(_strip_bullet(line) for line in body_lines) or None

        educations.append(
            Education(
                degree=degree,
                institution=institution or degree,
                start_date=start,
                end_date=end,
                description=description,
            )
        )

    return educations


def parse_skills(lines: list[str]) -> list[Skill]:
    """Parsea la sección de habilidades.

    Soporta habilidades separadas por comas, por saltos de línea o con viñeta.
    """
    skills: list[Skill] = []
    seen: set[str] = set()

    for line in lines:
        # Separar por comas, punto y coma o viñetas.
        parts = re.split(r"[,;•·▪◦]|\s-\s", line)
        for part in parts:
            name = _strip_bullet(part).strip()
            if name and name.lower() not in seen:
                seen.add(name.lower())
                skills.append(Skill(name=name))

    return skills


def parse_languages(lines: list[str]) -> list[Language]:
    """Parsea la sección de idiomas.

    Espera ``"Idioma - Nivel"`` o simplemente ``"Idioma"``.
    """
    languages: list[Language] = []

    for line in lines:
        text = _strip_bullet(line)
        if not text:
            continue
        # Separar por guiones que actúen como "nombre - nivel".
        parts = re.split(r"\s+[-–—]\s+", text, maxsplit=1)
        name = parts[0].strip()
        level = None
        if len(parts) == 2:
            level = _LANGUAGE_LEVELS.get(parts[1].strip().lower())
        if name:
            languages.append(Language(name=name, proficiency=level))

    return languages


def parse_certifications(lines: list[str]) -> list[Certification]:
    """Parsea la sección de certificaciones.

    Cada línea se considera una certificación; si contiene una fecha se extrae
    como ``issue_date`` y una URL como ``credential_url``.
    """
    certifications: list[Certification] = []

    for line in lines:
        text = _strip_bullet(line)
        if not text:
            continue
        urls = extract_links(text)
        # Eliminar la fecha y la URL del texto para obtener el nombre.
        cleaned = text
        issue_date = None
        date_match = re.search(_DATE_TOKEN, text)
        if date_match:
            try:
                issue_date = parse_flexible_date(date_match.group(0))
                cleaned = cleaned.replace(date_match.group(0), "")
            except ValueError:
                pass
        cleaned = re.sub(r"https?://\S+|www\.\S+", "", cleaned).strip(" -,;·")
        name = cleaned.strip() or text
        certifications.append(
            Certification(
                name=name,
                issue_date=issue_date,
                credential_url=urls[0] if urls else None,
            )
        )

    return certifications


def parse_projects(lines: list[str]) -> list[Project]:
    """Parsea la sección de proyectos.

    Cada línea se considera un proyecto; si contiene una URL se extrae como
    ``url``.
    """
    projects: list[Project] = []

    for line in lines:
        text = _strip_bullet(line)
        if not text:
            continue
        urls = extract_links(text)
        name = re.sub(r"https?://\S+|www\.\S+", "", text).strip(" -,;·") or text
        projects.append(
            Project(
                name=name,
                url=urls[0] if urls else None,
            )
        )

    return projects


def parse_contact(lead_lines: list[str], full_text: str) -> ContactInfo:
    """Extrae los datos de contacto a partir de las líneas iniciales y el texto.

    ``lead_lines`` son las primeras líneas significativas del documento (donde
    normalmente aparecen nombre y titular). De ``full_text`` se extraen correo,
    teléfono y enlaces con utilidades robustas.

    Raises:
        ValueError: Si no se puede determinar un nombre completo.
    """
    # El nombre suele ser la primera línea que no es encabezado ni dato obvio.
    full_name = ""
    headline = ""
    for line in lead_lines:
        candidate = line.strip()
        if not candidate:
            continue
        # Saltar líneas que son claramente datos de contacto o encabezados.
        if "@" in candidate or candidate.lower().startswith(("http", "www.")):
            continue
        if not full_name:
            full_name = candidate
        elif not headline:
            headline = candidate
            break

    if not full_name:
        raise ValueError("No se pudo determinar el nombre completo del titular del CV")

    emails = extract_emails(full_text)
    links = extract_links(full_text)

    # Ubicación: se busca una línea con formato "Ciudad, País" entre las iniciales.
    location = None
    for line in lead_lines:
        candidate = line.strip()
        if "," in candidate and "@" not in candidate and len(candidate.split(",")) == 2:
            first, second = (p.strip() for p in candidate.split(","))
            if first and second and not first.lower().startswith(("http", "www")):
                location = candidate
                break

    return ContactInfo(
        full_name=full_name,
        headline=headline or None,
        email=emails[0] if emails else None,
        phone=extract_phone(full_text),
        location=location,
        links=links,
    )
