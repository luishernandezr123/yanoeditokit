#!/usr/bin/env python3
"""Prueba corta del equipo Ya No Edito · comprueba que las herramientas obligatorias funcionan de verdad.

Uso (desde la carpeta del kit):  python3 herramientas/prueba_equipo.py

1. ffmpeg crea 3 s de audio: una voz sintética en Mac (comando «say») o un tono en Windows y Linux.
2. Whisper lo transcribe con herramientas/transcribir.py (el mismo camino que un video real).
   La primera vez baja el modelo de voz (1,6 a 3 GB): puede tardar varios minutos.
3. Remotion saca una foto de la plantilla remotion-pasos (npx remotion still).
   La primera vez baja un Chrome de Remotion (~100 MB).
Todo se hace en una carpeta temporal. Si public/ de la plantilla está vacía, pone archivos de relleno y los borra al final.
Si las obligatorias del diagnóstico están y las 3 pruebas pasan, crea .equipo-listo en la raíz del kit.
No instala nada.
"""
import datetime, json, os, pathlib, shutil, subprocess, sys, tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import diagnostico as dg  # noqa: E402

try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError): pass

KIT, PLANTILLA = dg.KIT, dg.PLANTILLA
print("Diagnóstico…")
d = dg.diagnosticar()
FF, FP = d["ffmpeg"], d["ffprobe"]
if not FF or not FP:
    sys.exit("Falta ffmpeg o ffprobe: corre primero herramientas/diagnostico.py e instala lo que falta.")
# Los programas que se lanzan desde aquí ven ffmpeg aunque no esté en el PATH de esta terminal
env = dict(os.environ, PATH=os.pathsep.join([str(pathlib.Path(FF).parent), str(pathlib.Path(FP).parent), os.environ.get("PATH", "")]))
tmp = pathlib.Path(tempfile.mkdtemp(prefix="yanoedito-prueba-"))
res = {}


def paso(n, texto): print(f"\n[{n}/3] {texto}", flush=True)


# 1. Audio de 3 s
paso(1, "ffmpeg crea 3 s de audio")
crudo = tmp / "prueba" / "crudo"; crudo.mkdir(parents=True)
wav = crudo / "voz.wav"
frase = "Hola, esta es una prueba del equipo."
voz = False
if shutil.which("say"):
    aiff = tmp / "voz.aiff"
    voz = subprocess.run(["say", "-o", str(aiff), frase], capture_output=True).returncode == 0 and aiff.exists()
fuente = ["-i", str(tmp / "voz.aiff")] if voz else ["-f", "lavfi", "-i", "sine=frequency=440:duration=3"]
r = subprocess.run([FF, "-y", "-loglevel", "error", *fuente, "-af", "apad", "-t", "3", "-ac", "1", "-ar", "16000", str(wav)],
                   capture_output=True, text=True)
res["audio"] = r.returncode == 0 and wav.exists()
print(("  ok: " + ("voz sintética" if voz else "tono de 440 Hz") + f" en {wav}") if res["audio"] else f"  falló: {r.stderr.strip()[:300]}")

# 2. Whisper
paso(2, "Whisper transcribe el audio (la primera vez baja el modelo)")
if res["audio"]:
    r = subprocess.run([sys.executable, str(KIT / "herramientas/transcribir.py"), str(tmp / "prueba")], env=env)
    pal = tmp / "prueba/trabajo/palabras.json"
    res["whisper"] = r.returncode == 0 and pal.exists()
    if res["whisper"]:
        texto = " ".join(w["texto"] for w in json.loads(pal.read_text(encoding="utf-8")))
        print(f"  ok: oyó «{texto or '(nada: era un tono, es normal)'}»")
        if voz and "prueba" not in texto.lower():
            print("  aviso: Whisper corrió, pero no entendió la frase de prueba. Escucha una transcripción real antes de confiar.")
    else:
        print("  falló: mira el error de arriba.")
else:
    res["whisper"] = False

# 3. Remotion still
paso(3, "Remotion saca una foto de la plantilla (la primera vez baja su Chrome)")
npx = shutil.which("npx")
public = PLANTILLA / "public"; public.mkdir(exist_ok=True)
relleno = []
try:
    for nombre, args in [("base.mp4", ["-f", "lavfi", "-i", "color=c=0x334455:s=1080x1920:d=3:r=30", "-pix_fmt", "yuv420p"]),
                         ("musica.wav", ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "3"]),
                         ("efectos.wav", ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "3"])]:
        if not (public / nombre).exists():
            subprocess.run([FF, "-y", "-loglevel", "error", *args, str(public / nombre)], check=True)
            relleno.append(public / nombre)
    props = tmp / "props.json"
    props.write_text(json.dumps({
        "duracion": 3, "titulo": {"texto": "Equipo listo", "etiqueta": "Prueba", "inicio": 0, "fin": 1},
        "escenas": [{"inicio": 0, "modo": "cara"}, {"inicio": 1.2, "modo": "tarjeta", "tarjeta": {
            "tipo": "lista", "titulo": "Prueba", "lineas": ["ffmpeg", "Whisper", "Remotion"]}}],
        "golpes": [], "palabras": [{"texto": "equipo", "inicio": 1.3, "fin": 1.7}, {"texto": "listo", "inicio": 1.7, "fin": 2.4}],
    }, ensure_ascii=False), encoding="utf-8")
    foto = tmp / "foto.png"
    if not npx:
        print("  falló: no encuentro npx (viene con Node).")
        res["remotion"] = False
    else:
        r = subprocess.run([npx, "--no-install", "remotion", "still", "src/index.tsx", "Reel", str(foto),
                            f"--props={props}", "--frame=60"], cwd=PLANTILLA, env=env)
        res["remotion"] = r.returncode == 0 and foto.exists() and foto.stat().st_size > 0
        print(f"  ok: foto en {foto}" if res["remotion"] else "  falló: mira el error de arriba.")
finally:
    for f in relleno: f.unlink(missing_ok=True)

# Resultado
print("\nResultado")
for k, v in res.items(): print(f"  {'OK   ' if v else 'FALLA'} {k}")
print(f"  {'OK   ' if d['listo'] else 'FALTA'} obligatorias del diagnóstico"
      + ("" if d["listo"] else f": {', '.join(d['faltan_obligatorias'])}"))
if all(res.values()) and d["listo"]:
    (KIT / ".equipo-listo").write_text(
        f"Equipo preparado el {datetime.datetime.now():%d/%m/%Y %H:%M}.\n"
        f"Opcionales sin instalar: {', '.join(d['faltan_opcionales']) or 'ninguna'}.\n"
        "Para revisar otra vez: python3 herramientas/diagnostico.py\n", encoding="utf-8")
    print("\nLISTO: creé .equipo-listo. Ya puedes darle tu primer encargo a luchoeditor.")
    print(f"(Archivos de la prueba en {tmp}; puedes borrarlos.)")
else:
    print("\nNO LISTO: arregla lo que falló y vuelve a correr esta prueba. No creé .equipo-listo.")
    sys.exit(1)
