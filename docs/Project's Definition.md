# ImCV

## Objetivo del proyecto:

Crear un programa que, a través de la interacción con el usuario y distintas fuentes de información (documentos, enlaces, etc.) sea capaz de generar un CV orientado a la búsqueda general de empleo o a un empleo en específico. Para potenciar las capacidades de este sistema lo ideal será utilizar modelos LLM de forma local utilizando Ollama (100% privado, local y sin necesidad de cuentas ni costos), o utilizando las APIs de proveedores comerciales si el usuario así lo prefiere.

## Requerimientos técnicos

El backend del programa se ejecutará en Python y utilizará las librerías más optimizadas para su uso con Python y manipulación de documentos. Necesito utilizar un stack tecnológico de front end que permita la edición y visualización del contenido de los documentos que se estarán manipulando en tiempo real. Para el backend quiero utilizar LangGraph y librerías que sean capaces de exportar a PDF, Docs y otros formatos, priorizando la calidad y la compatibilidad antes que un mayor número de formatos.

El backend deberá ser model-agnostic, por defecto se tendrá una lista de prioridades de modelos que tengan la mayor compatibilidad con las instrucciones del sistema, pero el usuario podrá también configurar su provedor de LLM preferido para esto, utilizando la versatilidad de LangChain y LangGraph junto a Ollama.

El frontend será desarrollado con Tauri para ofrecer una aplicación standalone de escritorio ligera y con soporte nativo para edición y renderizado web en tiempo real. Estará optimizada inicialmente para Linux y entornos KDE, pero con compatibilidad multiplataforma garantizada (Linux, Windows, macOS).

El proyecto será desarrollado por mí, de momento, y se subirá a mi cuenta de Github. Será desarrollado con SDD (Spec Driven Development) utilizando mi cuenta de Opencode, los specs se escribirán dentro de la carpeta `specs` del proyecto, la documentación se mantendrá junto a este archivo en `docs`.

## Funcionamiento básico inicial (POC)

Un usuario que utiliza nuestro programa debe poder adjuntar un documento con sus datos personales y experiencia laboral a través de un PDF, documento de Word o el PDF exportado de su perfil de LinkedIn (priorizando este formato para evitar restricciones de scraping directo), y que el programa pueda plasmar esta información en un formulario estructurado que contenga todo lo reflejado en dicha fuente.

Una vez se tenga esta información, si aún no se sabe el tipo de perfil que tiene el usuario, se le preguntará por el rol al que desea aplicar y una vez se tenga esta información se le sugerirá una paleta de colores y diseño básico recomendado a utilizar.

Si el usuario está de acuerdo con el diseño sugerido, la información que se tiene del usuario deberá ser organizada y plasmada en el nuevo documento con el diseño seleccionado de una forma que a los reclutadores de este tipo de perfil les sea fácil identificar por qué el perfil que se le presenta es bueno para el rol que contrata.

Una vez que el documento está terminado, el usuario podrá exportarlo a PDF o a Word para poder subirlo a LinkedIn en su próxima aplicación laboral.