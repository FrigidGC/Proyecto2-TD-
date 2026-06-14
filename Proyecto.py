import tkinter as tk

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
    "Medieval":   {"color": "#8B4513", "descripcion": "La vieja confiable"},
    "Futurista":  {"color": "#00BFFF", "descripcion": "2027"},
    "Naturaleza": {"color": "#228B22", "descripcion": "Poder de la naturaleza"},
}


class VentanaFacciones:
    """
    Ventana para que el jugador elija su faccion antes de iniciar la partida.
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

        # Frame con las opciones de faccion
        frame_opciones = tk.Frame(self.ventana)
        frame_opciones.pack(padx=20, pady=4)

        for nombre, datos in FACCIONES.items():
            fila = tk.Frame(frame_opciones, bd=1, relief="groove", padx=8, pady=6)
            fila.pack(fill="x", pady=3)

            rb = tk.Radiobutton(fila, text=nombre, variable=self.seleccion,
                                value=nombre, font=("Arial", 10, "bold"),
                                fg=datos["color"])
            rb.pack(side="left")

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


class Interfaz:
    def __init__(self, jugador, faccion, mapa):
        self.jugador = jugador
        self.faccion = faccion
        self.mapa    = mapa

        self.root = tk.Tk()
        self.root.title("Defensa de Torres")
        self.crear_interfaz()

    def crear_interfaz(self):
        canvas = tk.Canvas(self.root, width=500, height=300)
        canvas.pack()

        canvas.create_text(250, 100, text="Defensa de Torres",
                           fill="gold", font=("Arial", 30, "bold"))
        canvas.create_text(250, 145, text="Proyecto I",
                           fill="#aabbff", font=("Arial", 14))

        self.label_jugador1 = tk.Label(self.root, text=f"Jugador: {self.jugador}", anchor="nw")
        self.label_jugador1.pack()


# TEMPORAL: mostrar faccion y mapa seleccionados (en vez de "—")
        self.label_faccion = tk.Label(self.root, text=f"Faccion: {self.faccion}", anchor="nw")
        self.label_faccion.pack()

        self.label_mapa = tk.Label(self.root, text=f"Mapa: {self.mapa}", anchor="nw")
        self.label_mapa.pack()
#################################################################

        self.boton_login = tk.Button(self.root, text="Iniciar sesion / Registrarse",
                                     command=self.abrir_login)
        self.boton_login.pack(pady=4)

        self.boton_iniciar = tk.Button(self.root, text="Iniciar Juego",
                                       command=self.iniciar_juego, state="disabled")
        self.boton_iniciar.pack(pady=4)

        # self.boton_ver_puntajes = tk.Button(self.root, text="Ver Puntajes",
        #                                     command=self.ver_puntajes)
        # self.boton_ver_puntajes.pack()

        self.root.mainloop()

    def abrir_login(self):
        VentanaLogin(self.root, on_exito=self.al_autenticarse)

    def al_autenticarse(self, usuario):
        self.jugador = usuario
        self.label_jugador1.config(text=f"Jugador: {self.jugador}")
        self.boton_iniciar.config(state="normal")
        self.boton_login.config(state="disabled")

    def iniciar_juego(self):
        VentanaFacciones(self.root, jugador=self.jugador,
                         on_exito=self.al_elegir_faccion)

    def al_elegir_faccion(self, faccion):
        self.faccion = faccion
        self.label_faccion.config(text=f"Faccion: {self.faccion}")
        # TODO: abrir seleccion de mapa / rol


j = Interfaz(jugador="—", faccion=1, mapa=0)