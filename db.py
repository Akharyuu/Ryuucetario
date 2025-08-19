# db.py
from supabase import create_client, Client

url = "https://TU_PROJECT.supabase.co"   # 👉 pon tu URL real
key = "TU_ANON_KEY"                      # 👉 tu anon key

supabase: Client = create_client(url, key)

def get_recipes():
    res = supabase.table("recetas").select("*").execute()
    return res.data

def add_recipe(data):
    supabase.table("recetas").insert(data).execute()

def delete_recipe(recipe_id):
    supabase.table("recetas").delete().eq("id", recipe_id).execute()
