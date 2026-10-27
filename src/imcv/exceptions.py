"""Jerarquía de excepciones personalizadas de ImCV.

Todos los errores de dominio de ImCV derivan de :class:`ImCVError`, lo que
permite capturar cualquier fallo del paquete con un único ``except``.
"""

from __future__ import annotations


class ImCVError(Exception):
    """Error base de ImCV."""


class UnsupportedFormatError(ImCVError):
    """Formato o extensión de archivo no soportado."""


class ExtractionError(ImCVError):
    """No se pudo extraer contenido legible del documento."""


class ValidationError(ImCVError):
    """El contenido extraído no cumple el esquema ``CVModel``."""
