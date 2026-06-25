import tkinter as tk
from tkinter import messagebox


# =============================================================
# VENTANA DE LOGIN
# =============================================================
class VentanaLogin:
    # Se muestra una ventana emergente donde el jugador puede
    # iniciar sesion con una cuenta existente o crear una nueva.
    # El rol (defensor o atacante) NO depende de la cuenta,
    # sino del slot desde donde se abrio esta ventana.

    ARCHIVO = "jugadores.txt"  # nombre del archivo donde se guardan los jugadores

    def __init__(self, parent, on_exito):
        # "on_exito" es la funcion que se llama cuando el login es exitoso,
        # pasandole el nombre de usuario como argumento
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Inicio de sesion")
        self.ventana.resizable(False, False)
        self.on_exito = on_exito
        self.ventana.grab_set()  # bloquea la ventana principal mientras esta abierta

        # --- campos de texto ---
        tk.Label(self.ventana, text="Usuario:").grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.entry_usuario = tk.Entry(self.ventana, width=20)
        self.entry_usuario.grid(row=0, column=1, padx=10, pady=8)

        tk.Label(self.ventana, text="Contrasena:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.entry_contrasena = tk.Entry(self.ventana, show="*", width=20)  # show="*" oculta lo que se escribe
        self.entry_contrasena.grid(row=1, column=1, padx=10, pady=8)

        # label vacio que se usa para mostrar errores en rojo
        self.label_error = tk.Label(self.ventana, text="", fg="red")
        self.label_error.grid(row=2, column=0, columnspan=2)

        # --- botones ---
        tk.Button(self.ventana, text="Iniciar sesion", width=14,
                  command=self.iniciar_sesion).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(self.ventana, text="Registrarse", width=14,
                  command=self.registrarse).grid(row=3, column=1, padx=10, pady=10)

    # ----------------------------------------------------------
    # Manejo del archivo de jugadores
    # ----------------------------------------------------------

    def cargar_jugadores(self):
        # Se lee el archivo linea por linea y se arma un diccionario.
        # Cada clave es el nombre de usuario, y el valor son sus datos.
        jugadores = {}
        try:
            with open(self.ARCHIVO, "r") as f:
                for linea in f:
                    linea = linea.strip()
                    if linea == "":
                        continue  # se ignoran las lineas vacias
                    partes = linea.split(",")
                    if len(partes) != 4:
                        continue  # se ignoran lineas con formato incorrecto
                    usuario, contrasena, vic_def, vic_atac = partes
                    jugadores[usuario] = {
                        "contrasena": contrasena,
                        "victorias_defensor": int(vic_def),
                        "victorias_atacante": int(vic_atac)
                    }
        except FileNotFoundError:
            pass  # si el archivo no existe todavia, se devuelve el diccionario vacio
        return jugadores

    def guardar_jugadores(self, jugadores):
        # Se recorre el diccionario y se escribe cada jugador
        # como una linea en el archivo, separado por comas
        with open(self.ARCHIVO, "w") as f:
            for usuario, datos in jugadores.items():
                linea = f"{usuario},{datos['contrasena']},{datos['victorias_defensor']},{datos['victorias_atacante']}\n"
                f.write(linea)

    # ----------------------------------------------------------
    # Logica de los botones
    # ----------------------------------------------------------

    def _obtener_campos(self):
        # Se leen y limpian los espacios en blanco de los campos de texto
        return self.entry_usuario.get().strip(), self.entry_contrasena.get().strip()

    def iniciar_sesion(self):
        usuario, contrasena = self._obtener_campos()

        # Se valida que los campos no esten vacios
        if not usuario or not contrasena:
            self.label_error.config(text="Completa todos los campos.")
            return

        jugadores = self.cargar_jugadores()

        # Se verifica que el usuario exista en el archivo
        if usuario not in jugadores:
            self.label_error.config(text="Usuario no existe.")
            return

        # Se verifica que la contrasena sea correcta
        if jugadores[usuario]["contrasena"] != contrasena:
            self.label_error.config(text="Contrasena incorrecta.")
            return

        # Si todo esta bien, se cierra la ventana y se avisa al llamador
        self.ventana.destroy()
        self.on_exito(usuario)

    def registrarse(self):
        usuario, contrasena = self._obtener_campos()

        # Se valida que los campos no esten vacios
        if not usuario or not contrasena:
            self.label_error.config(text="Completa todos los campos.")
            return

        jugadores = self.cargar_jugadores()

        # No se permite registrar un nombre de usuario que ya existe
        if usuario in jugadores:
            self.label_error.config(text="El usuario ya existe.")
            return

        # Se agrega el nuevo jugador con 0 victorias y se guarda
        jugadores[usuario] = {
            "contrasena": contrasena,
            "victorias_defensor": 0,
            "victorias_atacante": 0
        }
        self.guardar_jugadores(jugadores)
        self.ventana.destroy()
        self.on_exito(usuario)


# =============================================================
# VENTANA DE SELECCION DE FACCION
# =============================================================
class VentanaFacciones:
    # Se muestra una ventana donde el jugador elige su faccion.
    # Si se pasa "faccion_bloqueada", esa opcion aparece deshabilitada
    # porque el otro jugador ya la eligio (requisito del enunciado).

    # Las 3 facciones disponibles con su color e identificacion visual
    FACCIONES = {
        "Medieval":   {"color": "#8B4513", "descripcion": "Muros de piedra y torres de madera."},
        "Futurista":  {"color": "#00BFFF", "descripcion": "Estructuras metalicas y energia laser."},
        "Naturaleza": {"color": "#228B22", "descripcion": "Torres organicas y muros de enredadera."},
    }

    def __init__(self, parent, jugador, on_exito, faccion_bloqueada=None):
        # "faccion_bloqueada" es la faccion que ya eligio el otro jugador (o None)
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Seleccion de Faccion")
        self.ventana.resizable(False, False)
        self.ventana.grab_set()
        self.on_exito = on_exito

        tk.Label(self.ventana, text=f"Jugador: {jugador}",
                 font=("Arial", 12, "bold")).pack(pady=(12, 4))
        tk.Label(self.ventana, text="Elige tu faccion:",
                 font=("Arial", 11)).pack(pady=(0, 8))

        # Se usa StringVar para saber cual opcion esta seleccionada
        self.seleccion = tk.StringVar(value="")

        frame_opciones = tk.Frame(self.ventana)
        frame_opciones.pack(padx=20, pady=4)

        # Se crea una fila por cada faccion
        for nombre, datos in self.FACCIONES.items():
            bloqueada = (nombre == faccion_bloqueada)  # True si ya la eligio el otro jugador
            fila = tk.Frame(frame_opciones, bd=1, relief="groove", padx=8, pady=6)
            fila.pack(fill="x", pady=3)

            # Si la faccion esta bloqueada, se muestra gris y deshabilitada
            tk.Radiobutton(
                fila, text=nombre, variable=self.seleccion,
                value=nombre, font=("Arial", 10, "bold"),
                fg="#aaaaaa" if bloqueada else datos["color"],
                state="disabled" if bloqueada else "normal"
            ).pack(side="left")

            # Si esta bloqueada, se avisa con "[ya elegida]"
            desc = datos["descripcion"] + (" [ya elegida]" if bloqueada else "")
            tk.Label(fila, text=desc,
                     font=("Arial", 9),
                     fg="#aaaaaa" if bloqueada else "#555555").pack(side="left", padx=(8, 0))

        # Label vacio para mostrar errores
        self.label_error = tk.Label(self.ventana, text="", fg="red")
        self.label_error.pack()

        tk.Button(self.ventana, text="Confirmar faccion", width=18,
                  command=self.confirmar).pack(pady=10)

    def confirmar(self):
        # Se verifica que el jugador haya seleccionado algo antes de continuar
        if not self.seleccion.get():
            self.label_error.config(text="Debes seleccionar una faccion.")
            return
        self.ventana.destroy()
        self.on_exito(self.seleccion.get())  # se devuelve la faccion elegida


# =============================================================
# CLASE TORRE
# =============================================================
class Torre:
    # Se representa una torre colocada en el tablero por el defensor.
    # Cada torre tiene un tipo ("Basica", "Pesada" o "Magica") que
    # determina sus estadisticas. Los datos de cada tipo estan
    # en el diccionario TIPOS_TORRE.

    TIPOS_TORRE = {
        "Basica": {
            "costo": 50,
            "vida": 100,
            "dano": 10,
            "alcance": 2,           # casillas de distancia a las que puede atacar
            "habilidad": "Ninguna",
            "turnos_habilidad": 0,  # 0 significa que no tiene habilidad especial
        },
        "Pesada": {
            "costo": 120,
            "vida": 250,
            "dano": 25,
            "alcance": 1,
            "habilidad": "Disparo doble",
            "turnos_habilidad": 3,  # se puede usar cada 3 turnos
        },
        "Magica": {
            "costo": 90,
            "vida": 60,
            "dano": 5,
            "alcance": 3,
            "habilidad": "Congelar unidad",
            "turnos_habilidad": 4,  # se puede usar cada 4 turnos
        },
    }

    def __init__(self, tipo, fila, columna):
        if tipo not in self.TIPOS_TORRE:
            raise ValueError(f"Tipo de torre desconocido: {tipo}")

        datos = self.TIPOS_TORRE[tipo]  # se sacan las stats del tipo elegido

        self.tipo    = tipo
        self.fila    = fila      # posicion en la matriz del mapa
        self.columna = columna

        self.vida     = datos["vida"]
        self.vida_max = datos["vida"]   # se guarda el maximo para saber cuanta vida tenia originalmente
        self.dano     = datos["dano"]
        self.alcance  = datos["alcance"]
        self.costo    = datos["costo"]
        self.habilidad        = datos["habilidad"]
        self.turnos_habilidad = datos["turnos_habilidad"]
        self.turnos_restantes = 0  # cuantos turnos faltan para poder usar la habilidad de nuevo

    def esta_viva(self):
        # Se devuelve True si la torre todavia tiene vida
        return self.vida > 0

    def recibir_dano(self, cantidad):
        # Se resta la vida recibida, pero no puede bajar de 0
        self.vida = self.vida - cantidad
        if self.vida < 0:
            self.vida = 0

    def puede_usar_habilidad(self):
        # La habilidad esta lista cuando el contador llega a 0
        return self.turnos_restantes <= 0

    def activar_habilidad(self):
        # Se intenta activar la habilidad. Si el cooldown no termino, no hace nada.
        # El efecto real de cada habilidad se programa en la fase de combate.
        if not self.puede_usar_habilidad():
            return False
        self.turnos_restantes = self.turnos_habilidad  # se reinicia el contador
        return True

    def pasar_turno(self):
        # Se llama al final de cada turno para bajar el contador de la habilidad
        if self.turnos_restantes > 0:
            self.turnos_restantes -= 1

    def __repr__(self):
        # Se usa para imprimir la torre de forma legible (util para depurar)
        return f"Torre({self.tipo}, fila={self.fila}, col={self.columna}, vida={self.vida})"


# =============================================================
# CLASE MURO
# =============================================================
class Muro:
    # Se representa un muro colocado en el tablero por el defensor.
    # Es mas sencillo que una torre: solo tiene vida y costo.
    # Su funcion es bloquear el paso de las unidades atacantes.

    COSTO    = 10  # precio para construir un muro
    VIDA_MAX = 50  # vida inicial de cada muro

    def __init__(self, fila, columna):
        self.fila    = fila     # posicion en la matriz del mapa
        self.columna = columna
        self.vida    = self.VIDA_MAX

    def esta_vivo(self):
        # Se devuelve True si el muro todavia tiene vida
        return self.vida > 0

    def recibir_dano(self, cantidad):
        # Se resta vida al muro, pero no puede bajar de 0
        self.vida = self.vida - cantidad
        if self.vida < 0:
            self.vida = 0

    def __repr__(self):
        return f"Muro(fila={self.fila}, col={self.columna}, vida={self.vida})"


# =============================================================
# VENTANA DEL TABLERO
# =============================================================
class VentanaTablero:
    # Se muestra el tablero de juego: una cuadricula de colores que
    # representa la matriz del mapa, mas un panel lateral donde el
    # defensor puede elegir que construir y ver su dinero disponible.

    TAMANO_MAPA    = 15   # la cuadricula es de 15x15 casillas
    TAMANO_CASILLA = 38   # cada cuadrito mide 38x38 pixeles en pantalla

    # Valores numericos que se guardan en cada casilla de la matriz.
    # Se usan nombres en vez de numeros sueltos para que el codigo sea legible.
    VACIA  = 0  # casilla libre, se puede construir ahi
    MURO   = 1  # hay un muro
    TORRE  = 2  # hay una torre
    BASE   = 3  # es la base central del defensor, no se puede tocar
    CAMINO = 4  # camino por donde entraran las unidades atacantes
    UNIDAD = 5  # hay una unidad atacante

    # Color de pantalla que le corresponde a cada valor de casilla
    COLORES = {
        0: "#dddddd",   # vacio = gris claro
        1: "#8B4513",   # muro = cafe
        2: "#4169E1",   # torre = azul
        3: "gold",      # base = dorado
        4: "#f0e68c",   # camino = amarillo claro
        5: "#cc0000",   # unidad = rojo
    }

    DINERO_INICIAL = 300  # dinero con el que arranca el defensor al inicio de cada ronda

    def __init__(self, parent, jugador_defensor, jugador_atacante):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Tablero de juego")
        self.ventana.resizable(False, False)

        self.jugador_defensor = jugador_defensor  # nombre del jugador defensor
        self.jugador_atacante = jugador_atacante  # nombre del jugador atacante

        # Se crea la matriz del mapa (15x15) con todas las casillas vacias,
        # excepto la base que ya se coloca en su posicion fija
        self.mapa = self._crear_mapa()

        # Lista donde se van guardando los objetos Torre que se colocan
        self.torres = []

        # Lista donde se van guardando los objetos Muro que se colocan
        self.muros = []

        # Lista donde se van guardando los objetos Unidad que coloca el atacante
        self.unidades = []

        # Fase actual del turno
        self.fase = "construccion"

        # Dinero del defensor
        self.dinero = self.DINERO_INICIAL

        # Dinero del atacante (mismo monto inicial)
        self.dinero_atacante = self.DINERO_INICIAL

        # Variable que guarda que esta seleccionado en el panel del defensor
        self.seleccion = tk.StringVar(value="Muro")

        # Variable que guarda que esta seleccionado en el panel del atacante
        self.seleccion_unidad = tk.StringVar(value="Soldado")

        self._construir_ventana()
        self.dibujar_mapa()  # se dibuja el mapa vacio al abrir la ventana

    # ----------------------------------------------------------
    # Creacion de la matriz del mapa
    # ----------------------------------------------------------

    def _crear_mapa(self):
        # Se arma la matriz fila por fila. Cada casilla empieza en VACIA (0).
        mapa = []
        for fila in range(self.TAMANO_MAPA):
            mapa.append([self.VACIA] * self.TAMANO_MAPA)

        # Se coloca la base en la ultima fila, justo en el centro
        fila_base = self.TAMANO_MAPA - 1
        col_base  = self.TAMANO_MAPA // 2
        mapa[fila_base][col_base] = self.BASE
        return mapa

    # ----------------------------------------------------------
    # Construccion de la interfaz del tablero
    # ----------------------------------------------------------

    def _construir_ventana(self):
        # La ventana se divide en dos columnas:
        # izquierda = el mapa | derecha = panel de construccion
        frame_principal = tk.Frame(self.ventana)
        frame_principal.pack(padx=8, pady=8)

        # --- columna izquierda: canvas donde se dibuja el mapa ---
        tamano_canvas = self.TAMANO_MAPA * self.TAMANO_CASILLA
        self.canvas = tk.Canvas(frame_principal,
                                width=tamano_canvas, height=tamano_canvas)
        self.canvas.grid(row=0, column=0, padx=(0, 8))

        # Se conecta el evento de click izquierdo con la funcion al_hacer_click
        self.canvas.bind("<Button-1>", self.al_hacer_click)

        # --- columna derecha: panel de construccion ---
        panel = tk.Frame(frame_principal, bd=2, relief="groove", padx=8, pady=8)
        panel.grid(row=0, column=1, sticky="n")

        # Nombre del jugador defensor
        tk.Label(panel, text=f"Defensor:\n{self.jugador_defensor}",
                 font=("Arial", 10, "bold"), justify="center").pack(pady=(0, 8))

        # Label del dinero; se actualiza cada vez que el jugador construye algo
        self.label_dinero = tk.Label(panel, text=f"Dinero: ${self.dinero}",
                                     font=("Arial", 11), fg="green")
        self.label_dinero.pack(pady=(0, 10))

        # Titulo de la seccion de construccion
        tk.Label(panel, text="Construir:", font=("Arial", 9, "bold")).pack(anchor="w")

        # Opciones de construccion: (valor interno, texto visible con precio)
        opciones = [
            ("Muro",   "Muro  $10"),
            ("Basica", "Torre Basica  $50"),
            ("Pesada", "Torre Pesada  $120"),
            ("Magica", "Torre Magica  $90"),
        ]

        # Se crea un boton de radio por cada opcion de construccion
        for valor, texto in opciones:
            tk.Radiobutton(
                panel, text=texto, variable=self.seleccion,
                value=valor, anchor="w", font=("Arial", 9)
            ).pack(fill="x", pady=1)

        # Instruccion breve para el usuario
        tk.Label(panel, text="\nHaz click en una\ncasilla gris\npara construir",
                 font=("Arial", 8), fg="#777777", justify="center").pack(pady=(10, 0))

        tk.Label(panel, text="").pack()  # espacio visual

        # Boton para que el defensor termine su fase y ceda el turno al atacante
        self.boton_terminar = tk.Button(
            panel, text="Terminar\nconstruccion",
            font=("Arial", 9, "bold"), fg="white", bg="#cc4444",
            width=14, command=self.terminar_construccion
        )
        self.boton_terminar.pack(pady=(4, 0))

        # Label que muestra en que fase estamos (construccion o ataque)
        self.label_fase = tk.Label(panel, text="Fase: Construccion",
                                   font=("Arial", 8), fg="#444444")
        self.label_fase.pack(pady=(6, 0))

        # --- panel del atacante (empieza oculto, se muestra al terminar construccion) ---
        self.panel_atacante = tk.Frame(frame_principal, bd=2, relief="groove", padx=8, pady=8)
        # No se agrega al grid todavia; se muestra cuando sea el turno del atacante

        tk.Label(self.panel_atacante, text=f"Atacante:\n{self.jugador_atacante}",
                 font=("Arial", 10, "bold"), fg="#cc0000", justify="center").pack(pady=(0, 8))

        self.label_dinero_atacante = tk.Label(self.panel_atacante,
                                              text=f"Dinero: ${self.dinero_atacante}",
                                              font=("Arial", 11), fg="green")
        self.label_dinero_atacante.pack(pady=(0, 10))

        tk.Label(self.panel_atacante, text="Desplegar unidad:",
                 font=("Arial", 9, "bold")).pack(anchor="w")

        # Opciones de unidad: (valor interno, texto con precio)
        opciones_unidad = [
            ("Soldado", "Soldado  $30"),
            ("Tanque",  "Tanque   $100"),
            ("Rapida",  "Rapida   $70"),
        ]

        for valor, texto in opciones_unidad:
            tk.Radiobutton(
                self.panel_atacante, text=texto, variable=self.seleccion_unidad,
                value=valor, anchor="w", font=("Arial", 9)
            ).pack(fill="x", pady=1)

        tk.Label(self.panel_atacante,
                 text="\nHaz click en la\nfila superior\npara desplegar",
                 font=("Arial", 8), fg="#777777", justify="center").pack(pady=(10, 0))

        tk.Label(self.panel_atacante, text="").pack()

        # Boton para que el atacante termine su fase
        self.boton_terminar_ataque = tk.Button(
            self.panel_atacante, text="Terminar\ndespliegue",
            font=("Arial", 9, "bold"), fg="white", bg="#884400",
            width=14, command=self.terminar_despliegue
        )
        self.boton_terminar_ataque.pack(pady=(4, 0))

    # ----------------------------------------------------------
    # Interaccion con el mapa
    # ----------------------------------------------------------

    def al_hacer_click(self, evento):
        # Se convierte la posicion del click (en pixeles) a fila y columna
        columna = evento.x // self.TAMANO_CASILLA
        fila    = evento.y // self.TAMANO_CASILLA

        # Se ignora si el click cae fuera de los limites
        if fila >= self.TAMANO_MAPA or columna >= self.TAMANO_MAPA:
            return

        # --- fase de construccion: el defensor coloca muros y torres ---
        if self.fase == "construccion":
            if self.mapa[fila][columna] != self.VACIA:
                return

            construccion = self.seleccion.get()

            if construccion == "Muro":
                if self.dinero < Muro.COSTO:
                    messagebox.showwarning("Sin dinero",
                                           "No tienes dinero suficiente para un muro.",
                                           parent=self.ventana)
                    return
                nuevo_muro = Muro(fila, columna)
                self.muros.append(nuevo_muro)
                self.mapa[fila][columna] = self.MURO
                self.dinero -= Muro.COSTO

            else:
                costo = Torre.TIPOS_TORRE[construccion]["costo"]
                if self.dinero < costo:
                    messagebox.showwarning("Sin dinero",
                                           "No tienes dinero suficiente para esta torre.",
                                           parent=self.ventana)
                    return
                nueva_torre = Torre(construccion, fila, columna)
                self.torres.append(nueva_torre)
                self.mapa[fila][columna] = self.TORRE
                self.dinero -= costo

            self.label_dinero.config(text=f"Dinero: ${self.dinero}")
            self.dibujar_mapa()

        # --- fase de ataque: el atacante coloca unidades en la fila superior ---
        elif self.fase == "ataque":
            # Las unidades solo se pueden colocar en la primera fila del mapa
            if fila != 0:
                messagebox.showwarning(
                    "Posicion invalida",
                    "Las unidades solo se pueden colocar en la fila superior del mapa.",
                    parent=self.ventana)
                return

            # La casilla debe estar vacia
            if self.mapa[fila][columna] != self.VACIA:
                return

            tipo_unidad = self.seleccion_unidad.get()
            costo = Unidad.TIPOS_UNIDAD[tipo_unidad]["costo"]

            if self.dinero_atacante < costo:
                messagebox.showwarning("Sin dinero",
                                       "No tienes dinero suficiente para esta unidad.",
                                       parent=self.ventana)
                return

            # Se crea la unidad y se coloca en el mapa
            nueva_unidad = Unidad(tipo_unidad, fila, columna)
            self.unidades.append(nueva_unidad)
            self.mapa[fila][columna] = self.UNIDAD
            self.dinero_atacante -= costo

            self.label_dinero_atacante.config(text=f"Dinero: ${self.dinero_atacante}")
            self.dibujar_mapa()

    def terminar_construccion(self):
        # Se le pide confirmacion al defensor antes de ceder el turno
        confirmar = messagebox.askyesno(
            "Terminar construccion",
            f"Torres colocadas: {len(self.torres)}\n"
            f"Muros colocados:  {len(self.muros)}\n"
            f"Dinero restante:  ${self.dinero}\n\n"
            "¿Terminar la fase de construccion y pasar al atacante?",
            parent=self.ventana
        )
        if not confirmar:
            return

        # Se cambia la fase y se bloquea el panel del defensor
        self.fase = "ataque"
        self.boton_terminar.config(state="disabled")
        self.label_fase.config(text="Fase: Ataque", fg="#cc4444")

        # Se muestra el panel del atacante en la columna derecha
        self.panel_atacante.grid(row=0, column=1, sticky="n")

        messagebox.showinfo(
            "Turno del atacante",
            f"Es el turno de {self.jugador_atacante}.\n"
            "Haz click en la fila superior del mapa para desplegar unidades.",
            parent=self.ventana
        )

    def terminar_despliegue(self):
        # Se le pide confirmacion al atacante antes de pasar al combate
        confirmar = messagebox.askyesno(
            "Terminar despliegue",
            f"Unidades desplegadas: {len(self.unidades)}\n"
            f"Dinero restante: ${self.dinero_atacante}\n\n"
            "¿Terminar el despliegue e iniciar el combate?",
            parent=self.ventana
        )
        if not confirmar:
            return

        self.fase = "combate"
        self.boton_terminar_ataque.config(state="disabled")

        # Se avisa que el combate viene en el siguiente avance
        messagebox.showinfo(
            "Combate",
            "El despliegue termino.\n\n"
            "(La fase de combate se implementara en el proximo avance.)",
            parent=self.ventana
        )

    # ----------------------------------------------------------
    # Dibujo del mapa
    # ----------------------------------------------------------

    def dibujar_mapa(self):
        self.canvas.delete("all")  # se borra todo antes de redibujar

        for fila in range(self.TAMANO_MAPA):
            for columna in range(self.TAMANO_MAPA):
                valor = self.mapa[fila][columna]
                color = self.COLORES.get(valor, "white")  # color segun el tipo de casilla

                # Se calcula la posicion en pixeles de este cuadrito
                x1 = columna * self.TAMANO_CASILLA
                y1 = fila    * self.TAMANO_CASILLA
                x2 = x1 + self.TAMANO_CASILLA
                y2 = y1 + self.TAMANO_CASILLA

                # Se dibuja el rectangulo con el color correspondiente
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color, outline="black")

                # Si la casilla tiene una torre, se dibuja la inicial de su tipo
                if valor == self.TORRE:
                    torre = self._torre_en(fila, columna)
                    if torre:
                        inicial = torre.tipo[0]  # "B" = Basica, "P" = Pesada, "M" = Magica
                        cx = x1 + self.TAMANO_CASILLA // 2
                        cy = y1 + self.TAMANO_CASILLA // 2
                        self.canvas.create_text(cx, cy, text=inicial,
                                                fill="white", font=("Arial", 10, "bold"))

                # Si la casilla tiene una unidad, se dibuja la inicial de su tipo
                if valor == self.UNIDAD:
                    unidad = self._unidad_en(fila, columna)
                    if unidad:
                        inicial = unidad.tipo[0]  # "S" = Soldado, "T" = Tanque, "R" = Rapida
                        cx = x1 + self.TAMANO_CASILLA // 2
                        cy = y1 + self.TAMANO_CASILLA // 2
                        self.canvas.create_text(cx, cy, text=inicial,
                                                fill="white", font=("Arial", 10, "bold"))

    def _torre_en(self, fila, columna):
        # Se recorre la lista de torres y se devuelve la que este en esa posicion.
        for torre in self.torres:
            if torre.fila == fila and torre.columna == columna:
                return torre
        return None

    def _unidad_en(self, fila, columna):
        # Se recorre la lista de unidades y se devuelve la que este en esa posicion.
        for unidad in self.unidades:
            if unidad.fila == fila and unidad.columna == columna:
                return unidad
        return None
# =============================================================
# Tropas/Unidades enemigas
# =============================================================
class Unidad:
    TIPOS_UNIDAD ={
    "Soldado":{
        "costo": 30,
        "vida": 80,
        "dano": 10,
        "velocidad":1,
        "habilidad": "Ataque doble",
        "turnos_habilidad": 3   
        },
    "Tanque":{
        "costo": 100,
        "vida": 300,
        "dano": 20,
        "velocidad":1,
        "habilidad": "Escudo temporal",
        "turnos_habilidad": 2   
        },
    "Rapida":{
        "costo": 70,
        "vida": 70,
        "dano": 30,
        "velocidad": 2,
        "habilidad": "Esquivo",  # esquiva el proximo ataque que reciba
        "turnos_habilidad": 3
        },
    }
    def __init__(self, tipo, fila, columna):
        if tipo not in self.TIPOS_UNIDAD:
            raise ValueError(f"Tipo de unidad desconocido: {tipo}")
        
        datos = self.TIPOS_UNIDAD[tipo]
        self.tipo = tipo
        self.fila = fila
        self.columna = columna

        self.vida = datos["vida"]
        self.vida_max = datos["vida"]
        self.dano = datos["dano"]
        self.velocidad = datos["velocidad"]
        self.habilidad = datos["habilidad"]
        self.turnos_habilidad = datos["turnos_habilidad"]
        self.turnos_restantes = 0  # cuenta regresiva para la habilidad

        # Estados especiales de habilidad
        self.escudo_activo = False  # usado por el Tanque
        self.esquivo = False        # usado por la Rapida

    # ----------------------------------------------------------
    # Funciones de vida
    # ----------------------------------------------------------

    def esta_viva(self):
        # Se devuelve True si la unidad todavia tiene vida
        return self.vida > 0

    def recibir_dano(self, cantidad):
        # Si el escudo esta activo, absorbe el dano y se desactiva
        if self.escudo_activo:
            self.escudo_activo = False
            return
        # Si el esquivo esta activo, el ataque falla y se desactiva
        if self.esquivo:
            self.esquivo = False
            return
        self.vida = self.vida - cantidad
        if self.vida < 0:
            self.vida = 0

    def mover(self, nueva_fila):
        # Se actualiza la posicion de la unidad en el mapa.
        # Las unidades se mueven siempre hacia abajo (hacia la base).
        self.fila = nueva_fila

    # ----------------------------------------------------------
    # Funciones de habilidad
    # ----------------------------------------------------------

    def puede_usar_habilidad(self):
        # La habilidad esta lista cuando el contador llega a 0
        return self.turnos_restantes <= 0

    def activar_habilidad(self):
        # Se activa la habilidad del tipo correspondiente.
        # Cada habilidad tiene su propio efecto.
        if not self.puede_usar_habilidad():
            return False

        if self.tipo == "Soldado":
            # Ataque doble: el efecto se aplica en la fase de combate
            pass
        elif self.tipo == "Tanque":
            # Escudo temporal: absorbe el proximo golpe
            self.escudo_activo = True
        elif self.tipo == "Rapida":
            # Esquivo: permite esquivar el proximo ataque
            self.esquivo = True

        self.turnos_restantes = self.turnos_habilidad  # se reinicia el cooldown
        return True

    def pasar_turno(self):
        # Se llama al final de cada turno para bajar el contador de la habilidad
        if self.turnos_restantes > 0:
            self.turnos_restantes -= 1

    def __repr__(self):
        # Se usa para imprimir la unidad de forma legible (util para depurar)
        return f"Unidad({self.tipo}, fila={self.fila}, col={self.columna}, vida={self.vida})"
    



# =============================================================
# INTERFAZ PRINCIPAL
# =============================================================
class Interfaz:
    # Se crea la ventana principal del juego donde los dos jugadores
    # inician sesion, eligen su faccion, y arrancan la partida.

    def __init__(self):
        # Se inicializan los datos de ambos jugadores como vacios
        self.jugador1 = "—"  # jugador 1 siempre es el defensor
        self.faccion1 = "—"
        self.jugador2 = "—"  # jugador 2 siempre es el atacante
        self.faccion2 = "—"

        self.root = tk.Tk()
        self.root.title("Defensa de Torres")
        self._construir_ventana()

    def _construir_ventana(self):
        # Titulo del juego en un canvas para poder usar colores y fuentes grandes
        canvas = tk.Canvas(self.root, width=520, height=160)
        canvas.pack()
        canvas.create_text(260, 70, text="Defensa de Torres",
                           fill="gold", font=("Arial", 30, "bold"))
        canvas.create_text(260, 115, text="Proyecto II",
                           fill="#aabbff", font=("Arial", 14))

        # --- bloque del jugador 1 (defensor) ---
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

        # --- bloque del jugador 2 (atacante) ---
        # Empieza deshabilitado; se habilita cuando el jugador 1 ya inicio sesion
        frame2 = tk.LabelFrame(self.root, text="Jugador 2 — Atacante",
                                padx=10, pady=6)
        frame2.pack(fill="x", padx=16, pady=(2, 8))

        self.label_j2 = tk.Label(frame2, text="Usuario: —", width=22, anchor="w")
        self.label_j2.grid(row=0, column=0, sticky="w")
        self.label_f2 = tk.Label(frame2, text="Faccion: —", width=22, anchor="w")
        self.label_f2.grid(row=1, column=0, sticky="w")

        self.boton_login2 = tk.Button(frame2, text="Iniciar sesion / Registrarse",
                                      width=26, command=self.abrir_login2,
                                      state="disabled")  # deshabilitado hasta que J1 termine
        self.boton_login2.grid(row=0, column=1, rowspan=2, padx=(12, 0))

        # Aclaracion de que los roles no cambian durante la partida
        tk.Label(
            self.root,
            text="Los roles son fijos durante la partida.\n"
                 "Para invertirlos, inicien sesion en el slot contrario la proxima vez.",
            font=("Arial", 8), fg="#777777", justify="center"
        ).pack(pady=(0, 4))

        # Boton para iniciar la partida; solo se habilita cuando ambos jugadores estan listos
        self.boton_iniciar = tk.Button(self.root, text="Iniciar Juego",
                                       command=self.iniciar_juego,
                                       state="disabled", width=20)
        self.boton_iniciar.pack(pady=6)

        self.root.mainloop()  # se inicia el loop principal de Tkinter

    # ----------------------------------------------------------
    # Flujo del jugador 1
    # ----------------------------------------------------------

    def abrir_login1(self):
        # Se abre la ventana de login para el jugador 1
        VentanaLogin(self.root, on_exito=self.al_autenticar_j1)

    def al_autenticar_j1(self, usuario):
        # Se guarda el usuario y se actualiza el label en pantalla
        self.jugador1 = usuario
        self.label_j1.config(text=f"Usuario: {usuario}")
        self.boton_login1.config(state="disabled")  # ya no se puede loguear de nuevo
        # Se abre inmediatamente la seleccion de faccion
        VentanaFacciones(self.root, jugador=usuario,
                         on_exito=self.al_elegir_faccion1)

    def al_elegir_faccion1(self, faccion):
        # Se guarda la faccion elegida y se habilita el turno del jugador 2
        self.faccion1 = faccion
        self.label_f1.config(text=f"Faccion: {faccion}")
        self.boton_login2.config(state="normal")  # ahora puede entrar el jugador 2

    # ----------------------------------------------------------
    # Flujo del jugador 2
    # ----------------------------------------------------------

    def abrir_login2(self):
        # Se abre la ventana de login para el jugador 2
        VentanaLogin(self.root, on_exito=self.al_autenticar_j2)

    def al_autenticar_j2(self, usuario):
        # No se permite que los dos jugadores usen la misma cuenta
        if usuario == self.jugador1:
            messagebox.showerror(
                "Error", "El jugador 2 no puede ser el mismo que el jugador 1.",
                parent=self.root)
            return
        self.jugador2 = usuario
        self.label_j2.config(text=f"Usuario: {usuario}")
        self.boton_login2.config(state="disabled")
        # Se abre la seleccion de faccion con la faccion del J1 bloqueada
        VentanaFacciones(self.root, jugador=usuario,
                         on_exito=self.al_elegir_faccion2,
                         faccion_bloqueada=self.faccion1)

    def al_elegir_faccion2(self, faccion):
        # Se guarda la faccion y se habilita el boton de inicio
        self.faccion2 = faccion
        self.label_f2.config(text=f"Faccion: {faccion}")
        self.boton_iniciar.config(state="normal")  # ya estan listos los dos jugadores

    # ----------------------------------------------------------
    # Inicio de la partida
    # ----------------------------------------------------------

    def iniciar_juego(self):
        # Se muestra un resumen de los dos jugadores y se pide confirmacion
        resumen = (
            f"Jugador 1 (Defensor): {self.jugador1}  [{self.faccion1}]\n"
            f"Jugador 2 (Atacante): {self.jugador2}  [{self.faccion2}]\n\n"
            "¿Comenzar la partida?"
        )
        if messagebox.askyesno("Confirmar partida", resumen, parent=self.root):
            VentanaTablero(self.root,
                           jugador_defensor=self.jugador1,
                           jugador_atacante=self.jugador2)


# Aqui arranca todo: al crear el objeto se abre la ventana principal
Interfaz()
