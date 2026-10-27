"""Interfaz común y factoría de cargadores de documentos."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from imcv.exceptions import UnsupportedFormatError
from imcv.models import CVModel

__all__ = ["DocumentLoader", "get_loader"]

# Extensiones que reconocemos como PDF.
_PDF_SUFFIXES = {".pdf"}
# Extensiones que reconocemos como Word.
_DOCX_SUFFIXES = {".docx", ".doc"}


class DocumentLoader(ABC):
    """Contrato para cargar y normalizar un CV desde un archivo.

    Cada implementación se encarga de leer un formato concreto y devolver un
    :class:`~imcv.models.CVModel` ya validado. Si el archivo no puede procesarse
    se lanza una excepción de la jerarquía ``ImCVError``.
    """

    @abstractmethod
    def load(self, path: Path) -> CVModel:
        """Extrae y normaliza el contenido del archivo a un ``CVModel`` validado."""


def get_loader(path: Path) -> DocumentLoader:
    """Devuelve el cargador adecuado para ``path`` según su extensión.

    Para los PDF se inspecciona además el contenido para distinguir entre un
    PDF exportado de LinkedIn y un PDF genérico.

    Raises:
        UnsupportedFormatError: Si la extensión no está soportada.
        FileNotFoundError: Si el archivo no existe.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"El archivo no existe: {path}")

    suffix = path.suffix.lower()

    if suffix in _PDF_SUFFIXES:
        # Import diferido para no cargar librerías pesadas innecesariamente.
        from imcv.ingestion.generic_pdf_loader import GenericPdfLoader
        from imcv.ingestion.linkedin_loader import LinkedInPdfLoader

        if _looks_like_linkedin(path):
            return LinkedInPdfLoader()
        return GenericPdfLoader()

    if suffix in _DOCX_SUFFIXES:
        from imcv.ingestion.docx_loader import DocxLoader

        return DocxLoader()

    raise UnsupportedFormatError(
        f"Formato no soportado: {suffix or '(sin extensión)'!s}. "
        "Formatos admitidos: .pdf, .docx, .doc"
    )


def _looks_like_linkedin(path: Path) -> bool:
    """Detecta si un PDF parece haber sido exportado desde LinkedIn.

    Busca la presencia de enlaces de perfil de LinkedIn o de términos típicos
    de la exportación de la red social. Es una heurística local y barata.
    """
    try:
        import pymupdf

        with pymupdf.open(path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
                if len(text) > 50_000:  # basta con el principio del documento
                    break
    except Exception:  # noqa: BLE001 - si falla, asumimos PDF genérico
        return False

    lowered = text.lower()
    return "linkedin.com/in/" in lowered or "linkedin.com" in lowered
