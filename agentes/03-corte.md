# 3 · Corte

**Qué hace:** quita pausas, errores y repeticiones sin cortar ideas a la mitad.

## Recibe
- `pietaje.md`, `palabras.json` y `errores.md`.

## Entrega
- Los tramos que se quedan, dentro de `videos/<nombre>/trabajo/montaje.json`, cada uno con su motivo.
- `videos/<nombre>/trabajo/voz.wav`: la voz ya cortada, en un solo archivo.

## Pasos
1. Marcar lo que sale: pausas largas, falsos arranques, repeticiones y muletillas.
2. Cortar entre frases, usando los tiempos de `palabras.json`.
3. Ajustar la velocidad de la voz si hace falta y generar `voz.wav` con `ffmpeg`.

## Reglas
- Frases completas: nunca media palabra.
- Un falso arranque se quita entero, no solo el silencio.
- La voz se arma desde la toma original, en un solo archivo, para que no se desincronice.

## Personaliza
- Velocidad de tu voz: [1,0× normal / 1,1× si hablas lento]
- Duración ideal de tus videos: [30 s, 60 s, 90 s…]
