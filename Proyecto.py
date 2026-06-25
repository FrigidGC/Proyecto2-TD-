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

# Valor usado para representar un alcance "infinito" (la Torre Magica
# puede atacar a cualquier unidad del tablero). Se usa un numero grande
# pero finito en vez de float('inf') para evitar errores de comparacion
# o de tipo en el resto del codigo (por ejemplo al dibujar o guardar datos).
ALCANCE_INFINITO = 999


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
            "alcance": 5,           # casillas de distancia a las que puede atacar
            "habilidad": "Ninguna",
            "turnos_habilidad": 0,  # 0 significa que no tiene habilidad especial
        },
        "Pesada": {
            "costo": 120,
            "vida": 250,
            "dano": 25,
            "alcance": 4,
            "habilidad": "Disparo doble",
            "turnos_habilidad": 3,  # se puede usar cada 3 turnos
        },
        "Magica": {
            "costo": 90,
            "vida": 60,
            "dano": 5,
            "alcance": ALCANCE_INFINITO,  # "infinito": cubre cualquier punto del tablero
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

        # Guarda el ultimo golpe recibido para mostrarlo en pantalla como
        # "vida_antes-dano" durante el turno en que ocurrio (ver dibujar_mapa).
        # Se limpia al inicio de cada turno de combate (ver limpiar_indicadores_dano).
        self.ultimo_dano = None

    def esta_viva(self):
        # Se devuelve True si la torre todavia tiene vida
        return self.vida > 0

    def recibir_dano(self, cantidad):
        # Se guarda la vida antes del golpe para el indicador visual
        self.ultimo_dano = (self.vida, cantidad)
        # Se resta la vida recibida, pero no puede bajar de 0
        self.vida = self.vida - cantidad
        if self.vida < 0:
            self.vida = 0

    def puede_usar_habilidad(self):
        # La habilidad esta lista cuando el contador llega a 0
        return self.turnos_restantes <= 0

    def activar_habilidad(self, objetivo=None):
        # Punto de entrada general para activar la habilidad de la torre.
        # Reparte el trabajo al metodo especifico segun el tipo de torre.
        # IMPORTANTE: este metodo todavia NO es llamado desde la fase de
        # combate (ver _torres_atacan en VentanaTablero); solo queda
        # preparada la logica para conectarla mas adelante.
        if not self.puede_usar_habilidad():
            return False

        if self.tipo == "Pesada":
            self._habilidad_disparo_doble(objetivo)
        elif self.tipo == "Magica":
            self._habilidad_congelar(objetivo)
        # La Torre Basica no tiene habilidad especial ("Ninguna")

        self.turnos_restantes = self.turnos_habilidad  # se reinicia el cooldown
        return True

    def _habilidad_disparo_doble(self, objetivo):
        # Habilidad de la Torre Pesada: dispara dos veces al mismo
        # objetivo en el mismo turno (el doble de dano total).
        if objetivo is None:
            return
        objetivo.recibir_dano(self.dano)
        objetivo.recibir_dano(self.dano)

    def _habilidad_congelar(self, objetivo):
        # Habilidad de la Torre Magica: ademas de hacer su dano normal,
        # congela al objetivo para que no pueda avanzar en su proximo turno.
        if objetivo is None:
            return
        objetivo.congelada = True
        objetivo.recibir_dano(self.dano)

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

        # Guarda el ultimo golpe recibido para mostrarlo en pantalla como
        # "vida_antes-dano" durante el turno en que ocurrio.
        self.ultimo_dano = None

    def esta_vivo(self):
        # Se devuelve True si el muro todavia tiene vida
        return self.vida > 0

    def recibir_dano(self, cantidad):
        # Se guarda la vida antes del golpe para el indicador visual
        self.ultimo_dano = (self.vida, cantidad)
        # Se resta vida al muro, pero no puede bajar de 0
        self.vida = self.vida - cantidad
        if self.vida < 0:
            self.vida = 0

    def __repr__(self):
        return f"Muro(fila={self.fila}, col={self.columna}, vida={self.vida})"


# =============================================================
# VENTANA DEL TABLERO
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
        self.congelada = False      # puesto por la Torre Magica

        # Guarda el ultimo golpe recibido para mostrarlo en pantalla como
        # "vida_antes-dano" durante el turno en que ocurrio. Solo se llena
        # cuando el dano realmente se aplica (no si lo absorbe un escudo
        # o lo evita un esquivo).
        self.ultimo_dano = None

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
        # Se guarda la vida antes del golpe para el indicador visual
        self.ultimo_dano = (self.vida, cantidad)
        self.vida = self.vida - cantidad
        if self.vida < 0:
            self.vida = 0

    def mover(self, nueva_fila, nueva_columna=None):
        # Se actualiza la posicion de la unidad en el mapa.
        # Con el pathfinding (BFS), la unidad puede desplazarse tanto en
        # fila como en columna para rodear obstaculos, por eso este metodo
        # acepta tambien una nueva columna (opcional, por compatibilidad).
        self.fila = nueva_fila
        if nueva_columna is not None:
            self.columna = nueva_columna

    # ----------------------------------------------------------
    # Funciones de habilidad
    # ----------------------------------------------------------

    def puede_usar_habilidad(self):
        # La habilidad esta lista cuando el contador llega a 0
        return self.turnos_restantes <= 0

    def activar_habilidad(self):
        # Punto de entrada general para activar la habilidad de la unidad.
        # Reparte el trabajo al metodo especifico segun el tipo de unidad.
        # IMPORTANTE: este metodo todavia NO es llamado desde la fase de
        # combate (ver _unidades_atacan en VentanaTablero); solo queda
        # preparada la logica para conectarla mas adelante.
        if not self.puede_usar_habilidad():
            return False

        if self.tipo == "Soldado":
            self._habilidad_ataque_doble()
        elif self.tipo == "Tanque":
            self._habilidad_escudo()
        elif self.tipo == "Rapida":
            self._habilidad_esquivo()

        self.turnos_restantes = self.turnos_habilidad  # se reinicia el cooldown
        return True

    def _habilidad_ataque_doble(self):
        # Habilidad del Soldado: el siguiente ataque hace el doble de dano.
        # El multiplicador real se aplica en la fase de combate, al
        # calcular el dano_total del ataque (todavia no conectado).
        pass

    def _habilidad_escudo(self):
        # Habilidad del Tanque: activa un escudo que absorbe por
        # completo el proximo golpe que reciba la unidad.
        self.escudo_activo = True

    def _habilidad_esquivo(self):
        # Habilidad de la Rapida: le permite esquivar por completo
        # el proximo ataque que reciba.
        self.esquivo = True

    def pasar_turno(self):
        # Se llama al final de cada turno para bajar el contador de la habilidad
        if self.turnos_restantes > 0:
            self.turnos_restantes -= 1

    def __repr__(self):
        # Se usa para imprimir la unidad de forma legible (util para depurar)
        return f"Unidad({self.tipo}, fila={self.fila}, col={self.columna}, vida={self.vida})"
    



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
        0: "#2d5a1b",   # vacio = verde oscuro (cesped)
        1: "#8B4513",   # muro = cafe
        2: "#4169E1",   # torre = azul
        3: "gold",      # base = dorado
        4: "#4a7c30",   # camino = verde medio
        5: "#cc0000",   # unidad = rojo
    }
    COLOR_GRID = "#5aaa3a"  # color de las lineas de la cuadricula (verde claro)

    DINERO_INICIAL    = 300  # dinero con el que arranca cada jugador al inicio de cada ronda
    DINERO_POR_RONDA  = 50   # dinero extra que reciben ambos jugadores al inicio de cada ronda
    DINERO_POR_UNIDAD = 20   # dinero que gana el defensor por cada unidad eliminada
    DINERO_POR_DANO   = 1    # dinero que gana el atacante por cada punto de dano a torres/base

    def __init__(self, parent, jugador_defensor, jugador_atacante):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Tablero de juego")
        self.ventana.resizable(False, False)
        self.vida_base = 200
        self._ultimo_dano_base = None  # indicador "vida_antes-dano" de la base
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

        # Marcador de rondas ganadas por cada jugador
        # El primero en ganar 3 rondas gana la partida
        self.rondas_defensor = 0
        self.rondas_atacante = 0
        self.ronda_actual    = 1

        # Contador de turnos de combate
        self.turno_combate = 0

        # Se acumula el dano total que hizo el atacante esta ronda
        # (para calcular su bono de dinero al inicio de la siguiente)
        self.dano_atacante_ronda = 0

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

        # Label de vida de la base (visible siempre)
        self.label_vida_base = tk.Label(panel, text=f"Vida base: {self.vida_base}",
                                        font=("Arial", 9, "bold"), fg="gold")
        self.label_vida_base.pack(pady=(4, 0))

        # Marcador de rondas: muestra cuantas rondas ha ganado cada jugador
        self.label_marcador = tk.Label(
            panel,
            text=f"Ronda {self.ronda_actual}\nDef: {self.rondas_defensor}  Atac: {self.rondas_atacante}",
            font=("Arial", 9, "bold"), fg="#333333", justify="center"
        )
        self.label_marcador.pack(pady=(6, 0))

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
        # Boton para avanzar un turno de combate manualmente
        self.boton_turno = tk.Button(
            self.panel_atacante, text="Ejecutar turno",
            font=("Arial", 9, "bold"), fg="white", bg="#336633",
            width=14, command=self.ejecutar_combate,
            state="disabled"  # se habilita cuando empieza el combate
        )
        self.boton_turno.pack(pady=(4, 0))

        # Contador de turno de combate
        self.label_turno = tk.Label(self.panel_atacante, text="Turno: 0",
                                    font=("Arial", 9), fg="#444444")
        self.label_turno.pack(pady=(2, 0))

        # Log de combate: muestra los ultimos eventos del turno
        tk.Label(self.panel_atacante, text="Log:", font=("Arial", 8, "bold")).pack(anchor="w", pady=(6, 0))
        self.log_text = tk.Text(self.panel_atacante, width=22, height=10,
                                font=("Arial", 7), state="disabled", bg="#f5f5f5")
        self.log_text.pack(pady=(0, 4))

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

    def _log(self, mensaje):
        # Agrega una linea al cuadro de texto del log de combate
        self.log_text.config(state="normal")
        self.log_text.insert("end", mensaje + "\n")
        self.log_text.see("end")  # hace scroll al final
        self.log_text.config(state="disabled")

    def terminar_despliegue(self):
        # Se verifica que el atacante tenga al menos una unidad desplegada,
        # a menos que ya no le quede dinero para ninguna (en ese caso se
        # fuerza el inicio del combate aunque no haya desplegado nada)
        costo_minimo = min(Unidad.TIPOS_UNIDAD[t]["costo"] for t in Unidad.TIPOS_UNIDAD)
        sin_dinero_suficiente = self.dinero_atacante < costo_minimo

        if len(self.unidades) == 0 and not sin_dinero_suficiente:
            messagebox.showwarning(
                "Sin unidades",
                "Debes desplegar al menos una unidad antes de iniciar el combate.",
                parent=self.ventana)
            return

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
        self.boton_turno.config(state="normal")

        messagebox.showinfo(
            "Combate",
            "El despliegue termino.\n\n"
            "Presiona 'Ejecutar turno' para avanzar el combate turno a turno.",
            parent=self.ventana
        )

    def ejecutar_combate(self):
        # Se ejecuta un turno completo de combate en este orden:
        # 1. Se limpian los indicadores de dano del turno anterior
        # 2. Las torres atacan a las unidades en su alcance (con habilidades)
        # 3. Las unidades avanzan hacia la base
        # 4. Las unidades atacan lo que tengan enfrente
        # 5. Se eliminan las torres, muros y unidades destruidos
        # 6. Se revisa si alguien gano la ronda

        self.turno_combate += 1
        self.label_turno.config(text=f"Turno: {self.turno_combate}")
        self._log(f"--- Turno {self.turno_combate} ---")

        self._limpiar_indicadores_dano()
        self._torres_atacan()
        self._unidades_avanzan()
        self._unidades_atacan()
        self._limpiar_muertos()

        # Actualizar label de vida de base
        self.label_vida_base.config(text=f"Vida base: {max(self.vida_base, 0)}")

        self._revisar_victoria()
        self.dibujar_mapa()

    def _limpiar_indicadores_dano(self):
        # Borra el indicador "vida_antes-dano" del turno anterior en todas
        # las piezas (torres, muros, unidades, base) antes de calcular los
        # golpes de este nuevo turno. Asi el indicador solo se ve durante
        # el turno en que ocurrio el golpe; al turno siguiente ya se
        # muestra solo la vida resultante (a menos que reciba otro golpe).
        self._ultimo_dano_base = None
        for torre in self.torres:
            torre.ultimo_dano = None
        for muro in self.muros:
            muro.ultimo_dano = None
        for unidad in self.unidades:
            unidad.ultimo_dano = None

    def _torres_atacan(self):
        # Cada torre busca la unidad mas cercana dentro de su alcance y le hace dano.
        #
        # NOTA: la logica de habilidades de cada torre (Disparo doble de la
        # Pesada, Congelar de la Magica) ya esta definida en la clase Torre
        # (ver puede_usar_habilidad / activar_habilidad), pero todavia NO
        # se ejecuta aqui. Se deja preparada para conectarla mas adelante;
        # por ahora cada torre solo hace su ataque base normal.
        for torre in self.torres:
            if not torre.esta_viva():
                continue

            # Se recopilan las unidades dentro del alcance, ordenadas por cercania
            en_alcance = []
            for unidad in self.unidades:
                if not unidad.esta_viva():
                    continue
                distancia = abs(torre.fila - unidad.fila) + abs(torre.columna - unidad.columna)
                if distancia <= torre.alcance:
                    en_alcance.append((distancia, unidad))

            if not en_alcance:
                torre.pasar_turno()
                continue

            # Se ataca la unidad mas cercana; si la habilidad esta lista se usa
            en_alcance.sort(key=lambda x: x[0])
            objetivo = en_alcance[0][1]

            if torre.puede_usar_habilidad() and torre.tipo != "Basica":
                torre.activar_habilidad(objetivo)
                if torre.tipo == "Pesada":
                    self._log(f"Torre Pesada ({torre.fila},{torre.columna}): Disparo doble x{torre.dano*2} a {objetivo.tipo}")
                elif torre.tipo == "Magica":
                    self._log(f"Torre Magica ({torre.fila},{torre.columna}): Congela a {objetivo.tipo} (-{torre.dano})")
            else:
                objetivo.recibir_dano(torre.dano)
                self._log(f"Torre {torre.tipo}: -{torre.dano} a {objetivo.tipo} (vida {objetivo.vida})")

            torre.pasar_turno()

    # ----------------------------------------------------------
    # Pathfinding (BFS) para las unidades atacantes
    # ----------------------------------------------------------

    def _es_transitable(self, fila, columna, fila_base, col_base, respetar_unidades=False):
        # Una casilla se puede pisar si esta dentro del mapa y no tiene
        # un obstaculo permanente (muro, torre o la base).
        # Las otras unidades NO se tratan como obstaculo para el BFS:
        # se ignoran al calcular la ruta para que el pathfinding no se
        # bloquee cuando varias unidades estan juntas. El paso real solo
        # se ejecuta si la casilla destino esta realmente vacia (ver
        # _unidades_avanzan).
        if not (0 <= fila < self.TAMANO_MAPA and 0 <= columna < self.TAMANO_MAPA):
            return False
        if fila == fila_base and columna == col_base:
            return False
        contenido = self.mapa[fila][columna]
        # MURO y TORRE son obstaculos permanentes; UNIDAD y VACIA y CAMINO
        # se consideran libres para el calculo de la ruta
        if respetar_unidades:
            return contenido not in (self.MURO, self.TORRE, self.UNIDAD)
        return contenido not in (self.MURO, self.TORRE)

    def _es_adyacente_a_base(self, fila, columna, fila_base, col_base):
        # Devuelve True si (fila, columna) esta justo al lado de la base
        # (arriba, abajo, izquierda o derecha), sin contar la base misma.
        distancia = abs(fila - fila_base) + abs(columna - col_base)
        return distancia == 1

    def _calcular_ruta(self, unidad, respetar_unidades=False, ignorar_obstaculos=False):
        fila_base = self.TAMANO_MAPA - 1
        col_base  = self.TAMANO_MAPA // 2

        inicio = (unidad.fila, unidad.columna)

        if self._es_adyacente_a_base(unidad.fila, unidad.columna, fila_base, col_base):
            return []

        movimientos = [(1, 0), (0, -1), (0, 1), (-1, 0)]
        visitados = {inicio}
        cola = [(inicio, [])]
        indice = 0

        while indice < len(cola):
            (fila_actual, col_actual), camino = cola[indice]
            indice += 1

            for d_fila, d_col in movimientos:
                siguiente = (fila_actual + d_fila, col_actual + d_col)

                if siguiente in visitados:
                    continue

                f_sig, c_sig = siguiente

                if ignorar_obstaculos:
                    # Validaciones manuales si ignoramos los obstáculos fijos
                    if not (0 <= f_sig < self.TAMANO_MAPA and 0 <= c_sig < self.TAMANO_MAPA):
                        continue
                    if f_sig == fila_base and c_sig == col_base:
                        continue
                    # Si respetar_unidades es True, los aliados siguen bloqueando
                    if respetar_unidades and self.mapa[f_sig][c_sig] == self.UNIDAD:
                        continue
                else:
                    if not self._es_transitable(f_sig, c_sig, fila_base, col_base, respetar_unidades):
                        continue

                nuevo_camino = camino + [siguiente]

                if self._es_adyacente_a_base(f_sig, c_sig, fila_base, col_base):
                    return nuevo_camino

                visitados.add(siguiente)
                cola.append((siguiente, nuevo_camino))

        return None
    
    def _unidades_avanzan(self):
        fila_base = self.TAMANO_MAPA - 1
        col_base  = self.TAMANO_MAPA // 2

        unidades_vivas = sorted(
            [u for u in self.unidades if u.esta_viva()],
            key=lambda u: (-u.fila, u.columna)
        )

        for unidad in unidades_vivas:
            if getattr(unidad, "congelada", False):
                unidad.congelada = False
                self._log(f"{unidad.tipo} ({unidad.fila},{unidad.columna}): congelada, no avanza")
                unidad.pasar_turno()
                continue

            pasos = unidad.velocidad
            for _ in range(pasos):
                if self._es_adyacente_a_base(unidad.fila, unidad.columna, fila_base, col_base):
                    break

                ruta = self._calcular_ruta(unidad, respetar_unidades=True)

                if ruta is None:
                    # Plan B: buscar la ruta más corta rompiendo estructuras
                    ruta = self._calcular_ruta(unidad, respetar_unidades=True, ignorar_obstaculos=True)

                if ruta is None:
                    break  # bloqueada completamente por aliados o bordes
                if not ruta:
                    break  # ya en destino

                siguiente_fila, siguiente_col = ruta[0]

                # NUEVO: Si el siguiente paso es una estructura, detenerse frente a ella para atacarla
                if self.mapa[siguiente_fila][siguiente_col] in (self.MURO, self.TORRE):
                    break

                # Verificacion final en mapa real
                if self.mapa[siguiente_fila][siguiente_col] not in (self.VACIA, self.CAMINO):
                    break

                if self.mapa[unidad.fila][unidad.columna] == self.UNIDAD:
                    self.mapa[unidad.fila][unidad.columna] = self.VACIA

                unidad.fila    = siguiente_fila
                unidad.columna = siguiente_col
                self.mapa[unidad.fila][unidad.columna] = self.UNIDAD

                if self._es_adyacente_a_base(unidad.fila, unidad.columna, fila_base, col_base):
                    self._log(f"{unidad.tipo} llego junto a la base")
                    break

            unidad.pasar_turno()


    def _unidades_atacan(self):
        # Cada unidad ataca el obstaculo que le este bloqueando el paso:
        # un muro, una torre, o la base (cuando esta justo al lado, sin
        # pisarla nunca). Como el movimiento usa pathfinding (BFS) y puede
        # rodear obstaculos, una unidad solo ataca cuando esta realmente
        # bloqueada (ruta == None) o cuando ya llego junto a la base
        # (ruta == [], es decir, ya no necesita moverse mas).
        for unidad in self.unidades:
            if not unidad.esta_viva():
                continue

            ruta = self._calcular_ruta(unidad)

            # Si todavia hay pasos pendientes en la ruta, la unidad no esta
            # bloqueada ni junto a la base: sigue avanzando, no ataca.
            if ruta:
                continue

            objetivo = self._buscar_obstaculo_adyacente(unidad)
            if objetivo is None:
                continue  # no hay nada que atacar (caso raro/borde)

            tipo_objetivo, fila_objetivo, col_objetivo = objetivo

            dano_base = unidad.dano

            # Se activan las habilidades de las unidades segun su tipo
            if unidad.tipo == "Soldado" and unidad.puede_usar_habilidad():
                # Ataque doble: hace el doble de dano este turno
                dano_base = unidad.dano * 2
                unidad.activar_habilidad()
                self._log(f"Soldado: Ataque doble activado! ({dano_base} dano)")

            elif unidad.tipo == "Tanque" and unidad.puede_usar_habilidad():
                # Escudo: se activa cuando le queda menos de la mitad de vida
                if unidad.vida < unidad.vida_max * 0.5:
                    unidad.activar_habilidad()
                    self._log(f"Tanque: Escudo activado!")

            # La Rapida usa su esquivo en recibir_dano, no al atacar

            dano_total = dano_base

            if tipo_objetivo == self.MURO:
                muro = self._muro_en(fila_objetivo, col_objetivo)
                if muro:
                    dano_real = min(dano_total, muro.vida)  # no contar dano de mas
                    muro.recibir_dano(dano_total)
                    self.dano_atacante_ronda += dano_real
                    self._log(f"{unidad.tipo}: ataca muro -{dano_real} (muro vida={muro.vida})")

            elif tipo_objetivo == self.TORRE:
                torre = self._torre_en(fila_objetivo, col_objetivo)
                if torre:
                    dano_real = min(dano_total, torre.vida)
                    torre.recibir_dano(dano_total)
                    self.dano_atacante_ronda += dano_real
                    self._log(f"{unidad.tipo}: ataca Torre {torre.tipo} -{dano_real} (torre vida={torre.vida})")

            elif tipo_objetivo == self.BASE:
                dano_real = min(dano_total, max(self.vida_base, 0))
                self._ultimo_dano_base = (max(self.vida_base, 0), dano_total)
                self.vida_base -= dano_total
                self.dano_atacante_ronda += dano_real
                self._log(f"{unidad.tipo}: ataca BASE -{dano_real} (base={max(self.vida_base,0)})")

    def _buscar_obstaculo_adyacente(self, unidad):
        # Revisa las 4 casillas adyacentes a la unidad (en el orden
        # abajo, izquierda, derecha, arriba) y devuelve la primera que
        # tenga un muro, una torre o la base, como (tipo_casilla, fila, columna).
        # Devuelve None si no hay ningun obstaculo adyacente.
        movimientos = [(1, 0), (0, -1), (0, 1), (-1, 0)]

        for d_fila, d_col in movimientos:
            f = unidad.fila + d_fila
            c = unidad.columna + d_col
            if not (0 <= f < self.TAMANO_MAPA and 0 <= c < self.TAMANO_MAPA):
                continue
            contenido = self.mapa[f][c]
            if contenido in (self.MURO, self.TORRE, self.BASE):
                return (contenido, f, c)
        return None

    def _limpiar_muertos(self):
        # Se eliminan de las listas y del mapa los muros, torres y unidades destruidos.
        for muro in self.muros:
            if not muro.esta_vivo():
                self.mapa[muro.fila][muro.columna] = self.VACIA
                self._log(f"Muro ({muro.fila},{muro.columna}) destruido")
        self.muros = [m for m in self.muros if m.esta_vivo()]

        for torre in self.torres:
            if not torre.esta_viva():
                self.mapa[torre.fila][torre.columna] = self.VACIA
                self._log(f"Torre {torre.tipo} ({torre.fila},{torre.columna}) destruida")
        self.torres = [t for t in self.torres if t.esta_viva()]

        for unidad in self.unidades:
            if not unidad.esta_viva():
                if 0 <= unidad.fila < self.TAMANO_MAPA:
                    if self.mapa[unidad.fila][unidad.columna] == self.UNIDAD:
                        self.mapa[unidad.fila][unidad.columna] = self.VACIA
                # El defensor gana dinero por cada unidad eliminada
                self.dinero += self.DINERO_POR_UNIDAD
                self.label_dinero.config(text=f"Dinero: ${self.dinero}")
                self._log(f"{unidad.tipo} eliminada — Defensor +${self.DINERO_POR_UNIDAD}")
        self.unidades = [u for u in self.unidades if u.esta_viva()]

    def _muro_en(self, fila, columna):
        # Se busca el muro que este en esa posicion del mapa.
        for muro in self.muros:
            if muro.fila == fila and muro.columna == columna:
                return muro
        return None
    
    def _revisar_victoria(self):
        ganador = None  # "defensor" o "atacante"

        # El defensor gana la ronda si todas las unidades fueron eliminadas
        if len(self.unidades) == 0 and self.fase == "combate":
            ganador = "defensor"

        # El atacante gana la ronda si destruyo la base
        if self.vida_base <= 0:
            ganador = "atacante"

        if ganador is None:
            return  # la ronda sigue, nadie gano todavia

        # Se actualiza el marcador de rondas
        if ganador == "defensor":
            self.rondas_defensor += 1
        else:
            self.rondas_atacante += 1

        self.boton_turno.config(state="disabled")
        self.fase = "fin_ronda"

        self.label_marcador.config(
            text=f"Ronda {self.ronda_actual}\nDef: {self.rondas_defensor}  Atac: {self.rondas_atacante}"
        )

        # El primero en ganar 3 rondas gana la partida completa
        if self.rondas_defensor == 3 or self.rondas_atacante == 3:
            self._fin_de_partida(ganador)
        else:
            # Todavia no hay ganador de la partida, se ofrece nueva ronda
            nombre_ganador = self.jugador_defensor if ganador == "defensor" else self.jugador_atacante
            continuar = messagebox.askyesno(
                "Fin de ronda",
                f"¡Gano {nombre_ganador}!\n\n"
                f"Marcador — Defensor: {self.rondas_defensor}  Atacante: {self.rondas_atacante}\n\n"
                "¿Jugar la siguiente ronda?",
                parent=self.ventana
            )
            if continuar:
                self._nueva_ronda()

    def _nueva_ronda(self):
        # Se reinicia el estado del tablero para jugar otra ronda.
        # El marcador de rondas se conserva; solo se limpia el mapa.
        self.ronda_actual += 1

        # Bono de dinero por ronda para ambos jugadores
        dinero_base_nuevo = self.DINERO_INICIAL + self.DINERO_POR_RONDA

        # El atacante ademas recibe dinero extra segun el dano que hizo esta ronda
        bono_atacante = (self.dano_atacante_ronda // 10) * self.DINERO_POR_DANO * 10
        dinero_atacante_nuevo = dinero_base_nuevo + bono_atacante

        self._log(f"Nueva ronda — Defensor recibe ${dinero_base_nuevo}, "
                  f"Atacante recibe ${dinero_atacante_nuevo} "
                  f"(bono por dano: ${bono_atacante})")

        self.mapa               = self._crear_mapa()
        self.torres             = []
        self.muros              = []
        self.unidades           = []
        self.vida_base          = 200
        self._ultimo_dano_base  = None
        self.dinero             = dinero_base_nuevo
        self.dinero_atacante    = dinero_atacante_nuevo
        self.turno_combate      = 0
        self.dano_atacante_ronda = 0   # se reinicia el contador de dano
        self.fase               = "construccion"

        # Se reinician los labels del panel
        self.label_dinero.config(text=f"Dinero: ${self.dinero}")
        self.label_dinero_atacante.config(text=f"Dinero: ${self.dinero_atacante}")
        self.label_vida_base.config(text=f"Vida base: {self.vida_base}")
        self.label_fase.config(text="Fase: Construccion", fg="#444444")
        self.label_marcador.config(
            text=f"Ronda {self.ronda_actual}\nDef: {self.rondas_defensor}  Atac: {self.rondas_atacante}"
        )
        self.label_turno.config(text="Turno: 0")

        # Se vuelven a habilitar los botones del defensor y del atacante
        self.boton_terminar.config(state="normal")
        self.boton_terminar_ataque.config(state="normal")
        self.boton_turno.config(state="disabled")

        # Se oculta el panel del atacante hasta que termine la construccion
        self.panel_atacante.grid_remove()

        self.seleccion.set("Muro")
        self.seleccion_unidad.set("Soldado")

        self.dibujar_mapa()

    def _fin_de_partida(self, ganador):
        # Se determina el jugador ganador y se actualiza su registro en el archivo
        if ganador == "defensor":
            nombre_ganador = self.jugador_defensor
            rol_ganador    = "victorias_defensor"
        else:
            nombre_ganador = self.jugador_atacante
            rol_ganador    = "victorias_atacante"

        # Se carga el archivo, se incrementa la victoria y se guarda
        login_temporal = VentanaLogin.__new__(VentanaLogin)
        jugadores = login_temporal.cargar_jugadores()
        if nombre_ganador in jugadores:
            jugadores[nombre_ganador][rol_ganador] += 1
            login_temporal.guardar_jugadores(jugadores)

        messagebox.showinfo(
            "Fin de partida",
            f"¡{nombre_ganador} gano la partida!\n\n"
            f"Defensor: {self.rondas_defensor} rondas\n"
            f"Atacante: {self.rondas_atacante} rondas\n\n"
            "Las victorias han sido guardadas.",
            parent=self.ventana
        )
        self.ventana.destroy()
   
   
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
                                             fill=color, outline=self.COLOR_GRID)

                cx = x1 + self.TAMANO_CASILLA // 2
                cy = y1 + self.TAMANO_CASILLA // 2

                # Si la casilla tiene una torre, se dibuja la inicial de su
                # tipo y, debajo, su indicador de vida
                if valor == self.TORRE:
                    torre = self._torre_en(fila, columna)
                    if torre:
                        inicial = torre.tipo[0]  # "B" = Basica, "P" = Pesada, "M" = Magica
                        self.canvas.create_text(cx, cy - 7, text=inicial,
                                                fill="white", font=("Arial", 10, "bold"))
                        self._dibujar_indicador_vida(torre, cx, cy + 9)

                # Si la casilla tiene un muro, se dibuja su indicador de vida
                elif valor == self.MURO:
                    muro = self._muro_en(fila, columna)
                    if muro:
                        self._dibujar_indicador_vida(muro, cx, cy)

                # Si la casilla tiene una unidad, se dibuja la inicial de su
                # tipo y, debajo, su indicador de vida
                elif valor == self.UNIDAD:
                    unidad = self._unidad_en(fila, columna)
                    if unidad:
                        inicial = unidad.tipo[0]  # "S" = Soldado, "T" = Tanque, "R" = Rapida
                        self.canvas.create_text(cx, cy - 7, text=inicial,
                                                fill="white", font=("Arial", 10, "bold"))
                        self._dibujar_indicador_vida(unidad, cx, cy + 9)

                # La base tambien muestra su indicador de vida, igual que
                # el resto de piezas (vida_antes-dano en el turno del golpe)
                elif valor == self.BASE:
                    self._dibujar_indicador_vida_base(cx, cy)

    def _dibujar_indicador_vida(self, pieza, cx, cy):
        # Dibuja el texto de vida de una pieza (torre, muro o unidad).
        # Si recibio un golpe en el turno actual, se muestra como
        # "vida_antes-dano" (ej. "70-20"); en el siguiente turno, al
        # limpiarse el indicador, se muestra solo la vida actual (ej. "50").
        if getattr(pieza, "ultimo_dano", None):
            vida_antes, dano = pieza.ultimo_dano
            texto = f"{vida_antes}-{dano}"
            color_texto = "yellow"
        else:
            texto = str(pieza.vida)
            color_texto = "white"

        self.canvas.create_text(cx, cy, text=texto,
                                fill=color_texto, font=("Arial", 8, "bold"))

    def _dibujar_indicador_vida_base(self, cx, cy):
        # Igual que _dibujar_indicador_vida, pero para la base, que no es
        # un objeto propio sino un simple contador (self.vida_base).
        if getattr(self, "_ultimo_dano_base", None):
            vida_antes, dano = self._ultimo_dano_base
            texto = f"{vida_antes}-{dano}"
            color_texto = "yellow"
        else:
            texto = str(max(self.vida_base, 0))
            color_texto = "black"

        self.canvas.create_text(cx, cy, text=texto,
                                fill=color_texto, font=("Arial", 8, "bold"))

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
# VENTANA DE TOP DE JUGADORES
# =============================================================
class VentanaTop:
    # Se muestra una ventana con los 5 mejores jugadores en cada rol.
    # Los datos se leen del archivo de jugadores y se ordenan por victorias.

    def __init__(self, parent):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Top de Jugadores")
        self.ventana.resizable(False, False)
        self.ventana.grab_set()

        tk.Label(self.ventana, text="Top de Jugadores",
                 font=("Arial", 14, "bold")).pack(pady=(12, 8))

        # Se crea un frame con dos columnas: defensores y atacantes
        frame = tk.Frame(self.ventana)
        frame.pack(padx=20, pady=(0, 12))

        # --- columna izquierda: top defensores ---
        frame_def = tk.LabelFrame(frame, text="Top Defensores", padx=10, pady=8)
        frame_def.grid(row=0, column=0, padx=(0, 10))

        # --- columna derecha: top atacantes ---
        frame_atac = tk.LabelFrame(frame, text="Top Atacantes", padx=10, pady=8)
        frame_atac.grid(row=0, column=1)

        # Se cargan los jugadores y se arman los rankings
        jugadores = self._cargar_jugadores()
        self._llenar_ranking(frame_def, jugadores, "victorias_defensor")
        self._llenar_ranking(frame_atac, jugadores, "victorias_atacante")

        tk.Button(self.ventana, text="Cerrar", width=12,
                  command=self.ventana.destroy).pack(pady=(0, 10))

    def _cargar_jugadores(self):
        # Se reutiliza la logica de carga de VentanaLogin sin crear una ventana
        login = VentanaLogin.__new__(VentanaLogin)
        return login.cargar_jugadores()

    def _llenar_ranking(self, frame, jugadores, clave):
        # Se ordena la lista de jugadores por la clave dada (victorias_defensor
        # o victorias_atacante) de mayor a menor, y se muestran los primeros 5
        ordenados = sorted(jugadores.items(),
                           key=lambda item: item[1][clave],
                           reverse=True)
        top5 = ordenados[:5]

        if not top5:
            tk.Label(frame, text="Sin datos todavia",
                     font=("Arial", 9), fg="#777777").pack()
            return

        # Encabezados de la tabla
        tk.Label(frame, text="#", width=3,
                 font=("Arial", 9, "bold")).grid(row=0, column=0)
        tk.Label(frame, text="Jugador", width=14,
                 font=("Arial", 9, "bold")).grid(row=0, column=1)
        tk.Label(frame, text="Victorias", width=9,
                 font=("Arial", 9, "bold")).grid(row=0, column=2)

        # Se llena una fila por cada jugador del top
        for posicion, (usuario, datos) in enumerate(top5, start=1):
            victorias = datos[clave]

            # El primer lugar se destaca en dorado
            color = "gold" if posicion == 1 else "black"

            tk.Label(frame, text=str(posicion), width=3,
                     font=("Arial", 9), fg=color).grid(row=posicion, column=0)
            tk.Label(frame, text=usuario, width=14, anchor="w",
                     font=("Arial", 9), fg=color).grid(row=posicion, column=1)
            tk.Label(frame, text=str(victorias), width=9,
                     font=("Arial", 9), fg=color).grid(row=posicion, column=2)


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

        # Boton para ver el ranking; disponible siempre, sin necesidad de login
        tk.Button(self.root, text="Ver Top de Jugadores",
                  command=self.abrir_top, width=20).pack(pady=(0, 8))

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

    def abrir_top(self):
        # Se abre la ventana del ranking de jugadores
        VentanaTop(self.root)


# Aqui arranca todo: al crear el objeto se abre la ventana principal
Interfaz()
