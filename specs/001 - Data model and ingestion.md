# Spec 01 — Modelo de Datos e Ingesta de Documentos

- **Estado:** Implementado
- **Versión:** 0.1.1
- **Última actualización:** 2026-10-27
- **Dependencias del entorno:** `pydantic>=2`, `pymupdf`, `python-docx`

---

## 1. Objetivo

Definir de forma estricta y tipada la **estructura universal de datos de un CV** (`CVModel`) que será independiente del formato de origen (PDF de LinkedIn, PDF genérico u hoja de vida Word). Este modelo actuará como el **estado compartido** que recorrerá el grafo de agentes de LangGraph (ingesta → análisis → reescritura ATS → formateo) y como contrato de datos entre el backend Python y el frontend React/Tauri.

Todo el módulo debe garantizar que la información personal sensible del usuario **nunca salga del entorno local**.

---

## 2. Alcance

### 2.1 Incluido

- Esquema Pydantic v2 del CV completo (datos personales, experiencia, educación, habilidades, idiomas, certificaciones, proyectos, referencias y metadatos).
- Normalización de datos extraídos a un esquema único y validado.
- Estrategia de ingesta desde tres fuentes: **PDF de LinkedIn**, **PDF genérico** y **DOCX**.
- Manejo de errores y validación estricta.

### 2.2 Fuera de alcance (specs posteriores)

- Orquestación con LangGraph (ver `specs/02-agent-orchestrator.md`).
- Sugerencia de diseño, paleta de colores y maquetación.
- Exportación a PDF/DOCX.
- API REST y comunicación con el frontend.

---

## 3. Modelo de Datos (`imcv.models`)

Implementado con **Pydantic v2**. Todos los campos usan tipado estricto de Python 3.12 y alias en `snake_case`.

### 3.1 Tipos de apoyo

```python
from enum import StrEnum
from typing import Annotated
from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ProficiencyLevel(StrEnum):
    """Nivel de dominio de una habilidad o idioma."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    VOLUNTEER = "volunteer"
```

### 3.2 Secciones del CV

```python
class ContactInfo(BaseModel):
    full_name: str = Field(min_length=1)
    headline: str | None = None            # p. ej. "Ingeniero de Software Senior"
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None
    links: list[HttpUrl] = Field(default_factory=list)  # LinkedIn, GitHub, portafolio, etc.


class Experience(BaseModel):
    role: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str | None = None
    start_date: datetime.date = Field(min_length=1)          # formato normalizado "YYYY-MM" o "YYYY"
    end_date: datetime.date | None = None            # None implica "Presente"
    is_current: bool = False
    employment_type: EmploymentType | None = None
    description: str | None = None         # logros y responsabilidades
    skills_list: list[str] = Field(default_factory=list)   # habilidades adquiridas o utilizadas
    achievements: list[str] = Field(default_factory=list)  # puntos cuantificables


class Education(BaseModel):
    degree: str = Field(min_length=1)
    institution: str = Field(min_length=1)
    field_of_study: str | None = None
    start_date: datetime.date = Field(min_length=1)
    end_date: datetime.date | None = None
    grade: str | None = None
    description: str | None = None


class Skill(BaseModel):
    name: str = Field(min_length=1)
    proficiency: ProficiencyLevel | None = None
    keywords: list[str] = Field(default_factory=list)


class Language(BaseModel):
    name: str = Field(min_length=1)
    proficiency: ProficiencyLevel | None = None


class Certification(BaseModel):
    name: str = Field(min_length=1)
    issuer: str | None = None
    issue_date: datetime.date | None = None
    expiry_date: datetime.date | None = None
    credential_url: HttpUrl | None = None


class Project(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None
    url: HttpUrl | None = None
    technologies: list[str] = Field(default_factory=list)


class Reference(BaseModel):
    name: str = Field(min_length=1)
    relationship: str | None = None
    contact: str | None = None
```

### 3.3 Modelo raíz

```python
class CVModel(BaseModel):
    """Esquema canónico e independiente de formato de un CV."""
    contact: ContactInfo
    summary: str | None = None
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[Skill] = Field(default_factory=list)
    languages: list[Language] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)
```

---

## 4. Pipeline de Ingesta (`imcv.ingestion`)

### 4.1 Interfaz común

Cada origen expone una implementación de una interfaz común para que el grafo sea agnóstico al formato:

```python
from abc import ABC, abstractmethod
from pathlib import Path


class DocumentLoader(ABC):
    """Contrato para cargar y normalizar un CV desde un archivo."""

    @abstractmethod
    def load(self, path: Path) -> CVModel:
        """Extrae y normaliza el contenido del archivo a un CVModel validado."""
        ...
```

### 4.2 Estrategias de origen

| Origen | Extensión | Implementación | Notas |
| :--- | :--- | :--- | :--- |
| **PDF de LinkedIn** | `.pdf` | `LinkedInPdfLoader` | Detectado por la estructura/URLs del PDF exportado de LinkedIn. Prioridad máxima para evitar scraping. |
| **PDF genérico** | `.pdf` | `GenericPdfLoader` | Cualquier CV en PDF. |
| **Word** | `.docx` | `DocxLoader` | Archivo `.docx` generado por Word o `python-docx`. |

#### 4.2.1 `LinkedInPdfLoader` / `GenericPdfLoader` (motor: `pymupdf`)

1. **Extracción de texto** por página con `pymupdf` (`pymupdf4llm` para Markdown estructurado cuando esté disponible), preservando bloques y orden de lectura.
2. **Detección de secciones** mediante análisis de encabezados y palabras clave (p. ej. `Experiencia`, `Educación`, `Habilidades`, `Contacto`) en Español o Inglés.
3. **Segmentación** en los tipos de la Sección 3.
4. **Normalización** de fechas (`YYYY-MM-DD` y `YYYY-MM` a datetime.date), listas y enlaces.
5. **Construcción** de `CVModel` y validación con Pydantic.

#### 4.2.2 `DocxLoader` (motor: `python-docx`)

1. **Recorrido de párrafos** con captura de estilo de encabezado (`Heading 1..N`) para segmentar secciones.
2. **Recorrido de tablas** (`doc.tables`) para experiencias o habilidades en formato tabular.
3. **Detección de enlaces** en relaciones del documento.
4. **Normalización y construcción** igual que en 4.2.1.

---

## 5. Manejo de Errores y Validación

- Se define una jerarquía de excepciones en `imcv.exceptions`:

```python
class ImCVError(Exception):
    """Error base de ImCV."""


class UnsupportedFormatError(ImCVError):
    """Formato o extensión de archivo no soportado."""


class ExtractionError(ImCVError):
    """No se pudo extraer contenido legible del documento."""


class ValidationError(ImCVError):
    """El contenido extraído no cumple el esquema CVModel."""
```

- Cualquier fallo de normalización o validación debe elevar una excepción de esta jerarquía, **nunca** datos a medio construir.
- Un `CVModel` solo se considera válido si pasa la validación de Pydantic sin errores.

---

## 6. Requisitos de Pruebas (`tests/test_ingestion.py`)

- Cada `DocumentLoader` debe tener pruebas unitarias con **fixtures reales** en `tests/fixtures/` (un PDF de LinkedIn de muestra, un PDF genérico y un `.docx`).
- Pruebas de validación de `CVModel` (campos obligatorios, formatos de fecha, rechazo de datos inválidos).
- Pruebas de manejo de errores (archivo corrupto, formato no soportado, documento vacío).
- Verificación: `uv run pytest` debe pasar al 100 %.

---

## 7. Decisiones Técnicas

| Decisión | Motivo |
| :--- | :--- |
| **Pydantic v2** | Validación estricta, serialización a/desde JSON y compatibilidad nativa con salida estructurada de LLMs. |
| **`pymupdf` como motor PDF** | Es el extractor más rápido y con mejor preservación de estructura; `pymupdf4llm` aporta Markdown de alta calidad para parsing por LLM. |
| **`python-docx` para Word** | Lectura nativa de estilos de encabezado y tablas, necesaria para segmentar el documento. |
| **Modelo agnóstico de origen** | Un único `CVModel` evita acoplar la lógica downstream al formato de entrada. |
| **Fechas normalizadas a `YYYY-MM`** | Facilita ordenamiento cronológico y reescritura posterior sin ambigüedad. |
| **Modo offline** | Todas las librerías utilizadas deben funcionar de forma local, sin acceso a internet para ninguna de las funcionalidades a utiliar dentro del flujo del programa. |

---

## 8. Criterios de Aceptación

1. `CVModel` cubre todas las secciones estándar de un CV y valida correctamente.
2. Los tres `DocumentLoader` convierten sus archivos fixture a un `CVModel` válido.
3. Las fechas y los enlaces quedan normalizados en el modelo resultante.
4. Los errores de formato/carga/validación se manejan mediante la jerarquía `ImCVError`.
5. `uv run pytest` pasa al 100 % y `uv run ruff check .` no reporta problemas.
