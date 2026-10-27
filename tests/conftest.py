"""Configuración compartida de fixtures para la suite de pruebas."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.fixtures.build import build_all


@pytest.fixture(scope="session")
def fixtures_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Construye todas las fixtures de documentos en un directorio temporal.

    Se genera una única vez por sesión para eficiencia. Todos los archivos se
    crean de forma local (modo offline)."""
    directory = tmp_path_factory.mktemp("fixtures")
    build_all(directory)
    return directory


@pytest.fixture(scope="session")
def linkedin_pdf(fixtures_dir: Path) -> Path:
    """Ruta al PDF de muestra exportado de LinkedIn."""
    return fixtures_dir / "sample_linkedin.pdf"


@pytest.fixture(scope="session")
def generic_pdf(fixtures_dir: Path) -> Path:
    """Ruta al PDF genérico de muestra."""
    return fixtures_dir / "sample_generic.pdf"


@pytest.fixture(scope="session")
def empty_pdf(fixtures_dir: Path) -> Path:
    """Ruta al PDF válido pero vacío."""
    return fixtures_dir / "sample_empty.pdf"


@pytest.fixture(scope="session")
def corrupt_pdf(fixtures_dir: Path) -> Path:
    """Ruta al archivo corrupto con extensión ``.pdf``."""
    return fixtures_dir / "sample_corrupt.pdf"


@pytest.fixture(scope="session")
def docx_path(fixtures_dir: Path) -> Path:
    """Ruta al documento Word de muestra."""
    return fixtures_dir / "sample_resume.docx"
