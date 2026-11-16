#!/usr/bin/env python3
"""Agente Corte · arma la voz y el video base desde montaje.json.

Uso:  python3 herramientas/cortar.py videos/<nombre>

Lee en videos/<nombre>/trabajo/:
  palabras.json  (de transcribir.py: texto, inicio, fin en segundos de la toma)
  montaje.json   (lo escribe el agente) con:
     "tramos": [{"origen_inicio": s, "origen_fin": s, "motivo": "..."}]
     "velocidad_voz": 1.08
     "correcciones": {"cloud": "Claude", ...}       (opcional)
     "titulo": {"texto", "etiqueta", "origen_fin"}
     "pasos": [{"n", "nombre", "origen", "tarjeta": {...}}]  (tiempos en segundos de la toma)
Escribe:
  base-4k.mp4  (vertical 2160x3840, solo los tramos, voz acelerada)
  montaje.json con "palabras", "duracion" y los tiempos ya pasados al reel ("inicio").
"""
import json, pathlib, subprocess, sys

FF = "ffmpeg"
for c in ["/Users/reset/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
    if pathlib.Path(c).exists(): FF = c; break

base = pathlib.Path(sys.argv[1]).resolve()
T = base / "trabajo"
m = json.loads((T / "montaje.json").read_text(encoding="utf-8"))
tramos = [(t["origen_inicio"], t["origen_fin"]) for t in m["tramos"]]
vel = float(m.get("velocidad_voz", 1.0))
corr = {k.lower(): v for k, v in m.get("correcciones", {}).items()}

def al_reel(s):
    """Pasa un segundo de la toma original al segundo del reel."""
    acc = 0.0
    for a, b in tramos:
        if s < a: return round(acc / vel, 2)
        if a <= s <= b: return round((acc + s - a) / vel, 2)
        acc += b - a
    return round(acc / vel, 2)

palabras, acc = [], 0.0
for a, b in tramos:
    for w in json.loads((T / "palabras.json").read_text(encoding="utf-8")):
        if w["fin"] > a + 0.05 and w["inicio"] < b - 0.05:
            txt = corr.get(w["texto"].lower(), w["texto"])
            if txt:
                palabras.append({"texto": txt, "inicio": round((acc + max(w["inicio"], a) - a) / vel, 3),
                                 "fin": round((acc + min(w["fin"], b) - a) / vel, 3)})
    acc += b - a
# "frases": [["la gente", "el agente"], ...] corrige pares de palabras que Whisper entendió mal
for viejo, nuevo in m.get("frases", []):
    v, n = viejo.lower().split(), nuevo.split()
    i = 0
    while i < len(palabras) - len(v) + 1:
        if [w["texto"].lower().strip(".,") for w in palabras[i:i + len(v)]] == [x.strip(".,") for x in v]:
            fin = palabras[i + len(v) - 1]["texto"][-1] if palabras[i + len(v) - 1]["texto"][-1] in ".,?" else ""
            grupo = palabras[i:i + len(v)]
            nuevas = [{"texto": n[j] + (fin if j == len(n) - 1 else ""), "inicio": grupo[min(j, len(grupo) - 1)]["inicio"],
                       "fin": grupo[min(j, len(grupo) - 1)]["fin"]} for j in range(len(n))]
            palabras[i:i + len(v)] = nuevas
            i += len(n)
        else:
            i += 1
palabras = [w for w in palabras if w["texto"].strip()]
m["palabras"] = palabras
m["duracion"] = round(acc / vel, 3)
if "titulo" in m:
    m["titulo"]["inicio"] = 0
    m["titulo"]["fin"] = al_reel(m["titulo"].get("origen_fin", tramos[0][1]))
for p in m.get("pasos", []):
    p["inicio"] = al_reel(p["origen"])
    for r in p.get("tarjeta", {}).get("resaltes", []):
        r["inicio"] = al_reel(r["origen"])
(T / "montaje.json").write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

salida = T / "base-4k.mp4"
if not salida.exists() or "--rehacer" in sys.argv:
    fuente = next((base / "crudo").glob("*"))
    parts, cat = "", ""
    for i, (a, b) in enumerate(tramos):
        parts += f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[a{i}];"
        cat += f"[v{i}][a{i}]"
    # vertical 9:16: si la toma es horizontal se recorta al centro
    fc = parts + f"{cat}concat=n={len(tramos)}:v=1:a=1[vc][ac];[vc]setpts=PTS/{vel},scale=-2:3840,crop=2160:3840,fps=30[vo];[ac]atempo={vel},loudnorm=I=-16:TP=-1.5[ao]"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(fuente), "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]",
                    "-c:v", "h264_videotoolbox", "-b:v", "45M", "-c:a", "aac", "-b:a", "256k", str(salida)], check=True)
print(f"Listo: {m['duracion']} s de reel, {len(palabras)} palabras, {len(m.get('pasos', []))} pasos.")
