import os
import sys

# Añadimos 'src' al path para que Python encuentre tus módulos
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from application.workflow.graph import app

def generate():
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