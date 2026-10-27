"""Utilidades de extracción de contacto y enlaces para el pipeline de ingesta."""

from __future__ import annotations

import re

__all__ = [
    "EMAIL_RE",
    "PHONE_RE",
    "LINKEDIN_RE",
    "extract_emails",
    "extract_links",
    "extract_phone",
]

# Correo electrónico razonable.
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Teléfono: acepta formatos internacionales y locales habituales.
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}")

# URL http/https o www.
_URL_SCHEME_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"']+")

# Dominio "desnudo" con ruta, p. ej. "linkedin.com/in/..." o "github.com/user".
# Exige una ruta ("/") y un TLD conocido para reducir falsos positivos.
_URL_BARE_RE = re.compile(
    r"(?:[A-Za-z0-9-]+\.)+(?:com|io|dev|net|org|me|co|es|edu|gov|info|app|ai|tech)/[^\s<>\"']+",
    re.IGNORECASE,
)

# Enlaces de LinkedIn detectados en el texto del documento.
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[A-Za-z0-9\-_/%.]+", re.IGNORECASE)


def extract_emails(text: str) -> list[str]:
    """Extrae y deduplica correos electrónicos del texto."""
    return list(dict.fromkeys(EMAIL_RE.findall(text)))


def extract_links(text: str) -> list[str]:
    """Extrae URLs del texto, normalizadas y sin duplicados.

    Reconoce tanto URLs completas (``https://`` o ``www.``) como dominios
    desnudos con ruta (``linkedin.com/in/...``). Los enlaces sin esquema se
    promueven a ``https://`` para cumplir con el esquema ``HttpUrl``.
    """
    links: list[str] = []

    def _add(raw: str) -> None:
        url = raw.rstrip(".,;:)")
        if not url.lower().startswith(("http://", "https://")):
            url = f"https://{url.lstrip('/')}"
        if url not in links:
            links.append(url)

    for raw in _URL_SCHEME_RE.findall(text):
        _add(raw)
    for raw in _URL_BARE_RE.findall(text):
        _add(raw)

    return links


def extract_phone(text: str) -> str | None:
    """Intenta extraer el primer número de teléfono plausible del texto.

    Se evitan falsos positivos como años o códigos postales exigiendo al menos
    7 dígitos en total.
    """
    for match in PHONE_RE.finditer(text):
        candidate = match.group(0)
        digits = re.sub(r"\D", "", candidate)
        if len(digits) >= 7:
            return candidate.strip()
    return None
