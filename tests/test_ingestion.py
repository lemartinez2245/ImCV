"""Pruebas del pipeline de ingesta de documentos."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from imcv.exceptions import ExtractionError, UnsupportedFormatError
from imcv.ingestion import (
    DocxLoader,
    GenericPdfLoader,
    LinkedInPdfLoader,
    get_loader,
)
from imcv.models import CVModel


class TestGetLoader:
    """Pruebas de la factoría de cargadores."""

    def test_routes_linkedin_pdf(self, linkedin_pdf: Path) -> None:
        loader = get_loader(linkedin_pdf)
        assert isinstance(loader, LinkedInPdfLoader)

    def test_routes_generic_pdf(self, generic_pdf: Path) -> None:
        loader = get_loader(generic_pdf)
        assert isinstance(loader, GenericPdfLoader)

    def test_routes_docx(self, docx_path: Path) -> None:
        loader = get_loader(docx_path)
        assert isinstance(loader, DocxLoader)

    def test_unsupported_extension(self, tmp_path: Path) -> None:
        bad = tmp_path / "cv.txt"
        bad.write_text("contenido")
        with pytest.raises(UnsupportedFormatError):
            get_loader(bad)

    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            get_loader(tmp_path / "no-existe.pdf")


class TestLinkedInLoader:
    """Pruebas del cargador de PDF exportado de LinkedIn."""

    def test_loads_valid_cv(self, linkedin_pdf: Path) -> None:
        cv = get_loader(linkedin_pdf).load(linkedin_pdf)
        assert isinstance(cv, CVModel)
        assert cv.contact.full_name == "Ana García López"
        assert cv.contact.headline == "Ingeniera de Software Senior"
        assert cv.contact.email == "ana.garcia@example.com"
        assert cv.contact.location == "Madrid, España"
        assert len(cv.experience) == 2
        assert len(cv.education) == 1
        assert len(cv.skills) >= 4
        assert len(cv.languages) == 2

    def test_experience_details(self, linkedin_pdf: Path) -> None:
        cv = get_loader(linkedin_pdf).load(linkedin_pdf)
        first = cv.experience[0]
        assert first.role == "Ingeniera de Software Senior"
        assert first.company == "Acme Corp"
        assert first.start_date == date(2020, 1, 1)
        assert first.end_date is None
        assert first.is_current is True
        assert len(first.achievements) == 2

        second = cv.experience[1]
        assert second.role == "Desarrolladora Backend"
        assert second.company == "Tech Solutions"
        assert second.start_date == date(2018, 1, 1)
        assert second.end_date == date(2020, 1, 1)
        assert second.is_current is False

    def test_education_details(self, linkedin_pdf: Path) -> None:
        cv = get_loader(linkedin_pdf).load(linkedin_pdf)
        edu = cv.education[0]
        assert edu.degree == "Grado en Ingeniería Informática"
        assert edu.institution == "Universidad Politécnica de Madrid"
        assert edu.start_date == date(2014, 1, 1)
        assert edu.end_date == date(2018, 1, 1)

    def test_languages_and_links(self, linkedin_pdf: Path) -> None:
        cv = get_loader(linkedin_pdf).load(linkedin_pdf)
        assert cv.languages[0].name == "Español"
        assert cv.languages[0].proficiency is not None
        link_hosts = [str(link) for link in cv.contact.links]
        assert any("linkedin.com" in link for link in link_hosts)
        assert any("github.com" in link for link in link_hosts)


class TestGenericPdfLoader:
    """Pruebas del cargador de PDF genérico."""

    def test_loads_valid_cv(self, generic_pdf: Path) -> None:
        cv = get_loader(generic_pdf).load(generic_pdf)
        assert cv.contact.full_name == "John Smith"
        assert cv.contact.headline == "Software Engineer"
        assert cv.contact.email == "john.smith@example.com"
        assert len(cv.experience) == 2
        assert len(cv.education) == 1

    def test_current_role_marked(self, generic_pdf: Path) -> None:
        cv = get_loader(generic_pdf).load(generic_pdf)
        assert cv.experience[0].role == "Senior Engineer"
        assert cv.experience[0].is_current is True
        assert cv.experience[0].end_date is None


class TestDocxLoader:
    """Pruebas del cargador de documentos Word."""

    def test_loads_valid_cv(self, docx_path: Path) -> None:
        cv = get_loader(docx_path).load(docx_path)
        assert cv.contact.full_name == "María Fernández Ruiz"
        assert cv.contact.headline == "Data Scientist"
        assert cv.contact.email == "maria.fernandez@example.com"
        assert cv.contact.location == "Bogotá, Colombia"
        assert len(cv.experience) == 2
        assert len(cv.education) == 1
        assert len(cv.languages) == 2

    def test_experience_from_docx(self, docx_path: Path) -> None:
        cv = get_loader(docx_path).load(docx_path)
        first = cv.experience[0]
        assert first.role == "Data Scientist"
        assert first.company == "DataCorp"
        assert first.start_date == date(2021, 3, 1)
        assert first.is_current is True

    def test_languages_from_table(self, docx_path: Path) -> None:
        cv = get_loader(docx_path).load(docx_path)
        names = [lang.name for lang in cv.languages]
        assert "Español" in names
        assert "Inglés" in names


class TestErrorHandling:
    """Pruebas de manejo de errores del pipeline de ingesta."""

    def test_empty_pdf_raises_extraction_error(self, empty_pdf: Path) -> None:
        with pytest.raises(ExtractionError):
            get_loader(empty_pdf).load(empty_pdf)

    def test_corrupt_pdf_raises(self, corrupt_pdf: Path) -> None:
        # Un PDF corrupto debe fallar con una excepción de ImCV, nunca devolver
        # datos a medio construir.
        with pytest.raises(ExtractionError):
            get_loader(corrupt_pdf).load(corrupt_pdf)

    def test_offline_no_network(self, linkedin_pdf: Path) -> None:
        """Verifica que la ingesta funciona sin acceso a la red.

        Se instalan "ganchos" de socket que fallan si algo intenta conectarse.
        Si la ingesta completa sin lanzar ``AssertionError``, es 100 % local.
        """
        import socket

        original = socket.socket

        def _blocked(*args: object, **kwargs: object) -> object:
            raise AssertionError("La ingesta intentó abrir una conexión de red")

        socket.socket = _blocked  # type: ignore[assignment]
        try:
            cv = get_loader(linkedin_pdf).load(linkedin_pdf)
            assert isinstance(cv, CVModel)
        finally:
            socket.socket = original  # type: ignore[assignment]
