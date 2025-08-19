from db import get_recipes, add_recipe

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
            r["nombre"],
            r["cocina"],
            r["raciones"],
            r["ingredientes"].split(", "),
            r["pasos"],
            r.get("tiempo", ""),
            r.get("categoria", "Principal")
        )
        recetario.append(receta)

def guardar_receta_individual(receta):
    add_recipe({
        "nombre": receta.name,
        "cocina": receta.cuisine,
        "raciones": receta.rations,
        "ingredientes": ", ".join(receta.ingredients),
        "pasos": receta.steps,
        "tiempo": receta.prep_time,
        "categoria": receta.category
    })