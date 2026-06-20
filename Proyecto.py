import tkinter as tk
from tkinter import messagebox

ARCHIVO_JUGADORES = "jugadores.txt"


def cargar_jugadores():
    """
    Lee el archivo .txt y devuelve un diccionario con los jugadores.
    Formato de cada linea: usuario,contrasena,victorias_defensor,victorias_atacante
    """
    jugadores = {}
    try:
        with open(ARCHIVO_JUGADORES, "r") as f:
            for linea in f:
                linea = linea.strip()
                if linea == "":
                    continue
                partes = linea.split(",")
                if len(partes) != 4:
                    continue
                usuario, contrasena, vic_def, vic_atac = partes
                jugadores[usuario] = {
                    "contrasena":         contrasena,
                    "victorias_defensor": int(vic_def),
                    "victorias_atacante": int(vic_atac)
                }
    except FileNotFoundError:
        pass
    return jugadores

def guardar_jugadores(jugadores):
    """
    Escribe todos los jugadores en el archivo .txt.
    Formato de cada linea: usuario,contrasena,victorias_defensor,victorias_atacante
    """
    with open(ARCHIVO_JUGADORES, "w") as f:
        for usuario, datos in jugadores.items():
            linea = (f"{usuario},"
                     f"{datos['contrasena']},"
                     f"{datos['victorias_defensor']},"
                     f"{datos['victorias_atacante']}\n")
            f.write(linea)


class VentanaLogin:
    """
    Ventana emergente para iniciar sesion o registrarse.
    Al autenticarse con exito llama a on_exito(usuario).
    El rol (defensor o atacante) lo determina el slot desde el que se abre
    esta ventana, no la cuenta en si misma. Los roles son fijos durante
    toda la partida; para invertirlos, cada jugador debe iniciar sesion
    en el slot contrario en la siguiente partida.
    """
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
            "contrasena":         contrasena,
            "victorias_defensor": 0,
            "victorias_atacante": 0
        }
        guardar_jugadores(jugadores)
        self.ventana.destroy()
        self.on_exito(usuario)


FACCIONES = {
    "Medieval":   {"color": "#8B4513", "descripcion": "Muros de piedra y torres de madera."},
    "Futurista":  {"color": "#00BFFF", "descripcion": "Estructuras metalicas y energia laser."},
    "Naturaleza": {"color": "#228B22", "descripcion": "Torres organicas y muros de enredadera."},
}


class VentanaFacciones:
    """
    Ventana para que el jugador elija su faccion antes de iniciar la partida.
    Las 3 facciones estan siempre disponibles para ambos jugadores.
    Llama a on_exito(faccion_elegida) al confirmar.
    """
    def __init__(self, parent, jugador, on_exito):
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
            fila = tk.Frame(frame_opciones, bd=1, relief="groove", padx=8, pady=6)
            fila.pack(fill="x", pady=3)

            tk.Radiobutton(fila, text=nombre, variable=self.seleccion,
                           value=nombre, font=("Arial", 10, "bold"),
                           fg=datos["color"]).pack(side="left")

            tk.Label(fila, text=datos["descripcion"],
                     font=("Arial", 9), fg="#555555").pack(side="left", padx=(8, 0))

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


TAMANO_MAPA = 10  # cuadricula 10x10

# Valores posibles dentro de cada casilla de la matriz del mapa
CASILLA_VACIA  = 0
CASILLA_MURO   = 1
CASILLA_TORRE  = 2
CASILLA_BASE   = 3
CASILLA_CAMINO = 4

# Ubicacion fija de la base central (ultima fila, columna central)
BASE_FILA    = TAMANO_MAPA - 1
BASE_COLUMNA = TAMANO_MAPA // 2


def crear_mapa_vacio():
    """
    Crea la matriz del mapa (lista de listas) de TAMANO_MAPA x TAMANO_MAPA,
    todas las casillas inician vacias excepto la posicion de la base central.
    """
    mapa = [[CASILLA_VACIA for _ in range(TAMANO_MAPA)] for _ in range(TAMANO_MAPA)]
    mapa[BASE_FILA][BASE_COLUMNA] = CASILLA_BASE
    return mapa


# ----------------------------------------------------------------------
# Torres
# ----------------------------------------------------------------------
TIPOS_TORRE = {
    "Basica": {
        "costo":  50,
        "vida":   100,
        "dano":   10,
        "alcance": 2,
        "habilidad": "Ninguna",
        "turnos_habilidad": 0,
    },
    "Pesada": {
        "costo":  120,
        "vida":   250,
        "dano":   25,
        "alcance": 1,
        "habilidad": "Disparo doble",
        "turnos_habilidad": 3,
    },
    "Magica": {
        "costo":  90,
        "vida":   60,
        "dano":   5,
        "alcance": 3,
        "habilidad": "Congelar unidad",
        "turnos_habilidad": 4,
    },
}


class Torre:
    """
    Representa una torre colocada en el tablero por el defensor.
    El tipo determina sus estadisticas base (ver TIPOS_TORRE).
    """
    def __init__(self, tipo, fila, columna):
        if tipo not in TIPOS_TORRE:
            raise ValueError(f"Tipo de torre desconocido: {tipo}")

        datos = TIPOS_TORRE[tipo]
        self.tipo     = tipo
        self.fila     = fila
        self.columna  = columna
        self.vida     = datos["vida"]
        self.vida_max = datos["vida"]
        self.dano     = datos["dano"]
        self.alcance  = datos["alcance"]
        self.costo    = datos["costo"]
        self.habilidad = datos["habilidad"]
        self.turnos_habilidad = datos["turnos_habilidad"]
        self.turnos_restantes = 0  # contador hasta poder activar la habilidad

    def esta_viva(self):
        return self.vida > 0

    def recibir_dano(self, cantidad):
        self.vida = max(0, self.vida - cantidad)

    def puede_usar_habilidad(self):
        return self.turnos_restantes <= 0

    def activar_habilidad(self):
        """
        Activa la habilidad especial de la torre si esta disponible y
        reinicia su contador de turnos. La logica concreta de cada
        habilidad se implementara mas adelante.
        """
        if not self.puede_usar_habilidad():
            return False
        self.turnos_restantes = self.turnos_habilidad
        return True

    def pasar_turno(self):
        if self.turnos_restantes > 0:
            self.turnos_restantes -= 1

    def __repr__(self):
        return f"Torre({self.tipo}, fila={self.fila}, col={self.columna}, vida={self.vida})"


class Interfaz:
    def __init__(self):
        # Jugador 1 (defensor)
        self.jugador1 = "—"
        self.faccion1 = "—"
        # Jugador 2 (atacante)
        self.jugador2 = "—"
        self.faccion2 = "—"

        self.root = tk.Tk()
        self.root.title("Defensa de Torres")
        self.crear_interfaz()

    # ------------------------------------------------------------------
    # Construccion de la pantalla principal
    # ------------------------------------------------------------------
    def crear_interfaz(self):
        canvas = tk.Canvas(self.root, width=520, height=160)
        canvas.pack()
        canvas.create_text(260, 70,  text="Defensa de Torres",
                           fill="gold", font=("Arial", 30, "bold"))
        canvas.create_text(260, 115, text="Proyecto II",
                           fill="#aabbff", font=("Arial", 14))

        # ---- Jugador 1 ----
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

        # ---- Jugador 2 ----
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

        # ---- Nota de roles ----
        tk.Label(
            self.root,
            text="Los roles son fijos durante la partida.\n"
                 "Para invertirlos, inicien sesion en el slot contrario la proxima vez.",
            font=("Arial", 8), fg="#777777", justify="center"
        ).pack(pady=(0, 4))

        # ---- Boton iniciar ----
        self.boton_iniciar = tk.Button(self.root, text="Iniciar Juego",
                                       command=self.iniciar_juego,
                                       state="disabled", width=20)
        self.boton_iniciar.pack(pady=6)

        self.root.mainloop()

    # ------------------------------------------------------------------
    # Flujo Jugador 1
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Flujo Jugador 2
    # ------------------------------------------------------------------
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
                         on_exito=self.al_elegir_faccion2)

    def al_elegir_faccion2(self, faccion):
        self.faccion2 = faccion
        self.label_f2.config(text=f"Faccion: {faccion}")
        self.boton_iniciar.config(state="normal")

    # ------------------------------------------------------------------
    # Inicio de partida
    # ------------------------------------------------------------------
    def iniciar_juego(self):
        resumen = (
            f"Jugador 1 (Defensor): {self.jugador1}  [{self.faccion1}]\n"
            f"Jugador 2 (Atacante): {self.jugador2}  [{self.faccion2}]\n\n"
            "¿Comenzar la partida?"
        )
        if messagebox.askyesno("Confirmar partida", resumen, parent=self.root):
            # TODO: abrir VentanaTablero(self.root, ...)
            messagebox.showinfo("En construccion",
                                "El tablero de juego se implementara en el proximo avance.",
                                parent=self.root)


j = Interfaz()