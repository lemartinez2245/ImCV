"""Pruebas de los modelos de datos y el normalizador de fechas."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError as PydanticValidationError

from imcv.dates import is_present_marker, parse_flexible_date
from imcv.models import (
    ContactInfo,
    CVModel,
    Education,
    Experience,
    Language,
    ProficiencyLevel,
    Skill,
)


class TestParseFlexibleDate:
    """Pruebas del normalizador multilingüe de fechas."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("2023", date(2023, 1, 1)),
            ("2023-05", date(2023, 5, 1)),
            ("2023-05-15", date(2023, 5, 15)),
            ("May 2021", date(2021, 5, 1)),
            ("mayo de 2020", date(2020, 5, 1)),
            ("septiembre 2019", date(2019, 9, 1)),
            ("January 2019", date(2019, 1, 1)),
            ("ene 2018", date(2018, 1, 1)),
            ("dec 2017", date(2017, 12, 1)),
            (date(2020, 3, 9), date(2020, 3, 9)),
            (2020, date(2020, 1, 1)),
        ],
    )
    def test_valid_dates(self, raw: object, expected: date) -> None:
        assert parse_flexible_date(raw) == expected

    def test_none_returns_none(self) -> None:
        assert parse_flexible_date(None) is None

    @pytest.mark.parametrize(
        "bad",
        ["", "no-fecha", "Presente", "abc 9999", "31/13/2020", "2020-13-01"],
    )
    def test_invalid_dates_raise(self, bad: str) -> None:
        with pytest.raises(ValueError):
            parse_flexible_date(bad)

    def test_year_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_flexible_date("1800")
        with pytest.raises(ValueError):
            parse_flexible_date(2200)


class TestPresentMarkers:
    """Pruebas de detección de marcadores de actualidad."""

    @pytest.mark.parametrize(
        "value", ["present", "Presente", "ACTUALIDAD", "current", "hoy", "en curso"]
    )
    def test_present(self, value: str) -> None:
        assert is_present_marker(value) is True

    @pytest.mark.parametrize("value", ["2020", "Presentación", "not present", None])
    def test_not_present(self, value: object) -> None:
        assert is_present_marker(value) is False


class TestContactInfo:
    """Pruebas del modelo de contacto."""

    def test_valid_minimal(self) -> None:
        contact = ContactInfo(full_name="Ana García")
        assert contact.full_name == "Ana García"
        assert contact.links == []

    def test_email_validation(self) -> None:
        contact = ContactInfo(full_name="Ana", email="ana@example.com")
        assert contact.email == "ana@example.com"
        with pytest.raises(PydanticValidationError):
            ContactInfo(full_name="Ana", email="no-es-email")

    def test_empty_name_rejected(self) -> None:
        with pytest.raises(PydanticValidationError):
            ContactInfo(full_name="")


class TestExperience:
    """Pruebas del modelo de experiencia."""

    def test_is_current_requires_no_end_date(self) -> None:
        with pytest.raises(PydanticValidationError):
            Experience(
                role="Dev",
                company="Acme",
                start_date="2020",
                end_date="2021",
                is_current=True,
            )

    def test_dates_are_normalized(self) -> None:
        exp = Experience(role="Dev", company="Acme", start_date="mayo 2020")
        assert exp.start_date == date(2020, 5, 1)
        assert exp.end_date is None
        assert exp.is_current is False

    def test_end_date_present_marker_rejected(self) -> None:
        # El modelo es estricto: "Presente" no es una fecha. El loader lo
        # convierte a end_date=None + is_current=True antes de construir.
        with pytest.raises(PydanticValidationError):
            Experience(role="Dev", company="Acme", start_date="2020", end_date="Presente")


class TestCVModel:
    """Pruebas del modelo raíz."""

    def _make(self, **kwargs: object) -> CVModel:
        data = {"contact": ContactInfo(full_name="Ana")}
        data.update(kwargs)  # type: ignore[arg-type]
        return CVModel(**data)  # type: ignore[arg-type]

    def test_empty_sections_by_default(self) -> None:
        cv = self._make()
        assert cv.experience == []
        assert cv.education == []
        assert cv.skills == []

    def test_sync_current_flag(self) -> None:
        exp = Experience(role="Dev", company="Acme", start_date="2020", is_current=False)
        cv = self._make(experience=[exp])
        assert cv.experience[0].is_current is True
        assert cv.experience[0].end_date is None

    def test_serialization_roundtrip(self) -> None:
        cv = self._make(
            skills=[Skill(name="Python", proficiency=ProficiencyLevel.ADVANCED)],
            languages=[Language(name="Español", proficiency=ProficiencyLevel.NATIVE)],
            education=[
                Education(degree="Grado", institution="UPM", start_date="2014", end_date="2018")
            ],
        )
        data = cv.model_dump(mode="json")
        restored = CVModel.model_validate(data)
        assert restored.contact.full_name == "Ana"
        assert restored.skills[0].name == "Python"
        assert restored.education[0].start_date == date(2014, 1, 1)
