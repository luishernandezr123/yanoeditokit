# 3 · Corte

**Misión:** dejar solo lo que suma. Quitar pausas, errores y repeticiones sin cortar ideas a la mitad, y darle ritmo al video.

## Recibe
- `pietaje.md` y los archivos de Transcripción (`palabras.json`, `errores.md`).
- Las preferencias de [reglas/MIS_REGLAS.md](../reglas/MIS_REGLAS.md), como la velocidad de la voz.

## Entrega
- Los tramos dentro de `videos/<nombre>/trabajo/montaje.json`. Cada tramo lleva su inicio y final en la toma original, el motivo y la velocidad.
- `videos/<nombre>/trabajo/voz.wav`: la voz ya cortada, como un único archivo continuo.
- `cortes.md`: una tabla de lo que se quitó y por qué.

## Cómo trabaja
1. Marcar lo que sale: falsos arranques completos, repeticiones, muletillas, pausas largas y esperas sin explicación.
2. Elegir los puntos de corte **entre frases o entre palabras**, usando los tiempos de `palabras.json` y comprobando el audio, no solo el texto.
3. Escribir los tramos en `montaje.json` en orden.
4. Aplicar la velocidad elegida a la voz sin cambiar el tono (por ejemplo, `atempo` de ffmpeg).
5. Generar `voz.wav` desde la toma original y comprobar que dura lo mismo que la suma de los tramos.

## Reglas
- **Frases completas.** Nunca dejar media palabra ni una frase que empieza y no termina.
- **Un falso arranque se quita entero:** se borra el intento completo y se deja solo el bueno, no solo el silencio entre los dos.
- **Cortar silencio no es corregir.** Además de las pausas, hay que quitar lo que se repite o no aporta, explicando el motivo.
- **No inventar acciones.** Un corte no debe hacer parecer que algo pasó solo o más rápido de lo que pasó.
- **Voz continua.** El audio final se arma como un solo WAV desde la fuente original. Nunca se pegan trozos de AAC/MP3: se desincronizan.
- **Nada de cuadros congelados** para tapar un corte.
- Si en el montaje entra una reacción o un inserto, la voz se pausa ahí y todos los tiempos se recalculan desde `montaje.json`.

## Antes de entregar
- Duración final = suma de los tramos ÷ velocidad.
- Escuchar cada unión: no hay sílabas mordidas ni respiraciones cortadas a la mitad.
- La voz coincide con los labios al principio, en el medio y al final.

## Ejemplo real (VID 17 de Luis)
Una toma de 157,74 s quedó en 89,83 s: 12 tramos, voz a 1,08×. Se quitaron 2 reinicios, una repetición y la pausa más larga, de 7,56 s.
