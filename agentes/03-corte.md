# 3 · Corte

**Qué hace:** quita pausas, errores y repeticiones sin cortar ideas a la mitad.

## Recibe
- `pietaje.md`, `palabras.json` y `errores.md`.

## Entrega
- Los tramos que se quedan, dentro de `videos/<nombre>/trabajo/montaje.json`, cada uno con su motivo.
- `videos/<nombre>/trabajo/voz.wav`: la voz ya cortada, en un solo archivo.

## Pasos
1. Leer el guion completo y marcar lo que sale: falsos arranques, repeticiones y frases que no se entienden.
2. Hacer el mapa de **bloques de voz**: lo que suena entre dos silencios de 0,18 s o más, medidos con el audio, no con Whisper.
3. Quedarse con bloques enteros. Las pausas de más de 0,30 s se recortan y quedan en unos 0,18 s, que es un respiro natural.
4. Si hay que cortar dentro de un bloque, buscar una micropausa (bajo −45 dB) y **probar la unión**: unir los dos pedazos y transcribirlos con Whisper. Si no suena a frase completa, no se corta ahí.
5. Correr `herramientas/cortar.py`. Ajusta cada corte al punto más silencioso y lo alinea al cuadro. No acepta avisos «⚠ corte sobre voz».
6. Pasar `herramientas/revisar.py` y escuchar las uniones que marque.

## Reglas
- Frases completas: nunca media palabra.
- Si una frase no se entiende ni al volver a escucharla, se quita entera. No se adivina el subtítulo.
- Revisa el desfase de audio de la toma (`transcribir.py` lo avisa) antes de cortar.
- Un falso arranque se quita entero, no solo el silencio.
- La voz se arma desde la toma original, en un solo archivo, para que no se desincronice.

## Personaliza
- Velocidad de tu voz: [1,0× normal / 1,15× para que no aburra]
- Duración ideal de tus videos: [30 s, 60 s, 90 s…]
