# 6 · CapCut

**Misión:** convertir el `montaje.json` en un video terminado en 4K y dejar el proyecto listo para que la persona que dirige lo abra **una sola vez** en CapCut, lo revise y lo exporte.

## Recibe
- `montaje.json` completo (cortes, gráficos y música) y los archivos de trabajo (`voz.wav`, `mezcla.wav`, `subtitulos.srt` y los recursos).
- La toma original, en la mejor calidad disponible.

## Entrega
En `videos/<nombre>/exportados/`:
- `<nombre>-4K.mp4`: 2160×3840 si es vertical o 3840×2160 si es horizontal, con los mismos cuadros por segundo del original.
- Una vista previa liviana, marcada como interna.
- **El paquete para CapCut:** el proyecto editable generado por script, si el equipo sabe hacerlo; si no, una carpeta con el video base, `subtitulos.srt` y las pistas de audio por separado (voz, música y efectos), lista para importar.
- `control.md`: medidas del archivo final y qué se comprobó.

## Cómo trabaja
1. Renderizar el video desde `montaje.json` con la herramienta disponible: Remotion (composición que lee el JSON) o ffmpeg para montajes simples.
2. Usar como base la toma original, no un video ya comprimido.
3. Preparar el paquete de CapCut con los mismos tiempos del montaje.
4. Solo al final, abrir CapCut **una vez** para revisar, aplicar el filtro «Mejorar» si se usa y exportar.

## Reglas
- **Edición por fuera.** Todos los cambios se hacen en `montaje.json` y se vuelve a generar. No se abre CapCut en cada iteración ni se edita a mano para corregir.
- **Respaldar antes de tocar** un proyecto de CapCut existente, con CapCut cerrado.
- **4K por defecto,** salvo que el encargo pida otra cosa.
- Si la apertura en CapCut falla, diagnosticar y anotar el motivo antes de reintentar.
- Si no hay acceso al escritorio para abrir CapCut, entregar el paquete y avisarlo; no fingir que se exportó.

## Antes de entregar
- Revisar con `ffprobe`: resolución, cuadros por segundo, duración y que tenga audio.
- Decodificar el video completo sin errores (`ffmpeg -v error -i video.mp4 -f null -`).
- Revisar fotogramas del inicio, el medio y el final, y que la voz coincida con los labios.
- Buscar cuadros congelados (`freezedetect`).

## Ejemplo real (VID 17 de Luis)
El máster 4K salió de Remotion leyendo el `montaje.json`. El proyecto de CapCut se generó por script, con el filtro «Mejorar» copiado de un borrador anterior.
