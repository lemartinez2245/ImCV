# Guía de Desarrollo para Agentes y Desarrolladores (ImCV)

## 🛠️ Gestión de Entorno y Dependencias (UV)

El proyecto utiliza estrictamente **[`uv`](https://docs.astral.sh/uv/)** como gestor de versiones de Python, dependencias y entornos virtuales. **No usar `pip`, `poetry`, `conda` ni otros gestores.**

- **Versión de Python requerida:** Python **3.12** (fijada en `.python-version` y `requires-python` de `pyproject.toml`).
- **Instalar o sincronizar dependencias y entorno virtual:**
  ```bash
  uv sync
  ```
- **Añadir dependencias:**
  ```bash
  uv add <paquete>
  uv add --dev <paquete-dev>   # para dependencias de desarrollo (grupo dev)
  ```
- **Eliminar dependencias:**
  ```bash
  uv remove <paquete>
  ```
- **Ejecutar comandos en el entorno virtual:**
  ```bash
  uv run <comando>
  # Ejemplos:
  uv run pytest
  uv run ruff check .
  uv run ruff format .
  uv run uvicorn imcv.main:app --reload
  ```
- **Actualizar el lockfile:**
  ```bash
  uv lock          # resolver dependencias
  uv lock --upgrade # actualizar a últimas versiones compatibles
  ```

> ⚠️ **Importante:** Tras modificar `pyproject.toml` manualmente, ejecutar `uv sync` para reflejar los cambios en `uv.lock` y en el entorno virtual (`.venv`).

## 📐 Metodología: Spec-Driven Development (SDD)

1. **Specs primero:** Cualquier implementación técnica no trivial debe estar precedida por (o acompañada de) su documento correspondiente en `specs/`.
2. **Backend tipado:** Código en `src/imcv/` con tipado estricto mediante Pydantic v2 y Type Hints de Python 3.12.
3. **Frontend:** Aplicación de escritorio con **Tauri v2** y frontend en **React (TypeScript)**.
4. **Documentación:** Decisiones arquitectónicas y guías de alto nivel en `docs/`.
5. **Verificación:** Todo cambio debe pasar las pruebas y el linter:
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run pytest
   ```

### Formato de nombre de archivos de Specs

Los Specs deben seguir el siguiente formato de nombre:

```
XXX - Spec name.MD
```

Dentro de la carpeta de `specs/`. Las `XXX` representan el número de spec, por ejemplo la 4 spec estaría representada como la `004`.

## 📁 Estructura del Proyecto

```
ImCV/
├── src/imcv/          # Código del backend (Python)
├── tests/             # Pruebas (pytest)
├── specs/             # Especificaciones técnicas (SDD)
├── docs/              # Documentación del proyecto
├── pyproject.toml     # Configuración del proyecto y dependencias
├── uv.lock            # Lockfile de UV (versiones exactas)
└── .python-version    # Versión de Python fijada (3.12)
```

## 🧰 Stack Tecnológico

- **Backend Core:** Python 3.12, Pydantic v2
- **Orquestación IA:** LangGraph + LangChain (`langchain-ollama` para inferencia local)
- **Ingesta de documentos:** `pymupdf` (PDF), `python-docx` (Word)
- **Exportación:** `docxtpl` (DOCX), `weasyprint` (PDF vectorial desde HTML/CSS)
- **API Backend:** FastAPI + Uvicorn
- **Frontend / Desktop:** Tauri v2 + React (TypeScript)
- **Calidad de código:** `ruff` (linter + formatter), `pytest`
