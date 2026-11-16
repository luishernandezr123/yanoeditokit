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
     o bien "escenas" (modo dinámico) y "golpes": ver plantillas/montaje.json
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
crudos = sorted(x for x in (base / "crudo").iterdir() if not x.name.startswith("."))
# Cada tramo puede decir de qué toma sale ("archivo"); si no, se usa la primera.
tramos = [(t["origen_inicio"], t["origen_fin"]) for t in m["tramos"]]
archivos = [t.get("archivo", crudos[0].name) for t in m["tramos"]]
vel = float(m.get("velocidad_voz", 1.0))
corr = {k.lower(): v for k, v in m.get("correcciones", {}).items()}

def al_reel(s, archivo=None):
    """Pasa un segundo de una toma original al segundo del reel."""
    archivo = archivo or archivos[0]
    acc = 0.0
    for (a, b), f in zip(tramos, archivos):
        if f == archivo and a <= s <= b: return round((acc + s - a) / vel, 2)
        acc += b - a
    acc = 0.0
    for (a, b), f in zip(tramos, archivos):
        if f == archivo and s < a: return round(acc / vel, 2)
        acc += b - a
    return round(acc / vel, 2)

palabras, acc, usadas = [], 0.0, set()
todas = json.loads((T / "palabras.json").read_text(encoding="utf-8"))
for t, (a, b), f in zip(m["tramos"], tramos, archivos):
    # Whisper a veces pone una palabra dentro del silencio que se quitó: si el tramo solo quita una pausa
    # ("pausa": true), esas palabras pasan a su inicio.
    lo = a - 0.6 if t.get("pausa") else a + 0.05
    for k, w in enumerate(todas):
        # cada palabra sale una sola vez, aunque toque dos tramos
        if k not in usadas and w.get("archivo", f) == f and w["fin"] > lo and w["inicio"] < b - 0.05:
            usadas.add(k)
            txt = corr.get(w["texto"].lower(), w["texto"])
            if txt:
                ini = round((acc + max(w["inicio"], a) - a) / vel, 3)
                palabras.append({"texto": txt, "inicio": ini, "fin": max(round((acc + min(w["fin"], b) - a) / vel, 3), ini + 0.1)})
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
    m["titulo"]["fin"] = al_reel(m["titulo"].get("origen_fin", tramos[0][1]), m["titulo"].get("archivo"))
for p in m.get("pasos", []):
    p["inicio"] = al_reel(p["origen"], p.get("archivo"))
    for r in p.get("tarjeta", {}).get("resaltes", []):
        r["inicio"] = al_reel(r["origen"], r.get("archivo", p.get("archivo")))
for g in m.get("golpes", []):
    g["inicio"] = al_reel(g["origen"], g.get("archivo"))
# "escenas": [{"origen", "archivo", "modo": cara | tarjeta | pantalla, "tarjeta": {..., "tiempos": [s, ...]}, "paso"}]
for e in m.get("escenas", []):
    e["inicio"] = al_reel(e["origen"], e.get("archivo"))
    tj = e.get("tarjeta", {})
    if "tiempos" in tj:
        tj["aparece"] = [al_reel(x, e.get("archivo")) for x in tj["tiempos"]]
# Inicio de cada tramo en el reel (para los zooms en cada corte)
acc = 0.0
m["cortes"] = []
for t, (a, b) in zip(m["tramos"], tramos):
    if not t.get("pausa"):  # los tramos marcados "pausa" solo quitan un silencio: sin zoom
        m["cortes"].append(round(acc / vel, 3))
    acc += b - a
(T / "montaje.json").write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

salida = T / "base-4k.mp4"
if not salida.exists() or "--rehacer" in sys.argv:
    entradas, idx = [], {}
    for f in archivos:
        if f not in idx: idx[f] = len(idx); entradas += ["-i", str(base / "crudo" / f)]
    parts, cat = "", ""
    for i, ((a, b), f) in enumerate(zip(tramos, archivos)):
        k = idx[f]
        parts += f"[{k}:v]trim={a}:{b},setpts=PTS-STARTPTS,scale=-2:3840,crop=2160:3840,setsar=1,fps=30[v{i}];[{k}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aresample=48000[a{i}];"
        cat += f"[v{i}][a{i}]"
    # vertical 9:16: si la toma es horizontal se recorta al centro
    fc = parts + f"{cat}concat=n={len(tramos)}:v=1:a=1[vc][ac];[vc]setpts=PTS/{vel},fps=30[vo];[ac]atempo={vel},loudnorm=I=-16:TP=-1.5[ao]"
    subprocess.run([FF, "-y", "-loglevel", "error", *entradas, "-filter_complex", fc, "-map", "[vo]", "-map", "[ao]",
                    "-c:v", "h264_videotoolbox", "-b:v", "45M", "-c:a", "aac", "-b:a", "256k", str(salida)], check=True)
print(f"Listo: {m['duracion']} s de reel, {len(palabras)} palabras, {len(m.get('pasos', []))} pasos.")
