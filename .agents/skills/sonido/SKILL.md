---
name: sonido
description: Busca y descarga música de fondo y efectos de sonido con licencia libre (Openverse, CC0) para un video, guarda los créditos y deja la mezcla lista. Úsala cuando el agente Música necesite audio.
---

# Skill · sonido

## 1. Buscar en Openverse (gratis, sin clave)
```
curl -s "https://api.openverse.org/v1/audio/?q=lofi&license=cc0&page_size=10"
```
- Cambia `q` por lo que buscas: `lofi`, `whoosh`, `pop`, `click`, `epic`, `ambient`.
- `license=cc0` = libre, sin crédito obligatorio. Para más opciones usa `license_type=commercial` (incluye CC BY: hay que dar crédito).
- Límite anónimo: unas 20 búsquedas por minuto.
- De cada resultado usa: `title`, `creator`, `license`, `url` (el archivo) y `foreign_landing_url` (la página original).

## 2. Descargar y guardar el crédito
```
curl -sL -o videos/<nombre>/trabajo/audio/musica-original.mp3 "<url>"
```
Anota en `videos/<nombre>/trabajo/audio/CREDITOS.md`: título, autor, licencia y enlace. Nunca uses licencias NC (no comerciales).

## 3. Preparar la mezcla
- Repetir la música hasta cubrir el video, con entrada y salida suaves:
```
ffmpeg -stream_loop 2 -i musica-original.mp3 -t <duración> -af "afade=t=in:d=1.5,afade=t=out:st=<duración-2.5>:d=2.5,loudnorm=I=-31:TP=-6" musica.wav
```
- La voz queda en −16 LUFS y la música en −31: unos 15 dB por debajo (o usa herramientas/mezclar.py --bajo 15).
- Efectos propios sin licencia:
```
ffmpeg -f lavfi -i "anoisesrc=d=0.6:c=pink:a=0.9" -af "highpass=f=400,lowpass=f=5000,afade=t=in:d=0.25,afade=t=out:st=0.3:d=0.3" whoosh.wav
ffmpeg -f lavfi -i "sine=f=1200:d=0.12" -af "afade=t=out:st=0.02:d=0.1" pop.wav
```

## Herramientas extra (opcionales)
- **Earshot** (gratis, código abierto): le da «oídos» a la IA para describir, comparar y revisar la mezcla. https://github.com/Leonxlnx/earshot
- **real-sfx** (skill gratis): pone efectos grabados en el cuadro exacto; tú le das los sonidos. https://github.com/Clipwing/skills
- **Freesound** (clave gratis) y **ElevenLabs** (de pago, crea efectos a pedido).
Pide permiso antes de instalar cualquiera.
