import tkinter as tk
from functools import partial
from recipe import recetario, cargar_recetario, guardar_receta_individual, Recipe
from tkinter import messagebox, ttk

class RecetarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recetario")
        self.root.geometry("600x500")

        cargar_recetario()

        self.frame_contenido = tk.Frame(self.root)
        self.frame_contenido.pack(fill="both", expand=True)

        self.mostrar_inicio()

    def limpiar_contenido(self):
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.limpiar_contenido()
        frame = tk.Frame(self.frame_contenido)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Bienvenido a tu Recetario", font=("Arial", 18)).pack(pady=20)
        tk.Button(frame, text="Ver recetas", width=20, command=self.mostrar_lista_recetas).pack(pady=10)
        tk.Button(frame, text="Añadir receta", width=20, command=self.mostrar_formulario_receta).pack(pady=10)

    def mostrar_lista_recetas(self):
        self.limpiar_contenido()

        canvas = tk.Canvas(self.frame_contenido)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Scroll dinámico
        def actualizar_scroll(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", actualizar_scroll)

        # Scroll con la rueda del ratón
        def scroll_wheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", scroll_wheel)

        busqueda_var = tk.StringVar()
        buscar_en_var = tk.StringVar(value="nombre")
        ordenar_var = tk.StringVar(value="categoria")

        # Buscar
        fila_buscar = tk.Frame(frame)
        fila_buscar.grid(row=0, column=0, columnspan=5, sticky="w", pady=5)

        tk.Label(fila_buscar, text="Buscar:").pack(side="left", padx=(0, 5))
        entry_buscar = tk.Entry(fila_buscar, textvariable=busqueda_var, width=30)
        entry_buscar.pack(side="left", padx=(0, 10))
        tk.Label(fila_buscar, text="en").pack(side="left", padx=(0, 5))
        tk.Radiobutton(fila_buscar, text="Nombre", variable=buscar_en_var, value="nombre").pack(side="left", padx=2)
        tk.Radiobutton(fila_buscar, text="Ingredientes", variable=buscar_en_var, value="ingredientes").pack(side="left", padx=2)

        # Ordenar por
        fila_orden = tk.Frame(frame)
        fila_orden.grid(row=1, column=0, columnspan=5, sticky="w", pady=5)

        tk.Label(fila_orden, text="Ordenar por:").pack(side="left", padx=(0, 5))
        tk.Radiobutton(fila_orden, text="Categoría", variable=ordenar_var, value="categoria").pack(side="left", padx=2)
        tk.Radiobutton(fila_orden, text="Cocina", variable=ordenar_var, value="cocina").pack(side="left", padx=2)
        tk.Radiobutton(fila_orden, text="Alfabético", variable=ordenar_var, value="alfabetico").pack(side="left", padx=2)

        # Separador
        ttk.Separator(frame, orient="horizontal").grid(row=2, column=0, columnspan=5, sticky="ew", pady=10)

        # Área de recetas
        frame_recetas = tk.Frame(frame)
        frame_recetas.grid(row=3, column=0, columnspan=5, sticky="nsew")

        def actualizar_listado(*args):
            for widget in frame_recetas.winfo_children():
                widget.destroy()

            texto = busqueda_var.get().lower().strip()
            campo = buscar_en_var.get()
            metodo = ordenar_var.get()

            # Filtrado
            recetas_filtradas = []
            for r in recetario:
                if not texto:
                    recetas_filtradas.append(r)
                elif campo == "nombre" and texto in r.name.lower():
                    recetas_filtradas.append(r)
                elif campo == "ingredientes" and any(texto in ing["nombre"].lower() for ing in r.ingredients):
                    recetas_filtradas.append(r)

            # Ordenación
            if metodo == "categoria":
                recetas_filtradas.sort(key=lambda r: (r.category, r.name.lower()))
                agrupar = lambda r: r.category
            elif metodo == "cocina":
                recetas_filtradas.sort(key=lambda r: (r.cuisine, r.name.lower()))
                agrupar = lambda r: r.cuisine
            else:
                recetas_filtradas.sort(key=lambda r: r.name.lower())
                agrupar = lambda r: ""

            actual = None
            for r in recetas_filtradas:
                clave = agrupar(r)
                if clave != actual and clave:
                    actual = clave
                    tk.Label(frame_recetas, text=clave.upper(), font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 0))
                fila = tk.Frame(frame_recetas)
                fila.pack(fill="x", pady=2)
                tk.Label(fila, text=r.name, anchor="w", width=40).pack(side="left")
                tk.Button(fila, text="Ver receta", command=partial(self.mostrar_detalle_receta, r)).pack(side="right")

        # Eventos
        busqueda_var.trace_add("write", actualizar_listado)
        buscar_en_var.trace_add("write", actualizar_listado)
        ordenar_var.trace_add("write", actualizar_listado)

        actualizar_listado()

        tk.Button(frame, text="Volver", command=lambda: [
            canvas.unbind_all("<MouseWheel>"),
            self.mostrar_inicio()
        ]).grid(row=4, column=0, columnspan=5, pady=10)

    def mostrar_detalle_receta(self, receta):
        self.limpiar_contenido()

        # === Scroll limpio sin fondo ===
        canvas = tk.Canvas(self.frame_contenido)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        frame = tk.Frame(canvas, bg="#ffffff", bd=0)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Actualiza área scrollable
        def actualizar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", actualizar_scroll)

        # Scroll con rueda del ratón
        def scroll(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", scroll)

        # Título
        tk.Label(frame, text=receta.name, font=("Arial", 16, "bold")).pack(pady=(0, 10))

        # Info básica
        def fila_info(etiqueta, valor):
            contenedor = tk.Frame(frame)
            contenedor.pack(anchor="w")
            tk.Label(contenedor, text=etiqueta, font=("Arial", 12, "bold")).pack(side="left")
            tk.Label(contenedor, text=valor, font=("Arial", 12)).pack(side="left")

        if receta.cuisine:
            fila_info("Cocina: ", receta.cuisine)
        if receta.rations:
            fila_info("Raciones: ", receta.rations)
        if receta.prep_time:
            fila_info("Tiempo: ", f"{receta.prep_time} min")
        if receta.category:
            fila_info("Categoría: ", receta.category)

        # Separador antes de ingredientes
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)

        def formatear_cantidad(cantidad):
            try:
                cantidad = float(cantidad)
                if cantidad.is_integer():
                    return str(int(cantidad))
                else:
                    return str(cantidad).rstrip("0").rstrip(".")  # Elimina ceros y puntos finales
            except:
                return cantidad  # Por si es algo raro como "½" directamente

        # Ingredientes
        tk.Label(frame, text="Ingredientes:", font=("Arial", 12, "bold")).pack(anchor="w")

        for ing in receta.ingredients:
            nombre = ing.get("nombre", "")
            cantidad = ing.get("cantidad", "")
            unidad = ing.get("unidad", "")
            nota = ing.get("nota", "")

            texto = f"• {nombre}"
            if cantidad:
                cantidad_str = formatear_cantidad(cantidad)
                if unidad == "unidad":
                    unidad_str = "unidad" if cantidad_str == "1" else "unidades"
                else:
                    unidad_str = unidad
                texto += f" ({cantidad_str} {unidad_str})"
                if nota:
                    texto += f" – {nota}"

            tk.Label(frame, text=texto, font=("Arial", 12)).pack(anchor="w", padx=10)

        # Separador antes de pasos
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)

        # Pasos
        if receta.steps:
            tk.Label(frame, text="Pasos:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
            for i, paso in enumerate(receta.steps, 1):
                paso_frame = tk.Frame(frame)
                paso_frame.pack(anchor="w", padx=10, pady=(2, 8))
                tk.Label(paso_frame, text=f"{i}.", font=("Arial", 12, "bold")).pack(anchor="nw", side="left", padx=(0, 5))
                tk.Label(paso_frame, text=paso, font=("Arial", 12), wraplength=500, justify="left").pack(anchor="w", side="left")

        # Botones de acción
        botones = tk.Frame(frame)
        botones.pack(pady=20)

        tk.Button(botones, text="Volver", command=lambda: [
            canvas.unbind_all("<MouseWheel>"),
            self.mostrar_lista_recetas()
        ]).pack(side="left", padx=5)

        def modificar():
            canvas.unbind_all("<MouseWheel>")
            self.mostrar_formulario_receta(modo="editar", receta_original=receta)

        tk.Button(botones, text="Modificar receta", command=modificar).pack(side="left", padx=5)


    def mostrar_formulario_receta(self, modo="crear", receta_original=None):
        self.limpiar_contenido()

        canvas = tk.Canvas(self.frame_contenido)
        scrollbar = tk.Scrollbar(self.frame_contenido, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        titulo = "Modificar receta" if modo == "editar" else "Añadir nueva receta"
        tk.Label(scroll_frame, text=titulo, font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        label_width = 20
        entry_width = 40

        tk.Label(scroll_frame, text="Nombre:", width=label_width, anchor="e").grid(row=1, column=0, padx=10, pady=5)
        entry_nombre = tk.Entry(scroll_frame, width=entry_width)
        entry_nombre.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(scroll_frame, text="Cocina:", width=label_width, anchor="e").grid(row=2, column=0, padx=10, pady=5)
        cocinas = ["Española", "Francesa", "Italiana", "Griega", "Japonesa", "China", "Tailandesa", "India", "Americana", "Mexicana"]
        cocina_var = tk.StringVar(value=cocinas[0])
        tk.OptionMenu(scroll_frame, cocina_var, *cocinas).grid(row=2, column=1, padx=10, pady=5, sticky="w")

        tk.Label(scroll_frame, text="Raciones:", width=label_width, anchor="e").grid(row=3, column=0, padx=10, pady=5)
        entry_raciones = tk.Entry(scroll_frame, width=entry_width)
        entry_raciones.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        tk.Label(scroll_frame, text="Tiempo (min):", width=label_width, anchor="e").grid(row=4, column=0, padx=10, pady=5)
        entry_tiempo = tk.Entry(scroll_frame, width=entry_width)
        entry_tiempo.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        tk.Label(scroll_frame, text="Categoría:", width=label_width, anchor="e").grid(row=5, column=0, padx=10, pady=5)
        categorias = ["Entrante", "Principal", "Acompañamiento", "Postre", "Salsa"]
        categoria_var = tk.StringVar(value=categorias[0])
        tk.OptionMenu(scroll_frame, categoria_var, *categorias).grid(row=5, column=1, padx=10, pady=5, sticky="w")

        # === INGREDIENTES ===
        tk.Label(scroll_frame, text="Número de ingredientes:", width=label_width, anchor="e").grid(row=6, column=0,
                                                                                                   padx=10, pady=5)
        num_ing_var = tk.IntVar(value=1)
        tk.Spinbox(scroll_frame, from_=1, to=20, textvariable=num_ing_var, width=5,
                   command=lambda: actualizar_ingredientes()).grid(row=6, column=1, padx=10, pady=5, sticky="w")

        tk.Label(scroll_frame, text="Ingredientes:", width=label_width, anchor="ne").grid(row=7, column=0, padx=10,
                                                                                          pady=5, sticky="ne")
        frame_ingredientes = tk.Frame(scroll_frame)
        frame_ingredientes.grid(row=7, column=1, padx=10, pady=5, sticky="w")

        num_pasos_var = tk.IntVar(value=1)

        if modo == "editar" and receta_original:
            entry_nombre.insert(0, receta_original.name)
            cocina_var.set(receta_original.cuisine)
            entry_raciones.insert(0, receta_original.rations)
            entry_tiempo.insert(0, receta_original.prep_time)
            categoria_var.set(receta_original.category)
            num_ing_var.set(len(receta_original.ingredients))
            num_pasos_var.set(len(receta_original.steps))

        entradas_ingredientes = []

        def actualizar_ingredientes():
            previos = [(n.get(), c.get(), u.get(), o.get()) for n, c, u, o in entradas_ingredientes]

            for widget in frame_ingredientes.winfo_children():
                widget.destroy()
            entradas_ingredientes.clear()

            for i in range(num_ing_var.get()):
                fila = tk.Frame(frame_ingredientes)
                fila.pack(anchor="w", pady=2)
                tk.Label(fila, text=f"{i + 1}.", width=3, anchor="e").pack(side="left")

                nombre = tk.Entry(fila, width=25)
                nombre.pack(side="left", padx=2)
                cantidad = tk.Entry(fila, width=6)
                cantidad.pack(side="left", padx=2)
                unidad_var = tk.StringVar(value="g")
                unidad = tk.OptionMenu(fila, unidad_var, "g", "ml", "L", "cda", "cdta", "unidad", "pizca")
                unidad.pack(side="left", padx=2)

                # Añadir campo de nota
                nota = tk.Entry(fila, width=15, fg="gray")
                nota.insert(0, "nota...")

                def on_focus_in(event, entry=nota):
                    if entry.get() == "nota...":
                        entry.delete(0, tk.END)
                        entry.config(fg="black")

                def on_focus_out(event, entry=nota):
                    if entry.get().strip() == "":
                        entry.insert(0, "nota...")
                        entry.config(fg="gray")

                nota.bind("<FocusIn>", on_focus_in)
                nota.bind("<FocusOut>", on_focus_out)
                nota.pack(side="left", padx=2)

                # Cargar datos previos si existen
                valor_nota = ""
                if modo == "editar" and receta_original and i < len(receta_original.ingredients):
                    nombre.insert(0, receta_original.ingredients[i].get("nombre", ""))
                    cantidad_valor = receta_original.ingredients[i].get("cantidad", "")
                    if cantidad_valor is not None:
                        cantidad.insert(0, str(cantidad_valor))
                    unidad_var.set(receta_original.ingredients[i].get("unidad", "g"))
                    valor_nota = receta_original.ingredients[i].get("nota", "")
                elif i < len(previos):
                    nombre.insert(0, previos[i][0])
                    cantidad.insert(0, previos[i][1])
                    unidad_var.set(previos[i][2])
                    valor_nota = previos[i][3] if len(previos[i]) > 3 else ""

                # Aplicar nota (tanto si venía de receta_original como de previos)
                if not valor_nota or valor_nota == "nota...":
                    nota.delete(0, tk.END)
                    nota.insert(0, "nota...")
                    nota.config(fg="gray")
                else:
                    nota.delete(0, tk.END)
                    nota.insert(0, valor_nota)
                    nota.config(fg="black")

                entradas_ingredientes.append((nombre, cantidad, unidad_var, nota))

        actualizar_ingredientes()

        # === PASOS ===
        tk.Label(scroll_frame, text="Número de pasos:", width=label_width, anchor="e").grid(row=8, column=0, padx=10, pady=5)
        tk.Spinbox(scroll_frame, from_=1, to=20, textvariable=num_pasos_var, width=5,
                   command=lambda: actualizar_pasos()).grid(row=8, column=1, padx=10, pady=5, sticky="w")

        tk.Label(scroll_frame, text="Pasos:", width=label_width, anchor="ne").grid(row=9, column=0, padx=10, pady=5,
                                                                                   sticky="ne")
        frame_pasos = tk.Frame(scroll_frame)
        frame_pasos.grid(row=9, column=1, padx=10, pady=5, sticky="w")

        entradas_pasos = []

        def actualizar_pasos():
            textos_previos = [txt.get("1.0", tk.END).strip() for txt in entradas_pasos]

            for widget in frame_pasos.winfo_children():
                widget.destroy()
            entradas_pasos.clear()

            for i in range(num_pasos_var.get()):
                paso_frame = tk.Frame(frame_pasos)
                paso_frame.pack(anchor="w", pady=4)
                tk.Label(paso_frame, text=f"{i + 1}.", width=3, anchor="ne").pack(side="left")
                txt = tk.Text(paso_frame, width=40, height=3)
                txt.pack(side="left")
                if i < len(textos_previos):
                    txt.insert("1.0", textos_previos[i])
                entradas_pasos.append(txt)

        actualizar_pasos()

        if modo == "editar" and receta_original:
            for i, paso in enumerate(receta_original.steps):
                entradas_pasos[i].insert("1.0", paso)

        # === BOTONES ===
        def cancelar():
            self.mostrar_inicio()

        def guardar():
            nombre = entry_nombre.get().strip()
            import re
            if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 \-]+", nombre):
                messagebox.showwarning("Error", "El nombre solo puede contener letras, números, espacios y guiones.")
                return

            try:
                raciones = int(entry_raciones.get())
                tiempo = int(entry_tiempo.get())
            except ValueError:
                messagebox.showwarning("Error", "Raciones y tiempo deben ser números enteros.")
                return

            ingredientes = []
            for nombre_ing, cant_ing, unidad_var, nota in entradas_ingredientes:
                nombre_i = nombre_ing.get().strip()
                unidad = unidad_var.get()
                if not nombre_i or nombre_i.isdigit():
                    messagebox.showwarning("Error", "Los nombres de ingredientes deben tener texto.")
                    return
                nombre_i = nombre_i.lower().capitalize()
                if unidad == "pizca":
                    cantidad = None
                else:
                    try:
                        cantidad_raw = cant_ing.get().strip()
                        if "/" in cantidad_raw:
                            num, den = cantidad_raw.split("/")
                            cantidad = round(float(num) / float(den), 2)
                        else:
                            cantidad = float(cantidad_raw)
                    except ValueError:
                        messagebox.showwarning("Error", f"Cantidad inválida en ingrediente '{nombre_i}'.")
                        return
                ingredientes.append({"nombre": nombre_i, "cantidad": cantidad, "unidad": unidad, "nota": "" if nota.get().strip() == "nota..." else nota.get().strip()})

            pasos = [txt.get("1.0", "end").strip() for txt in entradas_pasos if txt.get("1.0", "end").strip()]
            if not pasos:
                messagebox.showwarning("Error", "Debes indicar al menos un paso.")
                return

            receta = Recipe(
                name=nombre,
                cuisine=cocina_var.get(),
                rations=raciones,
                ingredients=ingredientes,
                steps=pasos,
                prep_time=tiempo,
                category=categoria_var.get()
            )
            if modo == "editar" and receta_original in recetario:
                recetario[recetario.index(receta_original)] = receta
            else:
                recetario.append(receta)
            guardar_receta_individual(receta)
            tk.messagebox.showinfo("Guardado", f"Receta '{nombre}' guardada correctamente.")
            self.mostrar_lista_recetas()

        frame_botones = tk.Frame(scroll_frame)
        frame_botones.grid(row=10, column=1, pady=20, sticky="w", padx=10)

        tk.Button(frame_botones, text="Guardar receta", command=guardar).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Cancelar", command=cancelar).pack(side="left", padx=5)

        if modo == "editar":
            def eliminar():
                confirmar = messagebox.askyesno("Eliminar receta", "¿Estás seguro de que quieres eliminar esta receta?")
                if confirmar and receta_original in recetario:
                    recetario.remove(receta_original)
                    guardar_receta_individual(receta)
                    messagebox.showinfo("Receta eliminada", "La receta se ha eliminado correctamente.")
                    self.mostrar_lista_recetas()

            tk.Button(scroll_frame, text="Eliminar", command=eliminar, fg="red").grid(row=11, column=1, sticky="e",
                                                                                      pady=(0, 10))


if __name__ == "__main__":
    root = tk.Tk()
    app = RecetarioApp(root)
    root.mainloop()