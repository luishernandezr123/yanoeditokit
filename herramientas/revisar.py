#!/usr/bin/env python3
"""luchoeditor · revisa un video antes de entregarlo: lo escucha, mide y mira.

Uso:  python3 herramientas/revisar.py videos/<nombre> [videos/<nombre>/exportados/<final>.mp4]

1. Escucha: vuelve a transcribir la voz ya cortada (base-4k.mp4) y la compara con el guion de montaje.json.
   Si falta o sobra una palabra, casi siempre es un corte que mochó una palabra.
2. Uniones: escucha 2,4 s alrededor de cada corte y mide el nivel justo en la unión (sobre −40 dB = corte sobre voz).
3. Música: mide voz y música por separado (trabajo/audio/) y la diferencia (12–16 dB es lo sano).
4. Imagen (si das el video final): medidas, cuadros por segundo, cuadros congelados y una foto por escena.
Escribe trabajo/revision.md y deja las fotos en trabajo/revision/. Termina con «APROBADO» o con la lista de problemas.
"""
import difflib, json, math, pathlib, re, subprocess, sys

FF = "ffmpeg"
for c in ["/Users/reset/bin/ffmpeg", "/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
    if pathlib.Path(c).exists(): FF = c; break
FP = "ffprobe"
for c in [str(pathlib.Path(FF).with_name("ffprobe")), "/opt/homebrew/bin/ffprobe", "/usr/local/bin/ffprobe",
          "/Users/reset/.local/share/luis-youtube/bin/ffprobe"]:
    if pathlib.Path(c).exists(): FP = c; break

base = pathlib.Path(sys.argv[1]).resolve()
T = base / "trabajo"; R = T / "revision"; R.mkdir(exist_ok=True)
final = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
m = json.loads((T / "montaje.json").read_text(encoding="utf-8"))
vel = float(m.get("velocidad_voz", 1.0))
problemas, informe = [], [f"# Revisión de {base.name}\n"]


def run(*a): return subprocess.run([*a], capture_output=True, text=True)
def norm(w): return re.sub(r"[^\wáéíóúñü%]", "", w.lower())


def transcribir(wav):
    try:
        import mlx_whisper
        r = mlx_whisper.transcribe(str(wav), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="es",
                                   word_timestamps=True, condition_on_previous_text=False, verbose=None, temperature=0)
        return [(w["word"].strip(), w["start"]) for s in r["segments"] for w in s["words"]], r["text"].strip()
    except ImportError:
        from faster_whisper import WhisperModel
        segs, _ = WhisperModel("large-v3", compute_type="int8").transcribe(str(wav), language="es", word_timestamps=True)
        segs = list(segs)
        return [(w.word.strip(), w.start) for s in segs for w in s.words], " ".join(s.text.strip() for s in segs)


# 1. Escucha completa
voz = R / "voz_16k.wav"
run(FF, "-y", "-loglevel", "error", "-i", str(T / "base-4k.mp4"), "-vn", "-ac", "1", "-ar", "16000", str(voz))
oidas, _ = transcribir(voz)
esperadas = [w["texto"] for w in m["palabras"]]
a, b = [norm(w) for w in esperadas], [norm(w) for w, _ in oidas]
informe.append("## 1. Escucha completa (Whisper otra vez sobre el video cortado)\n")
dif = 0
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if op == "equal": continue
    t = m["palabras"][min(i1, len(esperadas) - 1)]["inicio"] if esperadas else 0
    linea = f"- {t:5.1f} s · guion: «{' '.join(esperadas[i1:i2]) or '—'}» · se oye: «{' '.join(w for w, _ in oidas[j1:j2]) or '—'}»"
    informe.append(linea); dif += 1
coinc = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
informe.append(f"\nCoincidencia guion ↔ lo que se oye: {coinc:.1%} ({dif} diferencias). Whisper también se equivoca: escucha cada diferencia antes de cortar otra vez.\n")
if coinc < 0.93: problemas.append(f"El audio no coincide con el guion ({coinc:.0%}): revisa las diferencias de la sección 1.")

# 2. Uniones
import array
mu = array.array("f", subprocess.run([FF, "-loglevel", "error", "-i", str(voz), "-f", "f32le", "-"], capture_output=True).stdout)
def nivel(t):
    i = int(t * 16000); v = mu[max(0, i - 240):i + 240]
    return 20 * math.log10(math.sqrt(sum(x * x for x in v) / max(1, len(v))) + 1e-9)
uniones, acc = [], 0.0
for t in m["tramos"]:
    if acc > 0: uniones.append(round(acc / vel, 2))
    acc += t["origen_fin"] - t["origen_inicio"]
informe.append("## 2. Uniones (cada corte, escuchado por separado)\n")
for k, u in enumerate(uniones, 1):
    n = min(nivel(u + k * 0.01) for k in range(-10, 16))  # lo más silencioso cerca de la unión
    w = R / "union.wav"
    run(FF, "-y", "-loglevel", "error", "-ss", f"{max(0, u - 1.2):.2f}", "-t", "2.4", "-i", str(voz), str(w))
    _, texto = transcribir(w)
    marca = "⚠" if n > -40 else "ok"
    informe.append(f"- {marca} unión {k} · {u:5.2f} s · {n:4.0f} dB · «{texto}»")
    if n > -40: problemas.append(f"La unión {k} ({u:.2f} s) cae sobre voz ({n:.0f} dB).")
informe.append("")

# 3. Música
A = T / "audio"
def lufs(f):
    r = run(FF, "-hide_banner", "-i", str(f), "-af", "ebur128", "-f", "null", "-")
    v = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(v[-1]) if v else None
informe.append("## 3. Voz y música\n")
if (A / "voz.wav").exists() and (A / "musica.wav").exists():
    lv, lm = lufs(A / "voz.wav"), lufs(A / "musica.wav")
    informe.append(f"- Voz {lv} LUFS · música {lm} LUFS · diferencia {lv - lm:.1f} dB")
    if lv - lm < 12: problemas.append(f"La música está alta: solo {lv - lm:.1f} dB bajo la voz (mínimo 12).")
    if lv - lm > 18: problemas.append(f"La música casi no se oye: {lv - lm:.1f} dB bajo la voz (máximo 16–18).")
    if (A / "efectos.wav").exists(): informe.append(f"- Efectos {lufs(A / 'efectos.wav')} LUFS")
else:
    informe.append("- Sin pistas separadas en trabajo/audio/ (corre mezclar.py).")
informe.append("")

# 4. Imagen
if final and final.exists():
    informe.append("## 4. Video final\n")
    p = json.loads(run(FP, "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                       "-of", "json", str(final)).stdout)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    informe.append(f"- {v['width']}×{v['height']} · {v['r_frame_rate']} · {float(p['format']['duration']):.2f} s · audio: {'sí' if any(s['codec_type'] == 'audio' for s in p['streams']) else 'NO'}")
    if (v["width"], v["height"]) != (2160, 3840): informe.append("- (no es 4K vertical: si es la entrega final, renderiza con --scale=2)")
    err = run(FF, "-v", "error", "-i", str(final), "-f", "null", "-").stderr.strip()
    informe.append(f"- Decodifica: {'sin errores' if not err else err[:200]}")
    if err: problemas.append("El video final tiene errores de decodificación.")
    fz = re.findall(r"freeze_start: ([\d.]+)", run(FF, "-hide_banner", "-i", str(final), "-vf", "freezedetect=n=-60dB:d=1.5", "-an", "-f", "null", "-").stderr)
    informe.append(f"- Cuadros congelados de más de 1,5 s: {', '.join(fz) if fz else 'ninguno'}")
    if fz: problemas.append(f"Imagen congelada en {', '.join(fz)} s.")
    fotos = []
    for k, e in enumerate(m.get("escenas", []) or [{"inicio": 0.5}]):
        f = R / f"escena-{k:02d}.jpg"; fotos.append(f)
        run(FF, "-y", "-loglevel", "error", "-ss", f"{e['inicio'] + 0.9:.2f}", "-i", str(final), "-frames:v", "1", "-vf", "scale=270:-2", str(f))
    n = len(fotos)
    run(FF, "-y", "-loglevel", "error", *sum([["-i", str(f)] for f in fotos], []), "-filter_complex",
        "".join(f"[{i}]" for i in range(n)) + f"hstack={n}" if n > 1 else "null", str(R / "escenas.jpg"))
    informe.append(f"- Una foto por escena: trabajo/revision/escenas.jpg ({n} escenas). Mírala antes de entregar.")

informe.append("\n## Resultado\n")
informe += [f"- {p}" for p in problemas] or ["APROBADO: sin problemas medibles. Falta tu escucha y tu mirada final."]
(T / "revision.md").write_text("\n".join(informe) + "\n", encoding="utf-8")
print("\n".join(informe))
