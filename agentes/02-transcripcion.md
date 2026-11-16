# 2 · Transcripción

**Qué hace:** escribe lo que dices, palabra por palabra y con el segundo exacto de cada una.

## Recibe
- El audio de la toma original.

## Entrega
- `videos/<nombre>/trabajo/transcripcion.txt`: el texto completo.
- `videos/<nombre>/trabajo/palabras.json`: cada palabra con su inicio y su final.
- `videos/<nombre>/trabajo/errores.md`: falsos arranques, repeticiones y palabras dudosas, con su tiempo.

## Pasos
1. Sacar el audio con `ffmpeg`.
2. Transcribir con Whisper, con tiempos por palabra.
3. Revisar nombres y cifras, y volver a transcribir los tramos dudosos.

## Reglas
- Whisper a veces «limpia» los errores: contrasta con el audio.
- Si no se entiende una palabra, márcala como `[duda]`. No inventes.

## Personaliza
- Idioma y acento: [español de Colombia, México…]
- Palabras que siempre deben ir bien escritas: [tu marca, tus productos, tus herramientas]
