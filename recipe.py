from db import get_recipes, add_recipe
import json

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

def cargar_recetario():
    datos = get_recipes()
    recetario.clear()
    for r in datos:
        receta = Recipe(
            name=r["nombre"],
            cuisine=r["cocina"],
            rations=r["raciones"],
            ingredients=json.loads(r["ingredientes"]) if r.get("ingredientes") else [],
            steps=json.loads(r["pasos"]) if r.get("pasos") else [],
            prep_time=r.get("tiempo", ""),
            category=r.get("categoria", "Principal"),
        )
        recetario.append(receta)

def guardar_receta_individual(receta):
    add_recipe({
        "nombre": receta.name,
        "cocina": receta.cuisine,
        "raciones": receta.rations,
        "ingredientes": json.dumps(receta.ingredients, ensure_ascii=False),
        "pasos": json.dumps(receta.steps, ensure_ascii=False),
        "tiempo": receta.prep_time,
        "categoria": receta.category,
    })
