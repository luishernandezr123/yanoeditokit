# Aprendizajes del equipo

Cada vez que corriges a tu equipo, la corrección se guarda aquí y también en el archivo del agente responsable. Así no la vuelves a dar.

## Cómo registrar una corrección

```
### <fecha> · <video>
- Lo que dije: «<tu frase, tal cual>»
- Qué estaba mal: <qué pasó en el video, con el tiempo si aplica>
- Agente responsable: <Pietaje | Transcripción | Corte | Gráficos | Música | CapCut>
- Nueva regla: <la instrucción que el agente debe seguir desde ahora>
- Cómo se comprueba: <qué hay que revisar para saber que no se repite>
```

## Ejemplo

### 10/11/2026 · MG01
- Lo que dije: «La música está muy alta, que no tape la voz».
- Qué estaba mal: la música competía con la voz en las frases importantes.
- Agente responsable: Música.
- Nueva regla: la voz suena entre 12 y 16 dB por encima de la música.
- Cómo se comprueba: medir la mezcla antes de entregar y escuchar el inicio, el medio y el final.

## Registro

### 16/11/2026 · Prueba «guía de 10 formatos»
- Lo que dijo Luis: «Siento que los cortes no están bien hechos… analiza bien la estructura, el guion de lo que estoy hablando».
- Qué estaba mal: el audio de la toma empezaba 0,754 s después del video. Todos los cortes caían a mitad de palabra; Whisper oyó «llega un vez que elegir» y «algo día de hoy».
- Agente responsable: Corte (y Transcripción, por no avisar el desfase).
- Nueva regla:
  - medir el desfase de audio y trabajar todo en el reloj del video;
  - cortar por bloques de voz reales y probar cada unión dudosa con Whisper;
  - alinear los cortes a cuadros;
  - pasar `revisar.py` antes de entregar.
- Cómo se comprueba: `revisar.py` dice APROBADO, con coincidencia de 93 % o más y ninguna unión sobre voz.

### 16/11/2026 · Prueba «guía de 10 formatos»
- Lo que dijo Luis: «La música siento que está un poquito alta».
- Qué estaba mal: la música iba 12 dB bajo la voz.
- Agente responsable: Música.
- Nueva regla: punto de partida, 15 dB bajo la voz (`mezclar.py --bajo 15`).
- Cómo se comprueba: `revisar.py` mide voz y música por separado; la diferencia queda entre 14 y 16 dB.

### 16/11/2026 · Prueba «guía de 10 formatos»
- Lo que dijo Luis: «Que todo esto lo aprenda luchoeditor… no puede haber errores».
- Agente responsable: luchoeditor.
- Nueva regla: luchoeditor no entrega sin `revisar.py` APROBADO y sin mirar una foto por escena (sin tarjetas vacías ni textos sobre la cara).

