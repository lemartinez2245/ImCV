# ImCV 📄✨

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-orange.svg)](#)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](#)
[![Tauri: v2](https://img.shields.io/badge/Tauri-v2-FFC107.svg?logo=tauri&logoColor=black)](#)
[![Ollama: Supported](https://img.shields.io/badge/Ollama-Local%20LLM-black.svg)](#)

> **Generador y optimizador de CVs inteligente, local-first y enfocado en la privacidad del usuario.**

**ImCV** es una aplicación de escritorio diseñada para ayudar a profesionales a crear, reestructurar y optimizar sus currículums vitae. Utilizando inteligencia artificial orquestada mediante grafos de agentes, ImCV adapta el perfil del usuario a puestos de trabajo específicos, optimizando la redacción para sistemas **ATS** (*Applicant Tracking Systems*) y resaltando los logros clave para los reclutadores.

---

## 💡 ¿Por qué ImCV?

Muchos generadores de CVs actuales requieren subir datos personales sensibles (historial laboral, datos de contacto) a servidores de terceros o dependen de suscripciones costosas a APIs de IA.

ImCV resuelve esto mediante un enfoque **Local-First & Privacy-First**:

- **0% Filtración de datos:** Todo el procesamiento e inferencia se realiza localmente en tu ordenador mediante **Ollama**.
- **0% Costos recurrentes:** Diseñado para funcionar con modelos de código abierto y gratuitos.
- **Transparencia total:** Código abierto con soporte para personalizar el proveedor de IA si prefieres usar APIs comerciales.

---

## 🔥 Características Principales

- 📥 **Ingesta Inteligente de Datos:** Importa tu experiencia desde archivos **PDF**, **DOCX (Word)** o el **PDF exportado de tu perfil de LinkedIn**.
- 🎯 **Optimización Orientada al Rol:** Reorganización de contenidos según el puesto objetivo mediante metodologías comprobadas (formatos STAR / Google XYZ).
- 🎨 **Sugerencia de Diseños y Paletas:** Recomendaciones automáticas de maquetación y estilos visuales adaptados al sector laboral.
- ⚡ **Previsualización y Edición en Tiempo Real:** Interfaz fluida construida con **Tauri**, que permite ver los cambios en el documento al instante.
- 📤 **Exportación de Alta Fidelidad:** Genera documentos limpios y vectoriales en formatos **PDF** y **DOCX** totalmente editables.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Función |
| :--- | :--- | :--- |
| **Frontend / Desktop** | [Tauri (Rust + Web Tech)](https://tauri.app/) | App de escritorio liviana, multiplataforma y con renderizado en tiempo real. |
| **Backend Core** | [Python 3.11+](https://www.python.org/) | Extracción de datos, procesamiento de texto y motor de exportación. |
| **Orquestación IA** | [LangGraph](https://www.langchain.com/langgraph) / [LangChain](https://www.langchain.com/) | Agentes de análisis de perfiles, emparejamiento con vacantes y reescritura. |
| **Motor LLM Local** | [Ollama](https://ollama.com/) | Inferencia de modelos abiertos (Llama 3, Qwen, Mistral) localmente. |

---

## 🔄 Flujo del Usuario (Prueba de Concepto - POC)

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│ Ingesta de CV   │ ──► │ Selección de Rol │ ──► │ Sugerencia de Diseño │
│ (PDF/Word/LN)   │     │ & Perfil Objetivo│     │ & Paleta de Colores  │
└─────────────────┘     └──────────────────┘     └──────────────────────┘
                                                            │
┌─────────────────┐     ┌──────────────────┐                │
│ Exportación     │ ◄── │ Reescritura ATS  │ ◄──────────────┘
│ (PDF / Word)    │     │ & Maquetación    │
└─────────────────┘     └──────────────────┘
```

---

## 📋 Requisitos Previos (Para Desarrolladores / Usuarios)

Para ejecutar ImCV en su entorno local necesitarás:

1. **[Ollama](https://ollama.com/)** instalado y ejecutándose en segundo plano.
2. **Python 3.11** o superior.
3. **Rust / Cargo** (para la compilación del entorno de desarrollo de Tauri).

---

## 📐 Metodología de Desarrollo

Este proyecto sigue la metodología **Spec-Driven Development (SDD)**:

- 📂 `specs/`: Contiene las especificaciones técnicas estructuradas de cada componente antes de su implementación.
- 📂 `docs/`: Documentación del proyecto, arquitectura y guía de diseño.

---

## 📜 Licencia

Este proyecto está licenciado bajo la **GNU General Public License v3.0 (GPLv3)**.

Esto significa que ImCV es y siempre será **software libre y de código abierto**. Eres libre de usar, estudiar, modificar y redistribuir el código, siempre que cualquier obra derivada mantenga la misma licencia libre GPLv3. Consulta el archivo `LICENSE` para más detalles.
