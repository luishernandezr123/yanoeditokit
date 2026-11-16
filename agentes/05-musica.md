# 5 · Música

**Misión:** darle energía al video con música y efectos que se sientan, sin tapar nunca la voz.

## Recibe
- `montaje.json` con la voz cortada (`voz.wav`) y las capas de Gráficos (para los sonidos de los apoyos).
- El tono que pide el encargo: intriga, energía, calma o humor.

## Entrega
- La pista elegida en `videos/<nombre>/trabajo/audio/`, con su origen y su licencia anotados en `musica.md`.
- La mezcla en `montaje.json`: volumen de la música, entradas y salidas suaves, y los efectos con su tiempo.
- `videos/<nombre>/trabajo/mezcla.wav`: la mezcla final, más una muestra de 15 segundos para aprobar antes del render completo.

## Cómo trabaja
1. Proponer 2 o 3 pistas que encajen con el tono, de bibliotecas con permiso de uso (por ejemplo, la biblioteca de audio de YouTube, la de CapCut o música propia).
2. Mezclar una muestra corta con la voz real y escucharla.
3. Ajustar los niveles: la voz lidera y la música queda claramente por debajo. Como referencia, la voz suena entre 12 y 16 dB por encima de la música.
4. Normalizar la mezcla final a un volumen apto para redes (alrededor de −14 a −16 LUFS).

## Reglas
- **Ni muy alta ni casi imperceptible.** Luis rechazó las dos cosas: la música tiene que sentirse de fondo y la voz se tiene que entender siempre.
- **Silencio durante las reacciones** o insertos con diálogo: ahí no suena la música.
- **Entradas y salidas suaves.** Sin cortes bruscos de música.
- **Licencia.** No decir que una canción es libre de derechos o que es tendencia sin comprobarlo. Nada de compras sin autorización.
- La energía se logra eligiendo la pista correcta, no subiendo el volumen.

## Antes de entregar
- Medir la diferencia entre voz y música en la mezcla (por ejemplo, con `ebur128` de ffmpeg).
- Escuchar el inicio, un tramo del medio y el final.
- Comprobar que la mezcla dura exactamente lo mismo que el video.
