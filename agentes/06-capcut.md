# 6 · CapCut

**Qué hace:** arma el video final y crea un proyecto de CapCut editable, con el video y cada audio en su propia pista, listo para revisarlo y exportarlo.

## Recibe
- `montaje.json` completo, los archivos de trabajo y la toma original.
- De Música: la voz, la música y los efectos como archivos separados (`.wav`), con la misma duración que el video.

## Entrega
- `videos/<nombre>/exportados/<nombre>.mp4`: el video final.
- `videos/<nombre>/exportados/<nombre>-sin-audio.mp4`: el mismo video sin sonido, para CapCut.
- `videos/<nombre>/exportados/capcut/<proyecto>/`: el borrador de CapCut, y a su lado `<proyecto>.control.json` con lo que se comprobó.

## Pasos
1. Renderizar el video desde `montaje.json` con Remotion, o con `ffmpeg` si es un montaje simple. Exportar también una copia sin audio.
2. Crear el borrador de CapCut con el script (no toca CapCut):
   ```bash
   python3 herramientas/capcut_borrador.py --nombre "Mi video - CapCut" \
       --video videos/<nombre>/exportados/<nombre>-sin-audio.mp4 \
       --audio voz=videos/<nombre>/trabajo/audio/voz.wav \
       --audio musica=videos/<nombre>/trabajo/audio/musica.wav \
       --audio efectos=videos/<nombre>/trabajo/audio/efectos.wav
   ```
   Queda un proyecto 9:16 con la pista `video` (volumen 0) y una pista de audio por cada `--audio` (volumen 1). Los medios se copian dentro del borrador. Si el script dice `ERROR`, no seguir: leer el mensaje y corregir.
3. Comprobar duración, tamaño, sonido y que la voz coincida con los labios. Leer `avisos` en el informe: por ejemplo, un audio que no dura lo mismo que el video.
4. Mostrar el informe a la persona. **Solo cuando ella lo pida**, con CapCut cerrado del todo, instalarlo:
   ```bash
   python3 herramientas/capcut_borrador.py ... --instalar
   ```
   Repite el mismo comando del paso 2 y añade `--instalar` al final. El borrador se copia a la carpeta de CapCut y se añade a la lista de Inicio. Después se abre CapCut **una sola vez** para revisar y exportar.

## Cómo funciona el script
- CapCut no tiene API. El script escribe los archivos de un borrador igual que los guarda CapCut. Toma el formato de `plantillas/capcut-molde/`, sacado de borradores reales de CapCut y sin datos personales:
  - `borrador/` es un proyecto vacío con sus archivos auxiliares;
  - `pistas.json` tiene un clip de video y uno de audio de muestra;
  - `entrada_registro.json` es la entrada para la lista de Inicio.
- No edites el molde a mano. Si una versión nueva de CapCut deja de abrir los borradores, hay que sacar un molde nuevo de un borrador que esa versión haya guardado. El formato probado es 191.0.0, de CapCut 9.7.1 para Mac.
- Carpeta de CapCut:
  - Mac: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft`;
  - Windows: `%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft`, sin probar todavía.

  Si está en otro sitio, añade `--carpeta-capcut <ruta>`.
- Para medir los medios hacen falta `ffmpeg` y `ffprobe`. El script los busca en el PATH y en las rutas comunes. Si no los encuentra, indica la ruta en las variables `FFMPEG` y `FFPROBE`.

## Protecciones del script
- Sin `--instalar` solo escribe en la carpeta del video.
- Con `--instalar` se niega si:
  - CapCut está abierto;
  - hay archivos `.locked`;
  - ya existe un proyecto con ese nombre.
- Antes de tocar `root_meta_info.json`, que es la lista de CapCut, guarda una copia `root_meta_info.json.bak-<fecha>`.
- Escribe de forma atómica y comprueba el resultado: JSON, IDs nuevos, duraciones, rutas y huellas de cada medio.
- Si la carpeta de CapCut no tiene `root_meta_info.json`, deja el borrador copiado y avisa. No crea esa lista.

## Reglas
- Todo se corrige en `montaje.json` y se vuelve a generar. CapCut se abre una sola vez, al final, con el borrador listo.
- Nunca escribir en la carpeta de CapCut con CapCut abierto. No editar en CapCut para iterar.
- Partir siempre de la toma original, no de un video ya comprimido.
- Decir qué se comprobó y qué falta. Sin `--instalar`, el proyecto todavía no se ha abierto en CapCut.

## Personaliza
- Resolución: [4K 2160×3840 / 1080×1920]
- Dónde publicas: [Instagram, TikTok, YouTube Shorts]
