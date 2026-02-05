"""
Script de generación de diagramas del grafo LangGraph.

Genera artefactos visuales del workflow de agentes para documentación:
    - docs/workflow.mermaid: Código Mermaid para embeber en README.md o GitHub.
    - docs/workflow_graph.png: Imagen PNG del grafo (requiere Graphviz instalado).

Usage:
    python generate_graph.py

Note:
    Requiere que las variables de entorno del LLM estén configuradas en .env,
    ya que al importar el grafo se inicializan los adaptadores.
"""
import os
import sys
# Cargamos las variables de entorno
from dotenv import load_dotenv
load_dotenv()
# Añadimos 'src' al path para que Python encuentre tus módulos
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from application.workflow.graph import app



def generate():
    """
    Genera los artefactos visuales del grafo de LangGraph.

    Crea la carpeta ``docs/`` si no existe y exporta:
        1. Código Mermaid (.mermaid) — siempre disponible.
        2. Imagen PNG (.png) — opcional, depende de Graphviz.

    Raises:
        Exception: Si el grafo no puede ser compilado o exportado.
    """
    # Creamos la carpeta docs si no existe para guardar artefactos
    os.makedirs("docs", exist_ok=True)

    try:
        # 1. Obtener el código Mermaid (Ideal para el README.md)
        mermaid_code = app.get_graph().draw_mermaid()
        
        with open("docs/workflow.mermaid", "w") as f:
            f.write(mermaid_code)
        
        print("✅ Código Mermaid generado en 'docs/workflow.mermaid'")
        print("-" * 30)
        print("Copiá esto en tu README.md:")
        print(f"\n```mermaid\n{mermaid_code}\n```\n")
        print("-" * 30)

        # 2. Intentar generar el PNG (Opcional, requiere dependencias de sistema como Graphviz)
        # Si falla, no te preocupes, el código Mermaid es lo más importante.
        try:
            app.get_graph().draw_mermaid_png(output_file_path="docs/workflow_graph.png")
            print("✅ Imagen PNG generada en 'docs/workflow_graph.png'")
        except Exception:
            print("⚠️  Nota: No se pudo generar el PNG (faltan dependencias de sistema).")
            print("   Pero el código Mermaid de arriba funcionará perfecto en GitHub.")

    except Exception as e:
        print(f"❌ Error al generar el grafo: {e}")

if __name__ == "__main__":
    generate()