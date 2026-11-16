#!/usr/bin/env python3
"""Agente Transcripción · voz a texto con el tiempo de cada palabra.

Uso:  python3 herramientas/transcribir.py videos/<nombre>
Usa mlx-whisper (Mac con chip Apple) o, si no está, faster-whisper.
Escribe en videos/<nombre>/trabajo/: audio_16k.wav, palabras.json y transcripcion.txt
"""
import importlib.util, json, os, pathlib, subprocess, sys

# Si este Python no tiene Whisper y el kit tiene su propia .venv (la crea la skill preparar-equipo), se relanza con ella.
KIT = pathlib.Path(__file__).resolve().parent.parent
if not any(importlib.util.find_spec(m) for m in ("mlx_whisper", "faster_whisper")):
    VENV_PY = KIT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if VENV_PY.exists() and not os.environ.get("YANOEDITO_RELANZADO"):
        os.environ["YANOEDITO_RELANZADO"] = "1"  # evita un bucle si la .venv tampoco tiene Whisper
        argv = [str(VENV_PY), str(pathlib.Path(__file__).resolve()), *sys.argv[1:]]
        if os.name == "nt": sys.exit(subprocess.call(argv))
        os.execv(argv[0], argv)
    sys.exit("Falta Whisper (mlx-whisper o faster-whisper). Pídele a luchoeditor que use la skill preparar-equipo, "
             "o corre: python3 herramientas/diagnostico.py")

FF = "ffmpeg"
for c in ["/Users/reset/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
    if pathlib.Path(c).exists(): FF = c; break
FP = "ffprobe"
for c in [str(pathlib.Path(FF).with_name("ffprobe")), "/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe",
          "/Users/reset/.local/share/luis-youtube/bin/ffprobe"]:
    if pathlib.Path(c).exists(): FP = c; break


def desfase(fuente):
    """Segundos que el audio empieza después que el video (pasa en videos de teléfono o WhatsApp).
    Whisper mide desde el primer sonido; los cortes usan el reloj del video. Hay que sumarlo."""
    r = subprocess.run([FP, "-v", "error", "-show_entries", "stream=codec_type,start_time", "-of", "json", str(fuente)],
                       capture_output=True, text=True)
    st = {s["codec_type"]: float(s.get("start_time") or 0) for s in json.loads(r.stdout or "{}").get("streams", [])}
    return round(st.get("audio", 0) - st.get("video", 0), 3) if "video" in st else 0.0

base = pathlib.Path(sys.argv[1]).resolve()
T = base / "trabajo"; T.mkdir(parents=True, exist_ok=True)
# Varias tomas en crudo/ = varias partes de un mismo video. Cada palabra guarda de qué archivo viene.
palabras, lineas = [], []
for fuente in sorted(x for x in (base / "crudo").iterdir() if not x.name.startswith(".")):
    wav = T / f"audio_{fuente.stem}.wav"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(fuente), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    d = desfase(fuente)
    lineas.append(f"## {fuente.name}" + (f"  (el audio empieza {d} s después del video: tiempos ya corregidos)" if d else ""))
    try:
        import mlx_whisper
        r = mlx_whisper.transcribe(str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="es",
                                   word_timestamps=True, condition_on_previous_text=False, verbose=False)
        for s in r["segments"]:
            lineas.append(f"[{s['start'] + d:.2f}–{s['end'] + d:.2f}] {s['text'].strip()}")
            palabras += [{"archivo": fuente.name, "texto": w["word"].strip(), "inicio": round(w["start"] + d, 2), "fin": round(w["end"] + d, 2)} for w in s["words"]]
    except ImportError:
        from faster_whisper import WhisperModel
        segs, _ = WhisperModel("large-v3", compute_type="int8").transcribe(str(wav), language="es", word_timestamps=True)
        for s in segs:
            lineas.append(f"[{s.start + d:.2f}–{s.end + d:.2f}] {s.text.strip()}")
            palabras += [{"archivo": fuente.name, "texto": w.word.strip(), "inicio": round(w.start + d, 2), "fin": round(w.end + d, 2)} for w in s.words]

(T / "palabras.json").write_text(json.dumps(palabras, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
(T / "transcripcion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("\n".join(lineas))
