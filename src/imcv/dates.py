"""Normalización de fechas flexibles para ImCV.

Un CV real contiene fechas en multitud de formatos: ``"2023"``, ``"2023-05"``,
``"2023-05-15"``, ``"May 2021"``, ``"mayo 2020"``, ``"January 2019"``, etc.
Este módulo ofrece un parser tolerante que las convierte a :class:`datetime.date`.

Cuando no se conoce el mes o el día se asume ``1``, de modo que la fecha sigue
siendo utilizable para ordenamiento cronológico.
"""

from __future__ import annotations

import re
from datetime import date, datetime

__all__ = [
    "PRESENT_MARKERS",
    "is_present_marker",
    "parse_flexible_date",
]

# Palabras que indican "trabajo en curso / actualidad".
PRESENT_MARKERS: frozenset[str] = frozenset(
    {
        "present",
        "current",
        "presente",
        "actualidad",
        "actual",
        "hoy",
        "today",
        "now",
        "en curso",
        "to date",
        "to-date",
        "presente - hoy",
    }
)

# Meses en inglés (minúsculas, sin abreviaturas ambiguas).
_MONTHS_EN: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

# Meses en español (minúsculas, sin abreviaturas ambiguas).
_MONTHS_ES: dict[str, int] = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
    "ene": 1,
    "feb": 2,
    "mar": 3,
    "abr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "sep": 9,
    "sept": 9,
    "set": 9,
    "oct": 10,
    "nov": 11,
    "dic": 12,
}

_MONTHS: dict[str, int] = {**_MONTHS_EN, **_MONTHS_ES}

# "2023-05-15", "2023-05", "2023"
_ISO_RE = re.compile(r"^(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?$")

# "May 2021", "mayo 2020", "May de 2021", "mayo de 2020"
_MONTH_YEAR_RE = re.compile(
    r"^([a-záéíóúñ]+)\s+(?:de\s+|del\s+)?(\d{4})$",
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    """Normaliza un string para su comparación: minúsculas y sin comas."""
    return text.strip().strip(",").strip().lower()


def is_present_marker(value: object) -> bool:
    """Indica si ``value`` representa la idea de "actualidad / en curso".

    Se usa para marcar ``end_date = None`` junto a ``is_current = True``.
    """
    if value is None:
        return False
    if isinstance(value, str):
        return _clean(value) in PRESENT_MARKERS
    return False


def parse_flexible_date(value: object) -> date | None:
    """Convierte ``value`` a :class:`datetime.date` de forma tolerante.

    Acepta ``date``, ``datetime``, ``int``/``float`` (año) y ``str`` con los
    formatos ISO (``YYYY``, ``YYYY-MM``, ``YYYY-MM-DD``) o con nombre de mes
    en inglés o español (``"May 2021"``, ``"mayo de 2020"``).

    Retorna:
        La fecha resultante o ``None`` si ``value`` es ``None``.

    Raises:
        ValueError: Si ``value`` no puede interpretarse como fecha.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, bool):
        # bool es subclase de int; no debe tratarse como año.
        raise ValueError(f"No se puede interpretar {value!r} como fecha")
    if isinstance(value, int | float):
        year = int(value)
        _validate_year(year, value)
        return date(year, 1, 1)

    if not isinstance(value, str):
        raise ValueError(f"Tipo no soportado para fecha: {type(value).__name__}")

    text = value.strip()
    if not text:
        raise ValueError("Cadena de fecha vacía")

    # Formato ISO: 2023, 2023-05, 2023-05-15
    iso = _ISO_RE.match(text)
    if iso:
        year = int(iso.group(1))
        _validate_year(year, value)
        month = int(iso.group(2)) if iso.group(2) else 1
        day = int(iso.group(3)) if iso.group(3) else 1
        return _build_date(year, month, day, value)

    # Formato con nombre de mes: "May 2021", "mayo de 2020"
    month_year = _MONTH_YEAR_RE.match(text)
    if month_year:
        month_name = _clean(month_year.group(1))
        month = _MONTHS.get(month_name)
        if month is None:
            raise ValueError(f"Mes no reconocido en la fecha: {value!r}")
        year = int(month_year.group(2))
        _validate_year(year, value)
        return date(year, month, 1)

    raise ValueError(f"Formato de fecha no reconocido: {value!r}")


def _validate_year(year: int, original: object) -> None:
    """Valida que un año sea razonable para un CV (1900..2100)."""
    if not 1900 <= year <= 2100:
        raise ValueError(f"Año fuera de rango razonable en la fecha: {original!r}")


def _build_date(year: int, month: int, day: int, original: object) -> date:
    """Construye una fecha validando que mes y día sean correctos."""
    if not 1 <= month <= 12:
        raise ValueError(f"Mes inválido en la fecha: {original!r}")
    if not 1 <= day <= 31:
        raise ValueError(f"Día inválido en la fecha: {original!r}")
    try:
        return date(year, month, day)
    except ValueError as exc:  # p. ej. 30 de febrero
        raise ValueError(f"Fecha inválida: {original!r}") from exc
