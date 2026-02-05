## Arquitectura del Flujo (AI Agents)

El sistema utiliza **LangGraph** para orquestar un grafo cíclico de agentes que procesan el contenido del video de forma asíncrona.

```mermaid
graph TD
    __start__((START)) --> extract[Nodo de Extracción]
    extract --> analyze[Nodo de Análisis Gemini]
    analyze --> persist[Nodo de Persistencia Django]
    persist --> __end__((END))
    
    style extract fill:#f9f,stroke:#333,stroke-width:2px
    style analyze fill:#bbf,stroke:#333,stroke-width:2px
    style persist fill:#bfb,stroke:#333,stroke-width:2px