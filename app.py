from flask import Flask, render_template, abort
import json
import os

app = Flask(__name__)
ARCHIVO_RECETAS = "recipes.json"

# Cargar recetas
def cargar_recetas():
    if os.path.exists(ARCHIVO_RECETAS):
        with open(ARCHIVO_RECETAS, "r", encoding="utf-8") as f:
            return json.load(f)
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
    app.run(debug=True)
