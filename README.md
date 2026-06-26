# Defensa de Torres — Proyecto II

Juego de estrategia por turnos en Tkinter para 2 jugadores: uno defiende una base con torres y muros, el otro ataca con unidades. Tres rondas, gana quien se lleve 2.

## Cómo jugar

```bash
python Proyecto.py
```

Solo necesita Python 3 con Tkinter (viene incluido en la mayoría de instalaciones estándar).

1. Jugador 1 inicia sesión (o se registra) y elige facción → es el **Defensor**.
2. Jugador 2 hace lo mismo y elige una facción distinta → es el **Atacante**.
3. Fase de construcción: el Defensor coloca muros y torres con el dinero disponible.
4. Fase de despliegue: el Atacante saca sus unidades.
5. Combate por turnos hasta que la base caiga o las unidades sean eliminadas.

Las cuentas y el historial de victorias se guardan en `jugadores.txt`, en texto plano.

## Facciones

| Facción     |
|-------------|
| Naturaleza  |
| Futurista   |
| Medieval    |

Cada partida usa dos facciones distintas (no se pueden repetir entre los dos jugadores).

## Sprites

El tablero soporta sprites `.png` por facción. Si no encuentra el archivo, dibuja la pieza con un color sólido como respaldo, así que el juego corre igual sin arte.

Estructura esperada:

```
sprites/
  Naturaleza/   NormalN.png  TanqueN.png  RapidaN.png  BasicaN.png  PesadaN.png  MagicaN.png  MuroN.png  BaseN.png
  Futurista/    NormalF.png  TanqueF.png  RapidaF.png  BasicaF.png  PesadaF.png  MagicaF.png  MuroF.png  BaseF.png
  Medieval/     NormalM.png  TanqueM.png  RapidaM.png  BasicaM.png  PesadaM.png  MagicaM.png  MuroM.png  BaseM.png
```

Tamaño recomendado: 38×38 px (el tamaño de cada casilla del tablero).

- **Unidades** (Normal/Tanque/Rápida) usan la facción del **Atacante**.
- **Torres, muro y base** usan la facción del **Defensor**.

## Piezas

**Torres** (Defensor): Básica, Pesada (disparo doble), Mágica (alcance infinito, congela).

**Unidades** (Atacante): Soldado, Tanque (escudo), Rápida (esquiva).

**Muro**: solo bloquea el paso, sin ataque.

## Estructura del proyecto

```
Proyecto.py       lógica completa del juego (UI + reglas)
jugadores.txt     se genera solo, guarda usuarios y récords
sprites/          arte por facción (opcional)
```
