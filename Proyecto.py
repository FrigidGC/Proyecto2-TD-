import tkinter as tk
from tkinter import messagebox


class VentanaLogin:
    # ventana para iniciar sesion o registrar un usuario nuevo
    # el rol depende del slot desde donde se abre, no de la cuenta

    ARCHIVO = "jugadores.txt"

    def __init__(self, parent, on_exito):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Inicio de sesion")
        self.ventana.resizable(False, False)
        self.on_exito = on_exito
        self.ventana.grab_set()

        tk.Label(self.ventana, text="Usuario:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.entry_usuario = tk.Entry(self.ventana, width=20)
        self.entry_usuario.grid(row=0, column=1, padx=10, pady=8)

        tk.Label(self.ventana, text="Contrasena:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.entry_contrasena = tk.Entry(self.ventana, show="*", width=20)
        self.entry_contrasena.grid(row=1, column=1, padx=10, pady=8)

        self.label_error = tk.Label(self.ventana, text="", fg="red")
        self.label_error.grid(row=2, column=0, columnspan=2)

        tk.Button(self.ventana, text="Iniciar sesion", width=14,
                  command=self.iniciar_sesion).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(self.ventana, text="Registrarse", width=14,
                  command=self.registrarse).grid(row=3, column=1, padx=10, pady=10)

    # --- manejo del archivo de jugadores ---

    def cargar_jugadores(self):
        # Se lee el archivo y se devuelve un diccionario con todos los jugadores
        jugadores = {}
        try:
            with open(self.ARCHIVO, "r") as f:
                for linea in f:
                    linea = linea.strip()
                    if linea == "":
                        continue
                    partes = linea.split(",")
                    if len(partes) != 4:
                        continue
                    usuario, contrasena, vic_def, vic_atac = partes
                    jugadores[usuario] = {
                        "contrasena": contrasena,
                        "victorias_defensor": int(vic_def),
                        "victorias_atacante": int(vic_atac)
                    }
        except FileNotFoundError:
            pass  # si el archivo no existe todavia, se devuelve vacio
        return jugadores

    def guardar_jugadores(self, jugadores):
        # Se escribe el diccionario de jugadores de vuelta al archivo
        with open(self.ARCHIVO, "w") as f:
            for usuario, datos in jugadores.items():
                linea = f"{usuario},{datos['contrasena']},{datos['victorias_defensor']},{datos['victorias_atacante']}\n"
                f.write(linea)

    # --- logica de los botones ---

    def _obtener_campos(self):
        return self.entry_usuario.get().strip(), self.entry_contrasena.get().strip()

    def iniciar_sesion(self):
        usuario, contrasena = self._obtener_campos()
        if not usuario or not contrasena:
            self.label_error.config(text="Completa todos los campos.")
            return

        jugadores = self.cargar_jugadores()
        if usuario not in jugadores:
            self.label_error.config(text="Usuario no existe.")
            return
        if jugadores[usuario]["contrasena"] != contrasena:
            self.label_error.config(text="Contrasena incorrecta.")
            return

        self.ventana.destroy()
        self.on_exito(usuario)

    def registrarse(self):
        usuario, contrasena = self._obtener_campos()
        if not usuario or not contrasena:
            self.label_error.config(text="Completa todos los campos.")
            return

        jugadores = self.cargar_jugadores()
        if usuario in jugadores:
            self.label_error.config(text="El usuario ya existe.")
            return

        jugadores[usuario] = {
            "contrasena": contrasena,
            "victorias_defensor": 0,
            "victorias_atacante": 0
        }
        self.guardar_jugadores(jugadores)
        self.ventana.destroy()
        self.on_exito(usuario)


class VentanaFacciones:
    # Se crea la ventana de seleccion de faccion.
    # Si se pasa "faccion_bloqueada", esa opcion aparece deshabilitada
    # porque el otro jugador ya la eligio (el enunciado lo pide)

    FACCIONES = {
        "Medieval":   {"color": "#8B4513", "descripcion": "Muros de piedra y torres de madera."},
        "Futurista":  {"color": "#00BFFF", "descripcion": "Estructuras metalicas y energia laser."},
        "Naturaleza": {"color": "#228B22", "descripcion": "Torres organicas y muros de enredadera."},
    }

    def __init__(self, parent, jugador, on_exito, faccion_bloqueada=None):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Seleccion de Faccion")
        self.ventana.resizable(False, False)
        self.ventana.grab_set()
        self.on_exito = on_exito

        tk.Label(self.ventana, text=f"Jugador: {jugador}",
                 font=("Arial", 12, "bold")).pack(pady=(12, 4))
        tk.Label(self.ventana, text="Elige tu faccion:",
                 font=("Arial", 11)).pack(pady=(0, 8))

        self.seleccion = tk.StringVar(value="")

        frame_opciones = tk.Frame(self.ventana)
        frame_opciones.pack(padx=20, pady=4)

        for nombre, datos in self.FACCIONES.items():
            bloqueada = (nombre == faccion_bloqueada)
            fila = tk.Frame(frame_opciones, bd=1, relief="groove", padx=8, pady=6)
            fila.pack(fill="x", pady=3)

            tk.Radiobutton(
                fila, text=nombre, variable=self.seleccion,
                value=nombre, font=("Arial", 10, "bold"),
                fg="#aaaaaa" if bloqueada else datos["color"],
                state="disabled" if bloqueada else "normal"
            ).pack(side="left")

            desc = datos["descripcion"] + (" [ya elegida]" if bloqueada else "")
            tk.Label(fila, text=desc,
                     font=("Arial", 9),
                     fg="#aaaaaa" if bloqueada else "#555555").pack(side="left", padx=(8, 0))

        self.label_error = tk.Label(self.ventana, text="", fg="red")
        self.label_error.pack()

        tk.Button(self.ventana, text="Confirmar faccion", width=18,
                  command=self.confirmar).pack(pady=10)

    def confirmar(self):
        if not self.seleccion.get():
            self.label_error.config(text="Debes seleccionar una faccion.")
            return
        self.ventana.destroy()
        self.on_exito(self.seleccion.get())


class Torre:
    # Se representa una torre colocada en el tablero por el defensor.
    # El tipo le da sus estadisticas base (sacadas de TIPOS_TORRE)

    TIPOS_TORRE = {
        "Basica": {
            "costo": 50,
            "vida": 100,
            "dano": 10,
            "alcance": 2,
            "habilidad": "Ninguna",
            "turnos_habilidad": 0,
        },
        "Pesada": {
            "costo": 120,
            "vida": 250,
            "dano": 25,
            "alcance": 1,
            "habilidad": "Disparo doble",
            "turnos_habilidad": 3,
        },
        "Magica": {
            "costo": 90,
            "vida": 60,
            "dano": 5,
            "alcance": 3,
            "habilidad": "Congelar unidad",
            "turnos_habilidad": 4,
        },
    }

    def __init__(self, tipo, fila, columna):
        if tipo not in self.TIPOS_TORRE:
            raise ValueError(f"Tipo de torre desconocido: {tipo}")

        datos = self.TIPOS_TORRE[tipo]
        self.tipo = tipo
        self.fila = fila
        self.columna = columna
        self.vida = datos["vida"]
        self.vida_max = datos["vida"]
        self.dano = datos["dano"]
        self.alcance = datos["alcance"]
        self.costo = datos["costo"]
        self.habilidad = datos["habilidad"]
        self.turnos_habilidad = datos["turnos_habilidad"]
        self.turnos_restantes = 0  # cuenta regresiva para usar la habilidad de nuevo

    def esta_viva(self):
        return self.vida > 0

    def recibir_dano(self, cantidad):
        # Se resta vida, pero no baja de 0
        self.vida = self.vida - cantidad
        if self.vida < 0:
            self.vida = 0

    def puede_usar_habilidad(self):
        return self.turnos_restantes <= 0

    def activar_habilidad(self):
        # Se activa el cooldown; el efecto de cada habilidad se programa despues
        if not self.puede_usar_habilidad():
            return False
        self.turnos_restantes = self.turnos_habilidad
        return True

    def pasar_turno(self):
        # Cada turno que pasa, se baja el contador de espera en 1
        if self.turnos_restantes > 0:
            self.turnos_restantes -= 1

    def __repr__(self):
        return f"Torre({self.tipo}, fila={self.fila}, col={self.columna}, vida={self.vida})"


class VentanaTablero:
    # Se muestra el tablero de juego: el mapa en cuadritos de colores,
    # un panel lateral para elegir que construir, y el dinero del defensor

    TAMANO_MAPA   = 15   # la cuadricula es de 15x15 casillas
    TAMANO_CASILLA = 38  # pixeles por cuadrito

    # valores posibles en cada casilla de la matriz
    VACIA  = 0
    MURO   = 1
    TORRE  = 2
    BASE   = 3
    CAMINO = 4

    # colores para pintar cada tipo de casilla
    COLORES = {
        0: "#dddddd",   # vacio = gris claro
        1: "#8B4513",   # muro = cafe
        2: "#4169E1",   # torre = azul
        3: "gold",      # base = dorado
        4: "#f0e68c",   # camino = amarillo
    }

    DINERO_INICIAL = 300  # con cuanto dinero arranca el defensor cada ronda

    def __init__(self, parent, jugador_defensor):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Tablero de juego")
        self.ventana.resizable(False, False)

        # Se guarda quien es el defensor para mostrarlo en pantalla
        self.jugador_defensor = jugador_defensor

        # Se crea la matriz del mapa toda vacia, con la base ya colocada
        self.mapa = self._crear_mapa()

        # Se guardan las torres que se van colocando en el tablero
        self.torres = []

        # Dinero disponible del defensor en esta ronda
        self.dinero = self.DINERO_INICIAL

        # Lo que el defensor tiene seleccionado para construir
        # puede ser "Muro", "Basica", "Pesada" o "Magica"
        self.seleccion = tk.StringVar(value="Muro")

        self._construir_ventana()
        self.dibujar_mapa()

    def _crear_mapa(self):
        # Se crea una matriz TAMANO_MAPA x TAMANO_MAPA llena de ceros (vacio)
        mapa = []
        for fila in range(self.TAMANO_MAPA):
            mapa.append([self.VACIA] * self.TAMANO_MAPA)

        # Se coloca la base fija en la ultima fila, columna del centro
        fila_base = self.TAMANO_MAPA - 1
        col_base  = self.TAMANO_MAPA // 2
        mapa[fila_base][col_base] = self.BASE
        return mapa

    def _construir_ventana(self):
        # Se divide la ventana en dos partes: el mapa a la izquierda
        # y el panel de construccion a la derecha
        frame_principal = tk.Frame(self.ventana)
        frame_principal.pack(padx=8, pady=8)

        # --- lado izquierdo: el canvas con el mapa ---
        tamano_canvas = self.TAMANO_MAPA * self.TAMANO_CASILLA
        self.canvas = tk.Canvas(frame_principal,
                                width=tamano_canvas, height=tamano_canvas)
        self.canvas.grid(row=0, column=0, padx=(0, 8))
        self.canvas.bind("<Button-1>", self.al_hacer_click)

        # --- lado derecho: panel de construccion ---
        panel = tk.Frame(frame_principal, bd=2, relief="groove", padx=8, pady=8)
        panel.grid(row=0, column=1, sticky="n")

        tk.Label(panel, text=f"Defensor:\n{self.jugador_defensor}",
                 font=("Arial", 10, "bold"), justify="center").pack(pady=(0, 8))

        # Se muestra el dinero disponible; se actualiza cada vez que se gasta
        self.label_dinero = tk.Label(panel, text=f"Dinero: ${self.dinero}",
                                     font=("Arial", 11), fg="green")
        self.label_dinero.pack(pady=(0, 10))

        # --- botones de seleccion de lo que se va a construir ---
        tk.Label(panel, text="Construir:", font=("Arial", 9, "bold")).pack(anchor="w")

        opciones = [
            ("Muro",   f"Muro  $10"),
            ("Basica", f"Torre Basica  $50"),
            ("Pesada", f"Torre Pesada  $120"),
            ("Magica", f"Torre Magica  $90"),
        ]

        for valor, texto in opciones:
            tk.Radiobutton(
                panel, text=texto, variable=self.seleccion,
                value=valor, anchor="w", font=("Arial", 9)
            ).pack(fill="x", pady=1)

        # Se muestra un mensaje de ayuda abajo del panel
        tk.Label(panel, text="\nHaz click en una\ncasilla gris\npara construir",
                 font=("Arial", 8), fg="#777777", justify="center").pack(pady=(10, 0))

    def al_hacer_click(self, evento):
        # Se convierte la posicion del click (en pixeles) a fila/columna de la matriz
        columna = evento.x // self.TAMANO_CASILLA
        fila    = evento.y // self.TAMANO_CASILLA

        # Se ignora si el click cae fuera de los limites del mapa
        if fila >= self.TAMANO_MAPA or columna >= self.TAMANO_MAPA:
            return

        # Solo se puede construir en casillas vacias
        if self.mapa[fila][columna] != self.VACIA:
            return

        construccion = self.seleccion.get()

        if construccion == "Muro":
            costo = 10
            if self.dinero < costo:
                messagebox.showwarning("Sin dinero", "No tienes dinero suficiente para un muro.",
                                       parent=self.ventana)
                return
            self.mapa[fila][columna] = self.MURO
            self.dinero -= costo

        else:
            # Se crea la torre del tipo seleccionado
            costo = Torre.TIPOS_TORRE[construccion]["costo"]
            if self.dinero < costo:
                messagebox.showwarning("Sin dinero",
                                       f"No tienes dinero suficiente para esta torre.",
                                       parent=self.ventana)
                return
            nueva_torre = Torre(construccion, fila, columna)
            self.torres.append(nueva_torre)
            self.mapa[fila][columna] = self.TORRE
            self.dinero -= costo

        # Se actualiza el label del dinero y se redibuja el mapa
        self.label_dinero.config(text=f"Dinero: ${self.dinero}")
        self.dibujar_mapa()

    def dibujar_mapa(self):
        self.canvas.delete("all")  # se borra lo anterior antes de redibujar

        for fila in range(self.TAMANO_MAPA):
            for columna in range(self.TAMANO_MAPA):
                valor = self.mapa[fila][columna]
                color = self.COLORES.get(valor, "white")

                # Posicion en pixeles de este cuadrito
                x1 = columna * self.TAMANO_CASILLA
                y1 = fila    * self.TAMANO_CASILLA
                x2 = x1 + self.TAMANO_CASILLA
                y2 = y1 + self.TAMANO_CASILLA

                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color, outline="black")

                # Si hay una torre en esta casilla, se escribe su inicial encima
                if valor == self.TORRE:
                    torre = self._torre_en(fila, columna)
                    if torre:
                        inicial = torre.tipo[0]  # "B", "P" o "M"
                        self.canvas.create_text(x1 + self.TAMANO_CASILLA // 2,
                                                y1 + self.TAMANO_CASILLA // 2,
                                                text=inicial, fill="white",
                                                font=("Arial", 10, "bold"))

    def _torre_en(self, fila, columna):
        # Se busca en la lista de torres cual esta en esa posicion
        for torre in self.torres:
            if torre.fila == fila and torre.columna == columna:
                return torre
        return None


class Interfaz:
    def __init__(self):
        # Se guardan los datos de ambos jugadores
        self.jugador1 = "—"
        self.faccion1 = "—"
        self.jugador2 = "—"
        self.faccion2 = "—"

        self.root = tk.Tk()
        self.root.title("Defensa de Torres")
        self._construir_ventana()

    def _construir_ventana(self):
        canvas = tk.Canvas(self.root, width=520, height=160)
        canvas.pack()
        canvas.create_text(260, 70, text="Defensa de Torres",
                           fill="gold", font=("Arial", 30, "bold"))
        canvas.create_text(260, 115, text="Proyecto II",
                           fill="#aabbff", font=("Arial", 14))

        # bloque jugador 1
        frame1 = tk.LabelFrame(self.root, text="Jugador 1 — Defensor",
                                padx=10, pady=6)
        frame1.pack(fill="x", padx=16, pady=(4, 2))

        self.label_j1 = tk.Label(frame1, text="Usuario: —", width=22, anchor="w")
        self.label_j1.grid(row=0, column=0, sticky="w")
        self.label_f1 = tk.Label(frame1, text="Faccion: —", width=22, anchor="w")
        self.label_f1.grid(row=1, column=0, sticky="w")

        self.boton_login1 = tk.Button(frame1, text="Iniciar sesion / Registrarse",
                                      width=26, command=self.abrir_login1)
        self.boton_login1.grid(row=0, column=1, rowspan=2, padx=(12, 0))

        # bloque jugador 2
        frame2 = tk.LabelFrame(self.root, text="Jugador 2 — Atacante",
                                padx=10, pady=6)
        frame2.pack(fill="x", padx=16, pady=(2, 8))

        self.label_j2 = tk.Label(frame2, text="Usuario: —", width=22, anchor="w")
        self.label_j2.grid(row=0, column=0, sticky="w")
        self.label_f2 = tk.Label(frame2, text="Faccion: —", width=22, anchor="w")
        self.label_f2.grid(row=1, column=0, sticky="w")

        self.boton_login2 = tk.Button(frame2, text="Iniciar sesion / Registrarse",
                                      width=26, command=self.abrir_login2,
                                      state="disabled")
        self.boton_login2.grid(row=0, column=1, rowspan=2, padx=(12, 0))

        # aclaracion de roles fijos
        tk.Label(
            self.root,
            text="Los roles son fijos durante la partida.\n"
                 "Para invertirlos, inicien sesion en el slot contrario la proxima vez.",
            font=("Arial", 8), fg="#777777", justify="center"
        ).pack(pady=(0, 4))

        self.boton_iniciar = tk.Button(self.root, text="Iniciar Juego",
                                       command=self.iniciar_juego,
                                       state="disabled", width=20)
        self.boton_iniciar.pack(pady=6)

        self.root.mainloop()

    # --- flujo jugador 1 ---
    def abrir_login1(self):
        VentanaLogin(self.root, on_exito=self.al_autenticar_j1)

    def al_autenticar_j1(self, usuario):
        self.jugador1 = usuario
        self.label_j1.config(text=f"Usuario: {usuario}")
        self.boton_login1.config(state="disabled")
        VentanaFacciones(self.root, jugador=usuario,
                         on_exito=self.al_elegir_faccion1)

    def al_elegir_faccion1(self, faccion):
        self.faccion1 = faccion
        self.label_f1.config(text=f"Faccion: {faccion}")
        self.boton_login2.config(state="normal")

    # --- flujo jugador 2 ---
    def abrir_login2(self):
        VentanaLogin(self.root, on_exito=self.al_autenticar_j2)

    def al_autenticar_j2(self, usuario):
        if usuario == self.jugador1:
            messagebox.showerror(
                "Error", "El jugador 2 no puede ser el mismo que el jugador 1.",
                parent=self.root)
            return
        self.jugador2 = usuario
        self.label_j2.config(text=f"Usuario: {usuario}")
        self.boton_login2.config(state="disabled")
        VentanaFacciones(self.root, jugador=usuario,
                         on_exito=self.al_elegir_faccion2,
                         faccion_bloqueada=self.faccion1)

    def al_elegir_faccion2(self, faccion):
        self.faccion2 = faccion
        self.label_f2.config(text=f"Faccion: {faccion}")
        self.boton_iniciar.config(state="normal")

    # --- arrancar partida ---
    def iniciar_juego(self):
        resumen = (
            f"Jugador 1 (Defensor): {self.jugador1}  [{self.faccion1}]\n"
            f"Jugador 2 (Atacante): {self.jugador2}  [{self.faccion2}]\n\n"
            "¿Comenzar la partida?"
        )
        if messagebox.askyesno("Confirmar partida", resumen, parent=self.root):
            VentanaTablero(self.root, jugador_defensor=self.jugador1)


# Aqui arranca todo: al crear el objeto se abre la ventana principal
Interfaz()
