from flask import Flask, render_template, abort
import json, os

app = Flask(__name__)

# Ruta ABSOLUTA al JSON, importante en Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_RECETAS = os.path.join(BASE_DIR, "recipes.json")

def cargar_recetas():
    if not os.path.exists(ARCHIVO_RECETAS):
        return []
    try:
        with open(ARCHIVO_RECETAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Si el JSON estuviera corrupto, evita que casque la app
        return []

@app.route("/")
def inicio():
    recetas = cargar_recetas()
    return render_template("index.html", recetas=recetas)

@app.route("/receta/<nombre>")
def ver_receta(nombre):
    recetas = cargar_recetas()
    for r in recetas:
        if r["name"].lower().replace(" ", "-") == nombre.lower():
            return render_template("receta.html", receta=r)
    abort(404)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Nada de debug/reloader en Render
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
