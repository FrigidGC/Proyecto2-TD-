import tkinter as tk
from tkinter import messagebox

ARCHIVO_JUGADORES = "jugadores.txt"


# Se carga el archivo de jugadores en un diccionario
# formato de cada linea: usuario,contrasena,victorias_defensor,victorias_atacante
def cargar_jugadores():
    jugadores = {}
    try:
        with open(ARCHIVO_JUGADORES, "r") as f:
            for linea in f:
                linea = linea.strip()
                if linea == "":
                    continue
                partes = linea.split(",")
                if len(partes) != 4:
                    continue  # linea mal formada, la ignoramos
                usuario, contrasena, vic_def, vic_atac = partes
                jugadores[usuario] = {
                    "contrasena": contrasena,
                    "victorias_defensor": int(vic_def),
                    "victorias_atacante": int(vic_atac)
                }
    except FileNotFoundError:
        pass  # si no existe el archivo todavia, no hay jugadores guardados
    return jugadores


def guardar_jugadores(jugadores):
    with open(ARCHIVO_JUGADORES, "w") as f:
        for usuario, datos in jugadores.items():
            linea = f"{usuario},{datos['contrasena']},{datos['victorias_defensor']},{datos['victorias_atacante']}\n"
            f.write(linea)


class VentanaLogin:
    # ventana para iniciar sesion o registrar un usuario nuevo
    # el rol (defensor/atacante) NO depende de la cuenta, depende del slot
    # desde donde se llama esta ventana. osea si quieren jugar al reves
    # la otra partida, solo inician sesion en el otro slot y ya
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

    def _obtener_campos(self):
        return self.entry_usuario.get().strip(), self.entry_contrasena.get().strip()

    def iniciar_sesion(self):
        usuario, contrasena = self._obtener_campos()
        if not usuario or not contrasena:
            self.label_error.config(text="Completa todos los campos.")
            return

        jugadores = cargar_jugadores()
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

        jugadores = cargar_jugadores()
        if usuario in jugadores:
            self.label_error.config(text="El usuario ya existe.")
            return

        jugadores[usuario] = {
            "contrasena": contrasena,
            "victorias_defensor": 0,
            "victorias_atacante": 0
        }
        guardar_jugadores(jugadores)
        self.ventana.destroy()
        self.on_exito(usuario)


# Se definen las 3 facciones que pide el proyecto, cada una con su color para
# identificarla rapido en la interfaz y una descripcion corta
FACCIONES = {
    "Medieval":   {"color": "#8B4513", "descripcion": "Muros de piedra y torres de madera."},
    "Futurista":  {"color": "#00BFFF", "descripcion": "Estructuras metalicas y energia laser."},
    "Naturaleza": {"color": "#228B22", "descripcion": "Torres organicas y muros de enredadera."},
}


class VentanaFacciones:
    # Se crea la ventana de seleccion de faccion.
    # Si se pasa "faccion_bloqueada", esa opcion aparece deshabilitada
    # porque el otro jugador ya la eligio (el enunciado lo pide)
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

        for nombre, datos in FACCIONES.items():
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


# ---------------------------------------------------------
# MAPA DEL JUEGO
# Lo guardamos como una matriz: una lista que tiene adentro
# otras 10 listas (una por fila). Cada casilla guarda un numero
# que nos dice que hay ahi (vacio, muro, torre, etc).
# ---------------------------------------------------------
TAMANO_MAPA = 15  # el mapa es de 15x15 casillas

# En vez de usar 0, 1, 2... directamente en el codigo, se usan
# estos nombres para que sea mas facil de leer y de recordar
CASILLA_VACIA  = 0  # no hay nada, se puede construir ahi
CASILLA_MURO   = 1  # hay un muro
CASILLA_TORRE  = 2  # hay una torre
CASILLA_BASE   = 3  # es la base central, no se puede tocar
CASILLA_CAMINO = 4  # camino por donde entran los atacantes

# la base siempre esta en el mismo lugar: en la ultima fila,
# justo en el centro
BASE_FILA = TAMANO_MAPA - 1
BASE_COLUMNA = TAMANO_MAPA // 2


def crear_mapa_vacio():
    # Se crea una matriz de TAMANO_MAPA x TAMANO_MAPA, toda vacia
    mapa = []
    for fila in range(TAMANO_MAPA):
        mapa.append([CASILLA_VACIA] * TAMANO_MAPA)

    mapa[BASE_FILA][BASE_COLUMNA] = CASILLA_BASE  # se coloca la base
    return mapa


# ---------------------------------------------------------
# TORRES
# Por ahora solo manejamos los datos y la logica de las torres.
# Dibujarlas en el tablero lo hacemos mas adelante.
# ---------------------------------------------------------

# Aqui se guardan las estadisticas de cada tipo de torre.
# es como una tabla: el nombre de la torre y sus datos
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


class Torre:
    # esta clase representa UNA torre que el jugador puso en el mapa.
    # cuando se crea, le copiamos las estadisticas segun su tipo
    # (sacadas del diccionario TIPOS_TORRE de arriba)
    def __init__(self, tipo, fila, columna):
        if tipo not in TIPOS_TORRE:
            raise ValueError(f"Tipo de torre desconocido: {tipo}")

        datos = TIPOS_TORRE[tipo]  # aqui sacamos las stats de ese tipo

        self.tipo = tipo
        self.fila = fila          # en que fila del mapa esta
        self.columna = columna    # en que columna del mapa esta

        self.vida = datos["vida"]
        self.vida_max = datos["vida"]
        self.dano = datos["dano"]
        self.alcance = datos["alcance"]
        self.costo = datos["costo"]
        self.habilidad = datos["habilidad"]
        self.turnos_habilidad = datos["turnos_habilidad"]

        # esto cuenta cuantos turnos faltan para poder volver
        # a usar la habilidad especial. arranca en 0 (lista para usar)
        self.turnos_restantes = 0

    def esta_viva(self):
        # la torre sigue viva mientras le quede vida
        return self.vida > 0

    def recibir_dano(self, cantidad):
        # le restamos vida, pero nunca dejamos que baje de 0
        self.vida = self.vida - cantidad
        if self.vida < 0:
            self.vida = 0

    def puede_usar_habilidad(self):
        # solo puede usar la habilidad si ya paso el tiempo de espera
        return self.turnos_restantes <= 0

    def activar_habilidad(self):
        # si todavia esta en cooldown, no hacemos nada
        if not self.puede_usar_habilidad():
            return False

        # si se puede usar, reiniciamos el contador de espera
        # (el efecto de cada habilidad lo programamos mas adelante)
        self.turnos_restantes = self.turnos_habilidad
        return True

    def pasar_turno(self):
        # Cada turno que pasa, se baja el contador de espera en 1
        if self.turnos_restantes > 0:
            self.turnos_restantes -= 1

    def __repr__(self):
        # Esto es solo para que se vea bonito si se imprime la torre
        return f"Torre({self.tipo}, fila={self.fila}, col={self.columna}, vida={self.vida})"


class VentanaTablero:
    # Esta ventana muestra el mapa en pantalla como una cuadricula
    # de cuadritos de colores. Cada cuadrito representa una casilla
    # de la matriz "mapa". Tambien deja hacer click para construir.
    def __init__(self, parent):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Tablero de juego")
        self.ventana.resizable(False, False)

        # Se crea la matriz del mapa, todavia vacia
        self.mapa = crear_mapa_vacio()

        # Cuantos pixeles mide cada cuadrito en pantalla
        # (se bajo a 30 para que el mapa de 15x15 quepa bien)
        self.tamano_casilla = 30

        # El dibujo completo mide TAMANO_MAPA cuadritos de ancho y de alto
        ancho_total = TAMANO_MAPA * self.tamano_casilla
        alto_total = TAMANO_MAPA * self.tamano_casilla

        # El Canvas es el "lienzo" donde se va a dibujar el mapa
        self.canvas = tk.Canvas(self.ventana, width=ancho_total, height=alto_total)
        self.canvas.pack(padx=10, pady=10)

        # Se le avisa a Tkinter: "cuando hagan click en el canvas,
        # llama a la funcion al_hacer_click"
        self.canvas.bind("<Button-1>", self.al_hacer_click)

        # Se dibuja el mapa por primera vez al abrir la ventana
        self.dibujar_mapa()

    def al_hacer_click(self, evento):
        # Se convierte el pixel del click en fila/columna de la matriz,
        # dividiendo entre el tamano de cada cuadrito
        columna = evento.x // self.tamano_casilla
        fila = evento.y // self.tamano_casilla

        # Si esa casilla esta vacia, se pone un muro ahi
        if self.mapa[fila][columna] == CASILLA_VACIA:
            self.mapa[fila][columna] = CASILLA_MURO
            self.dibujar_mapa()

    def color_de_casilla(self, valor):
        # Esta funcion recibe el numero de una casilla (0, 1, 2...)
        # y devuelve de que color hay que pintarla en el canvas
        if valor == CASILLA_VACIA:
            return "#dddddd"      # gris claro = casilla libre
        elif valor == CASILLA_MURO:
            return "#8B4513"      # cafe = muro
        elif valor == CASILLA_TORRE:
            return "#4169E1"      # azul = torre
        elif valor == CASILLA_BASE:
            return "gold"         # dorado = la base, no se toca
        elif valor == CASILLA_CAMINO:
            return "#f0e68c"      # amarillo claro = camino
        else:
            return "white"        # por si acaso, color de respaldo

    def dibujar_mapa(self):
        self.canvas.delete("all")  # se borra lo anterior antes de redibujar

        for fila in range(TAMANO_MAPA):
            for columna in range(TAMANO_MAPA):
                valor = self.mapa[fila][columna]
                color = self.color_de_casilla(valor)

                # Posicion en pixeles de este cuadrito
                x1 = columna * self.tamano_casilla
                y1 = fila * self.tamano_casilla
                x2 = x1 + self.tamano_casilla
                y2 = y1 + self.tamano_casilla

                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color, outline="black")


class Interfaz:
    def __init__(self):
        # jugador 1 siempre defensor, jugador 2 siempre atacante
        self.jugador1 = "—"
        self.faccion1 = "—"
        self.jugador2 = "—"
        self.faccion2 = "—"

        self.root = tk.Tk()
        self.root.title("Defensa de Torres")
        self.crear_interfaz()

    def crear_interfaz(self):
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

        # aclaracion de que los roles no cambian a media partida
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
        self.boton_login2.config(state="normal")  # ya puede entrar el jugador 2

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
            VentanaTablero(self.root)


# Aqui arranca todo: al crear el objeto se abre la ventana principal
j = Interfaz()
