"""Modelos de datos canónicos de un CV (Pydantic v2).

El :class:`CVModel` es el contrato de datos independiente de formato que
recorre todo el pipeline de ImCV. Cualquier fuente (PDF de LinkedIn, PDF
genérico o DOCX) se normaliza a estas estructuras antes de ser procesada.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator, model_validator

from imcv.dates import parse_flexible_date

__all__ = [
    "CVModel",
    "Certification",
    "ContactInfo",
    "Education",
    "EmploymentType",
    "Experience",
    "Language",
    "ProficiencyLevel",
    "Project",
    "Reference",
    "Skill",
]


class ProficiencyLevel(StrEnum):
    """Nivel de dominio de una habilidad o idioma."""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"


class EmploymentType(StrEnum):
    """Tipo de relación laboral."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    VOLUNTEER = "volunteer"


class _DateNormalizingModel(BaseModel):
    """Base que normaliza automáticamente campos de fecha flexibles."""

    @field_validator(
        "start_date",
        "end_date",
        "issue_date",
        "expiry_date",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def _normalize_date(cls, value: object) -> date | None:
        return parse_flexible_date(value)


class ContactInfo(BaseModel):
    """Datos personales y de contacto del titular del CV."""

    full_name: str = Field(min_length=1, description="Nombre completo.")
    headline: str | None = Field(
        default=None, description="Título profesional, p. ej. 'Ingeniero de Software Senior'."
    )
    email: EmailStr | None = Field(default=None, description="Correo electrónico validado.")
    phone: str | None = Field(default=None, description="Teléfono de contacto.")
    location: str | None = Field(default=None, description="Ubicación (ciudad, país).")
    links: list[HttpUrl] = Field(
        default_factory=list,
        description="Enlaces a LinkedIn, GitHub, portafolio, etc.",
    )


class Experience(_DateNormalizingModel):
    """Una entrada del historial laboral."""

    role: str = Field(min_length=1, description="Puesto o rol desempeñado.")
    company: str = Field(min_length=1, description="Empresa u organización.")
    location: str | None = Field(default=None, description="Ubicación del puesto.")
    start_date: date = Field(description="Fecha de inicio (YYYY, YYYY-MM o YYYY-MM-DD).")
    end_date: date | None = Field(
        default=None,
        description="Fecha de fin. ``None`` implica 'Presente' cuando ``is_current`` es True.",
    )
    is_current: bool = Field(default=False, description="Indica si es el puesto actual.")
    employment_type: EmploymentType | None = Field(default=None, description="Tipo de contrato.")
    description: str | None = Field(
        default=None, description="Resumen de responsabilidades y logros."
    )
    skills_list: list[str] = Field(
        default_factory=list,
        description="Habilidades o tecnologías utilizadas en este puesto.",
    )
    achievements: list[str] = Field(
        default_factory=list,
        description="Logros concretos y cuantificables.",
    )

    @model_validator(mode="after")
    def _check_current_consistency(self) -> Self:
        """Un puesto actual no debe tener fecha de fin."""
        if self.is_current and self.end_date is not None:
            raise ValueError("Un puesto marcado como actual no debe tener end_date")
        return self


class Education(_DateNormalizingModel):
    """Una entrada de formación académica."""

    degree: str = Field(min_length=1, description="Título, grado o certificación obtenida.")
    institution: str = Field(min_length=1, description="Institución educativa.")
    field_of_study: str | None = Field(default=None, description="Área de estudio.")
    start_date: date = Field(description="Fecha de inicio.")
    end_date: date | None = Field(default=None, description="Fecha de fin o graduación.")
    grade: str | None = Field(default=None, description="Nota, calificación o mención.")
    description: str | None = Field(default=None, description="Detalle adicional de la formación.")


class Skill(BaseModel):
    """Una habilidad o competencia técnica."""

    name: str = Field(min_length=1, description="Nombre de la habilidad.")
    proficiency: ProficiencyLevel | None = Field(default=None, description="Nivel de dominio.")
    keywords: list[str] = Field(default_factory=list, description="Palabras clave relacionadas.")


class Language(BaseModel):
    """Un idioma y su nivel de dominio."""

    name: str = Field(min_length=1, description="Nombre del idioma.")
    proficiency: ProficiencyLevel | None = Field(default=None, description="Nivel de dominio.")


class Certification(_DateNormalizingModel):
    """Una certificación, licenca o curso relevante."""

    name: str = Field(min_length=1, description="Nombre de la certificación.")
    issuer: str | None = Field(default=None, description="Entidad emisora.")
    issue_date: date | None = Field(default=None, description="Fecha de emisión.")
    expiry_date: date | None = Field(default=None, description="Fecha de caducidad, si aplica.")
    credential_url: HttpUrl | None = Field(default=None, description="URL de verificación.")


class Project(BaseModel):
    """Un proyecto personal o profesional destacado."""

    name: str = Field(min_length=1, description="Nombre del proyecto.")
    description: str | None = Field(default=None, description="Descripción del proyecto.")
    url: HttpUrl | None = Field(default=None, description="Enlace al proyecto.")
    technologies: list[str] = Field(default_factory=list, description="Tecnologías utilizadas.")


class Reference(BaseModel):
    """Una referencia profesional o personal."""

    name: str = Field(min_length=1, description="Nombre de la referencia.")
    relationship: str | None = Field(default=None, description="Relación con el candidato.")
    contact: str | None = Field(default=None, description="Datos de contacto de la referencia.")


class CVModel(BaseModel):
    """Esquema canónico e independiente de formato de un CV."""

    contact: ContactInfo = Field(description="Datos personales obligatorios.")
    summary: str | None = Field(default=None, description="Resumen o perfil profesional.")
    experience: list[Experience] = Field(default_factory=list, description="Historial laboral.")
    education: list[Education] = Field(default_factory=list, description="Formación académica.")
    skills: list[Skill] = Field(default_factory=list, description="Habilidades y competencias.")
    languages: list[Language] = Field(default_factory=list, description="Idiomas.")
    certifications: list[Certification] = Field(
        default_factory=list, description="Certificaciones."
    )
    projects: list[Project] = Field(default_factory=list, description="Proyectos.")
    references: list[Reference] = Field(default_factory=list, description="Referencias.")

    @model_validator(mode="after")
    def _sync_current_flag(self) -> Self:
        """Marca automáticamente ``is_current`` cuando ``end_date`` es ``None``.

        Esto permite construir la experiencia sin tener que recordar poner el
        flag a mano cuando se importa desde documentos que no lo indican.
        """
        for exp in self.experience:
            if exp.end_date is None and not exp.is_current:
                exp.is_current = True
        return self
