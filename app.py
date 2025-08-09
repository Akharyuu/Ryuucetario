from flask import Flask, render_template, abort
from flask import request, redirect, url_for
import unicodedata
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

def _norm(s):
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s.lower().strip()

@app.route("/")
def inicio():
    recetas = cargar_recetas()

    # Parámetros GET
    busqueda = request.args.get("q", "").strip()
    buscar_en = request.args.get("campo", "nombre")      # "nombre" | "ingredientes"
    ordenar   = request.args.get("ordenar", "categoria") # "categoria" | "cocina" | "alfabetico"

    # --- Filtrado ---
    if busqueda:
        q = _norm(busqueda)
        if buscar_en == "nombre":
            recetas = [r for r in recetas if q in _norm(r.get("name", ""))]
        elif buscar_en == "ingredientes":
            filtradas = []
            for r in recetas:
                ok = False
                for ing in r.get("ingredients", []):
                    if isinstance(ing, dict):
                        # Busca en nombre y en nota (si existe)
                        if q in _norm(ing.get("nombre", "")) or q in _norm(ing.get("nota", "")):
                            ok = True
                            break
                    else:
                        # Por si algún día guardas ingredientes como texto
                        if q in _norm(ing):
                            ok = True
                            break
                if ok:
                    filtradas.append(r)
            recetas = filtradas

    # --- Orden y agrupación ---
    if ordenar == "categoria":
        recetas.sort(key=lambda r: (r.get("category", "") or "", r.get("name","").lower()))
        agrupar_por = "category"
    elif ordenar == "cocina":
        recetas.sort(key=lambda r: (r.get("cuisine", "") or "", r.get("name","").lower()))
        agrupar_por = "cuisine"
    else:
        recetas.sort(key=lambda r: r.get("name","").lower())
        agrupar_por = None

    grupos = {}
    if agrupar_por:
        for r in recetas:
            clave = r.get(agrupar_por, "") or "Sin clasificar"
            grupos.setdefault(clave, []).append(r)
    else:
        grupos[""] = recetas

    return render_template("index.html",
                           grupos=grupos,
                           busqueda=busqueda,
                           buscar_en=buscar_en,
                           ordenar=ordenar)

@app.route("/receta/<nombre>")
def ver_receta(nombre):
    recetas = cargar_recetas()
    for r in recetas:
        if r["name"].lower().replace(" ", "-") == nombre.lower():
            return render_template("receta.html", receta=r)
    abort(404)

@app.route("/nueva", methods=["GET", "POST"])
def nueva_receta():
    if request.method == "POST":
        recetas = cargar_recetas()

        # Parseo sencillo: 1 ingrediente por línea, 1 paso por línea
        ingredients_str = request.form.get("ingredients", "")
        steps_str = request.form.get("steps", "")

        ingredientes = [s.strip() for s in ingredients_str.splitlines() if s.strip()]
        pasos = [s.strip() for s in steps_str.splitlines() if s.strip()]

        # Campos numéricos tolerantes (si vienen vacíos → 0)
        def to_int(x, default=0):
            try:
                return int(x)
            except:
                return default

        nueva = {
            "name": request.form.get("name", "").strip(),
            "cuisine": request.form.get("cuisine", "").strip(),
            "rations": to_int(request.form.get("rations", 0)),
            "prep_time": to_int(request.form.get("prep_time", 0)),
            "category": request.form.get("category", "").strip() or "Principal",
            "ingredients": ingredientes,
            "steps": pasos
        }

        recetas.append(nueva)
        with open(ARCHIVO_RECETAS, "w", encoding="utf-8") as f:
            json.dump(recetas, f, ensure_ascii=False, indent=2)
        return redirect(url_for("inicio"))

    return render_template("form_receta.html", receta=None)


@app.route("/editar/<nombre>", methods=["GET", "POST"])
def editar_receta(nombre):
    recetas = cargar_recetas()
    slug = nombre.lower()
    receta = next((r for r in recetas if r["name"].lower().replace(" ", "-") == slug), None)
    if not receta:
        abort(404)

    if request.method == "POST":
        ingredients_str = request.form.get("ingredients", "")
        steps_str = request.form.get("steps", "")

        ingredientes = [s.strip() for s in ingredients_str.splitlines() if s.strip()]
        pasos = [s.strip() for s in steps_str.splitlines() if s.strip()]

        def to_int(x, default=0):
            try:
                return int(x)
            except:
                return default

        receta.update({
            "name": request.form.get("name", "").strip(),
            "cuisine": request.form.get("cuisine", "").strip(),
            "rations": to_int(request.form.get("rations", 0)),
            "prep_time": to_int(request.form.get("prep_time", 0)),
            "category": request.form.get("category", "").strip() or "Principal",
            "ingredients": ingredientes,
            "steps": pasos
        })

        with open(ARCHIVO_RECETAS, "w", encoding="utf-8") as f:
            json.dump(recetas, f, ensure_ascii=False, indent=2)
        # Redirigimos al detalle con el nuevo slug por si cambió el nombre
        return redirect(url_for("ver_receta", nombre=receta["name"].lower().replace(" ", "-")))

    return render_template("form_receta.html", receta=receta)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Nada de debug/reloader en Render
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
