"""ImCV — Generador y optimizador de CVs inteligente, local-first."""

from imcv.exceptions import (
    ExtractionError,
    ImCVError,
    UnsupportedFormatError,
    ValidationError,
)
from imcv.models import (
    Certification,
    ContactInfo,
    CVModel,
    Education,
    EmploymentType,
    Experience,
    Language,
    ProficiencyLevel,
    Project,
    Reference,
    Skill,
)

__all__ = [
    "CVModel",
    "Certification",
    "ContactInfo",
    "Education",
    "EmploymentType",
    "ExtractionError",
    "Experience",
    "ImCVError",
    "Language",
    "ProficiencyLevel",
    "Project",
    "Reference",
    "Skill",
    "UnsupportedFormatError",
    "ValidationError",
]


def main() -> None:
    """Punto de entrada de demostración de ImCV."""
    print("ImCV — Generador y optimizador de CVs")
