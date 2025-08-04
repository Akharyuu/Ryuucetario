import json
import os

ARCHIVO_RECETAS = "recetas.json"

class Recipe:

    def __init__(self, name, cuisine, rations, ingredients, steps, prep_time, category):
        self.name = name
        self.cuisine = cuisine
        self.rations = rations
        self.ingredients = ingredients
        self.steps = steps
        self.prep_time = prep_time
        self.category = category

recetario = []

def guardar_recetario():
    with open(ARCHIVO_RECETAS, "w", encoding="utf-8") as f:
        json.dump([r.__dict__ for r in recetario], f, ensure_ascii=False, indent=2)

def cargar_recetario():
    if os.path.exists(ARCHIVO_RECETAS):
        with open(ARCHIVO_RECETAS, "r", encoding="utf-8") as f:
            datos = json.load(f)
            for r in datos:
                receta = Recipe(
                    r["name"],
                    r["cuisine"],
                    r["rations"],
                    r["ingredients"],
                    r["steps"],
                    r.get("prep_time", 0),
                    r.get("category", "Principal")
                )
                recetario.append(receta)




