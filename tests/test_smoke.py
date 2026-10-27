"""Pruebas de humo para verificar la configuración del entorno."""

from importlib.metadata import version


def test_imcv_importable() -> None:
    import imcv

    assert callable(imcv.main)


def test_core_dependencies_installed() -> None:
    for pkg in (
        "langgraph",
        "langchain-core",
        "langchain-ollama",
        "pydantic",
        "pymupdf",
        "python-docx",
        "docxtpl",
        "weasyprint",
        "fastapi",
        "uvicorn",
    ):
        assert version(pkg), f"{pkg} no está instalado"


def test_pydantic_v2() -> None:
    from pydantic import BaseModel

    class _Sample(BaseModel):
        name: str

    assert _Sample(name="ImCV").name == "ImCV"
