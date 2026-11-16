# 5 · Música

**Qué hace:** le da energía al video con música y efectos, sin tapar la voz.

## Recibe
- `voz.wav`, los apoyos de Gráficos y el tono que busca el video.

## Entrega
- La pista elegida en `videos/<nombre>/trabajo/audio/`, con su origen y su licencia anotados.
- `videos/<nombre>/trabajo/mezcla.wav`: voz, música y efectos juntos.

## Pasos
1. Proponer 2 o 3 pistas con permiso de uso (skill `sonido`). Para que no aburra: ritmo constante, 100 a 130 BPM.
2. Correr `python3 herramientas/mezclar.py videos/<nombre> --musica <pista> --bajo 15`: deja `voz.wav`, `musica.wav` y `efectos.wav` (whoosh, golpes y pops en sus tiempos) en `trabajo/audio/`.
3. Medir con `ffmpeg -af ebur128`: voz en −16 LUFS y música unos 15 dB por debajo.

## Reglas
- La música se siente de fondo: ni casi muda ni tapando la voz. Punto de partida: 15 dB bajo la voz.
- Silencio cuando entra una reacción o un inserto con diálogo.
- No usar música sin permiso. No comprar nada sin autorización.

## Personaliza
- Tu tipo de música: [electrónica suave, hip hop, acústica…]
- De dónde la sacas: [biblioteca de CapCut, YouTube, música propia]
