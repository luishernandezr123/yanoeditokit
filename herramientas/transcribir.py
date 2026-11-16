#!/usr/bin/env python3
"""Agente Transcripción · voz a texto con el tiempo de cada palabra.

Uso:  python3 herramientas/transcribir.py videos/<nombre>
Usa mlx-whisper (Mac con chip Apple) o, si no está, faster-whisper.
Escribe en videos/<nombre>/trabajo/: audio_16k.wav, palabras.json y transcripcion.txt
"""
import json, pathlib, subprocess, sys

FF = "ffmpeg"
for c in ["/Users/reset/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
    if pathlib.Path(c).exists(): FF = c; break

base = pathlib.Path(sys.argv[1]).resolve()
T = base / "trabajo"; T.mkdir(parents=True, exist_ok=True)
fuente = next((base / "crudo").glob("*"))
wav = T / "audio_16k.wav"
subprocess.run([FF, "-y", "-loglevel", "error", "-i", str(fuente), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)

palabras, lineas = [], []
try:
    import mlx_whisper
    r = mlx_whisper.transcribe(str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="es",
                               word_timestamps=True, condition_on_previous_text=False, verbose=False)
    for s in r["segments"]:
        lineas.append(f"[{s['start']:.2f}–{s['end']:.2f}] {s['text'].strip()}")
        palabras += [{"texto": w["word"].strip(), "inicio": round(w["start"], 2), "fin": round(w["end"], 2)} for w in s["words"]]
except ImportError:
    from faster_whisper import WhisperModel
    segs, _ = WhisperModel("large-v3", compute_type="int8").transcribe(str(wav), language="es", word_timestamps=True)
    for s in segs:
        lineas.append(f"[{s.start:.2f}–{s.end:.2f}] {s.text.strip()}")
        palabras += [{"texto": w.word.strip(), "inicio": round(w.start, 2), "fin": round(w.end, 2)} for w in s.words]

(T / "palabras.json").write_text(json.dumps(palabras, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
(T / "transcripcion.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("\n".join(lineas))
