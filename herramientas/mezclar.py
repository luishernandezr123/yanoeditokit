#!/usr/bin/env python3
"""Agente Música · deja la voz, la música y los efectos en pistas separadas, listos para Remotion y CapCut.

Uso:  python3 herramientas/mezclar.py videos/<nombre> --musica <archivo de música> [--bajo 12]

Lee videos/<nombre>/trabajo/montaje.json (después de cortar.py) y base-4k.mp4. Escribe en trabajo/audio/:
  voz.wav      la voz ya cortada y acelerada (sale de base-4k.mp4, a −16 LUFS)
  musica.wav   la música repetida hasta cubrir el reel, con entrada y salida suaves,
               --bajo dB por debajo de la voz (12 = se siente; 14–16 = más discreta)
  efectos.wav  whoosh en cada cambio de escena o paso, golpe en cada "golpe" y pop cuando aparece una línea
Los efectos se generan aquí con ffmpeg: no necesitan licencia.
"""
import argparse, json, pathlib, subprocess

FF = "ffmpeg"
for c in ["/Users/reset/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
    if pathlib.Path(c).exists(): FF = c; break

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("--musica", required=True); ap.add_argument("--bajo", type=float, default=12)
a = ap.parse_args()
T = pathlib.Path(a.video).resolve() / "trabajo"
A = T / "audio"; A.mkdir(exist_ok=True)
m = json.loads((T / "montaje.json").read_text(encoding="utf-8"))
dur = m["duracion"]
ff = lambda *x: subprocess.run([FF, "-y", "-loglevel", "error", *x], check=True)

# 1. Voz
ff("-i", str(T / "base-4k.mp4"), "-vn", "-ac", "2", "-ar", "48000", "-af", "loudnorm=I=-16:TP=-1.5", str(A / "voz.wav"))

# 2. Música
ff("-stream_loop", "-1", "-i", a.musica, "-t", f"{dur:.3f}", "-ac", "2", "-ar", "48000",
   "-af", f"afade=t=in:d=0.4,afade=t=out:st={max(0, dur - 1.8):.3f}:d=1.8,loudnorm=I={-16 - a.bajo}:TP=-6",
   str(A / "musica.wav"))

# 3. Efectos propios
sfx = {
    "whoosh": ["-f", "lavfi", "-i", "anoisesrc=d=0.45:c=pink:a=0.8", "-af",
               "highpass=f=500,lowpass=f=6000,afade=t=in:d=0.2,afade=t=out:st=0.2:d=0.25,volume=0.8"],
    "golpe": ["-f", "lavfi", "-i", "sine=f=55:d=0.5", "-f", "lavfi", "-i", "anoisesrc=d=0.08:c=white:a=0.5",
              "-filter_complex", "[0]volume=1.6,afade=t=out:st=0.05:d=0.45[b];[1]highpass=f=2000,afade=t=out:d=0.08[c];[b][c]amix=2:normalize=0"],
    "pop": ["-f", "lavfi", "-i", "sine=f=1100:d=0.1", "-af", "afade=t=out:st=0.01:d=0.09,volume=0.5"],
}
for n, args in sfx.items():
    ff(*args, "-ac", "2", "-ar", "48000", str(A / f"{n}.wav"))

eventos = []
escenas = m.get("escenas") or [{"inicio": p["inicio"]} for p in m.get("pasos", [])]
for i, e in enumerate(escenas):
    if e["inicio"] > 0.2: eventos.append(("whoosh", e["inicio"] - 0.15))
    eventos += [("pop", s) for s in e.get("tarjeta", {}).get("aparece", [])]
eventos += [("golpe", g["inicio"]) for g in m.get("golpes", [])]
eventos = [(n, max(0, s)) for n, s in eventos if s < dur]
entradas, filtros = ["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo:d={dur:.3f}"], []
for k, (n, s) in enumerate(eventos, start=1):
    entradas += ["-i", str(A / f"{n}.wav")]
    filtros.append(f"[{k}]adelay={int(s * 1000)}|{int(s * 1000)}[e{k}]")
mix = "".join(f"[e{k}]" for k in range(1, len(eventos) + 1))
fc = ";".join(filtros) + f";[0]{mix}amix=inputs={len(eventos) + 1}:normalize=0:duration=first" if eventos else "[0]anull"
ff(*entradas, "-filter_complex", fc, "-t", f"{dur:.3f}", str(A / "efectos.wav"))
print(f"Listo: voz, música (−{a.bajo:g} dB bajo la voz) y {len(eventos)} efectos en {A}")
