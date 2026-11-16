# 2 · Transcripción

**Misión:** escribir lo que se dice en la toma, palabra por palabra y con el tiempo exacto de cada una. Sin esto no hay cortes precisos ni subtítulos sincronizados.

## Recibe
- El audio de cada toma original.
- Nombres propios y términos que deben escribirse bien (por ejemplo: Codex, Claude Code, CapCut, el nombre de la marca).

## Entrega
En `videos/<nombre>/trabajo/`:
- `transcripcion.txt`: el texto completo y legible.
- `palabras.json`: cada palabra con su inicio y su final en segundos de la toma original.
- `errores.md`: la lista de falsos arranques, repeticiones, muletillas y palabras dudosas, con su tiempo.

## Cómo trabaja
1. Extraer el audio de la toma con ffmpeg (WAV, 16 kHz, mono para el reconocimiento).
2. Transcribir con tiempos por palabra usando la herramienta disponible: Whisper local (`mlx-whisper` en Mac, `faster-whisper` u `openai-whisper`) u otra que ya esté instalada.
3. Revisar nombres, cifras y frases raras. Si una palabra suena dudosa, volver a transcribir solo ese tramo.
4. Hacer el inventario de errores: dónde arranca una frase y se repite, dónde hay muletillas, dónde se corrige.

## Reglas
- **El reconocimiento de voz limpia los errores.** Whisper a veces escribe la frase «perfecta» aunque se dijo con tropiezos. Por eso el inventario de errores se contrasta con el audio y con el informe de Pietaje.
- **No inventar palabras.** Si no se entiende, se marca `[duda]` con su tiempo.
- **Guardar dos versiones:** la de auditoría, con los errores tal como suenan, y la limpia para subtítulos. Los subtítulos se regeneran después de los cortes, desde la voz que queda.
- Conservar la forma de hablar de la persona; no corregir su estilo.

## Antes de entregar
- Las palabras cubren toda la toma y sus tiempos no se solapan.
- Los nombres de herramientas y marcas están bien escritos.
- Las dudas que quedan abiertas están listadas.

## Ejemplo real
En el VID 17 de Luis, el reconocimiento escribió «¿cómo esperas facturar BAS?». Al volver a transcribir ese tramo salió lo que se dijo: «más».
