"""Análisis compartido de PDFs para el pipeline de ingesta.

Extrae el texto de un PDF preservando el orden de lectura y lo segmenta en las
secciones canónicas del CV usando el vocabulario multilingüe de
:mod:`imcv.sections`. Es la base común de los cargadores de PDF.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from imcv.exceptions import ExtractionError
from imcv.sections import CVSection, match_section

__all__ = [
    "DocumentLines",
    "extract_lines",
    "segment_sections",
]

# Caracteres de viñeta que algunos renderizadores (p. ej. WeasyPrint) emiten como
# glifos independientes en lugar de prefijarlos al texto.
_BULLET_ONLY_RE = re.compile(r"^[\s•·▪◦*–—-]+$")


@dataclass
class DocumentLines:
    """Texto extraído de un PDF, organizado en líneas limpias."""

    lines: list[str] = field(default_factory=list)
    full_text: str = ""

    @property
    def non_empty_lines(self) -> list[str]:
        """Solo las líneas con contenido, para el análisis de secciones."""
        return [line for line in self.lines if line.strip()]


def extract_lines(path: Path) -> DocumentLines:
    """Extrae el texto de un PDF en líneas, preservando el orden de lectura.

    Se unen los ``span`` de cada línea y se normalizan los espacios múltiples.

    Raises:
        ExtractionError: Si el PDF no puede abrirse o leerse.
    """
    lines: list[str] = []
    try:
        with pymupdf.open(path) as doc:
            for page in doc:
                # "dict" conserva la estructura de bloques, párrafos y líneas.
                page_dict = page.get_text("dict")
                for block in page_dict.get("blocks", []):
                    if block.get("type") != 0:  # 0 = texto; ignorar imágenes
                        continue
                    for para in block.get("lines", []):
                        span_text = "".join(span.get("text", "") for span in para.get("spans", []))
                        span_text = re.sub(r"\s+", " ", span_text).strip()
                        # Descartar líneas que solo son viñetas (glifos sueltos).
                        if span_text and _BULLET_ONLY_RE.match(span_text):
                            continue
                        lines.append(span_text)
    except Exception as exc:  # noqa: BLE001 - pymupdf lanza excepciones variadas
        raise ExtractionError(f"No se pudo leer el PDF: {path}") from exc

    # Unimos líneas vacías consecutivas para no inflar la lista.
    compact: list[str] = []
    for line in lines:
        if line or (compact and compact[-1]):
            compact.append(line)
    # Quitamos una posible línea vacía final.
    while compact and not compact[-1]:
        compact.pop()

    full_text = "\n".join(compact)
    return DocumentLines(lines=compact, full_text=full_text)


def segment_sections(doc_lines: DocumentLines) -> dict[CVSection, list[str]]:
    """Divide el documento en secciones canónicas.

    Recorre las líneas detectando encabezados de sección (usando
    :func:`~imcv.sections.match_section`) y agrupa el contenido que sigue a cada
    encabezado hasta el siguiente.

    Returns:
        Un mapping de sección canónica a sus líneas de contenido.
    """
    sections: dict[CVSection, list[str]] = {}
    current: CVSection | None = None

    for raw_line in doc_lines.non_empty_lines:
        detected = match_section(raw_line)
        # Un encabezado es una línea corta que coincide con una sección.
        if detected is not None and len(raw_line.strip()) <= 40:
            current = detected
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(raw_line)

    return sections
