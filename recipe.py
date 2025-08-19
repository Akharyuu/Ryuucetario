import json
import os
from db import get_recipes, add_recipe

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
    # en vez de sobrescribir todo como JSON,
    # insertamos una a una en la tabla
    for r in recetario:
        add_recipe({
            "nombre": r.name,
            "cocina": r.cuisine,
            "raciones": r.rations,
            "ingredientes": ", ".join(r.ingredients),
            "pasos": r.steps,
            "tiempo": r.prep_time,
            "categoria": r.category
        })

def cargar_recetario():
    datos = get_recipes()
    for r in datos:
        receta = Recipe(
            r["nombre"],
            r["cocina"],
            r["raciones"],
            r["ingredientes"].split(", "),
            r["pasos"],
            r.get("tiempo", ""),
            r.get("categoria", "Principal")
        )
        recetario.append(receta)

