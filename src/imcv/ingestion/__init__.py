"""Pipeline de ingesta de documentos de ImCV.

Expone la interfaz :class:`~imcv.ingestion.base.DocumentLoader` y la factoría
:func:`~imcv.ingestion.base.get_loader` para convertir documentos de entrada
(PDF de LinkedIn, PDF genérico o Word) en un :class:`~imcv.models.CVModel`.
"""

from imcv.ingestion.base import DocumentLoader, get_loader
from imcv.ingestion.docx_loader import DocxLoader
from imcv.ingestion.generic_pdf_loader import GenericPdfLoader
from imcv.ingestion.linkedin_loader import LinkedInPdfLoader

__all__ = [
    "DocumentLoader",
    "DocxLoader",
    "GenericPdfLoader",
    "LinkedInPdfLoader",
    "get_loader",
]
