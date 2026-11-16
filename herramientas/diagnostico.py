#!/usr/bin/env python3
"""Diagnóstico del equipo Ya No Edito · revisa qué hay en tu computadora y qué falta.

Uso (desde la carpeta del kit):
    python3 herramientas/diagnostico.py          tabla para leer
    python3 herramientas/diagnostico.py --json   lo mismo en JSON, para el agente

Solo mira: no instala, no cambia ni borra nada y no lee claves. Lo único que sale a internet es una
búsqueda de prueba en Openverse (gratis, sin clave). Por cada herramienta dice si está, para qué sirve,
si es obligatoria u opcional y el comando exacto para instalarla en tu sistema.
Los comandos se corren desde la carpeta del kit. «lo_hace: persona» = pide contraseña o un instalador
con ventanas: el agente te explica los pasos y tú lo haces.
"""
import datetime, glob, importlib.util, json, os, pathlib, platform, re, shutil, subprocess, sys, urllib.request

KIT = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = KIT / "plantillas" / "remotion-pasos"
SO = {"Darwin": "mac", "Windows": "windows"}.get(platform.system(), "linux")
HOME = pathlib.Path.home()
LOCALAPPDATA = pathlib.Path(os.environ.get("LOCALAPPDATA", HOME / "AppData" / "Local"))
VENV_PY = KIT / ".venv" / ("Scripts/python.exe" if SO == "windows" else "bin/python")
EXE = ".exe" if SO == "windows" else ""


def apple_silicon():
    if SO != "mac": return False
    r = correr(["sysctl", "-n", "hw.optional.arm64"])  # vale también si Python corre con Rosetta
    return (r or "").strip() == "1" or platform.machine() == "arm64"


def correr(cmd, timeout=20):
    """Corre un comando de solo lectura y devuelve su salida, o None si no se pudo."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout or r.stderr) if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def clt_mac():
    """En Mac, /usr/bin/git y /usr/bin/python3 abren un instalador si faltan las herramientas de Xcode.
    Para no abrir ventanas, primero se pregunta si están."""
    return SO != "mac" or correr(["xcode-select", "-p"]) is not None


def ejecutable_seguro(ruta):
    if not ruta: return False
    if SO == "mac" and str(ruta) in ("/usr/bin/git", "/usr/bin/python3") and not clt_mac(): return False
    if SO == "windows" and "WindowsApps" in str(ruta): return False  # atajo de la Microsoft Store, no es Python
    return True


# Carpetas donde suelen quedar los programas aunque no estén en el PATH de esta terminal
EXTRA = {
    "mac": ["/opt/homebrew/bin", "/usr/local/bin", HOME / "bin", HOME / ".local/bin",
            HOME / ".local/share/luis-youtube/bin"],  # esta última ya la buscan transcribir.py y revisar.py
    "linux": ["/usr/local/bin", "/usr/bin", HOME / "bin", HOME / ".local/bin"],
    "windows": [LOCALAPPDATA / "Microsoft/WinGet/Links", pathlib.Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "nodejs",
                pathlib.Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/cmd", HOME / ".local/bin"]
    + [pathlib.Path(p) for p in glob.glob(str(LOCALAPPDATA / "Programs/Python/Python3*"))]
    + [pathlib.Path(p) for p in glob.glob(str(LOCALAPPDATA / "Microsoft/WinGet/Packages/Gyan.FFmpeg*/*/bin"))],
}


def buscar(nombre, junto_a=None):
    """Devuelve (ruta, en_path). Primero el PATH; después carpetas conocidas."""
    p = shutil.which(nombre)
    if p and ejecutable_seguro(p): return p, True
    dirs = ([pathlib.Path(junto_a).parent] if junto_a else []) + [pathlib.Path(d) for d in EXTRA[SO]]
    for d in dirs:
        for ext in ([".exe", ".cmd", ""] if SO == "windows" else [""]):
            c = d / f"{nombre}{ext}"
            if c.is_file() and ejecutable_seguro(c): return str(c), False
    return None, False


def version(ruta, *args, patron=r"(\d+\.\d+(?:\.\d+)?)"):
    out = correr([ruta, *(args or ["--version"])])
    m = re.search(patron, out or "")
    return m.group(1) if m else None


# --- comandos de instalación por sistema ----------------------------------------------------------
BREW, _ = buscar("brew")
WINGET = shutil.which("winget")


def por_brew(paquete):
    if BREW:
        return {"comandos": [f"{'brew' if shutil.which('brew') else BREW} install {paquete}"], "lo_hace": "agente"}
    return {"comandos": [f"brew install {paquete}"], "lo_hace": "persona",
            "nota": "Primero hay que instalar Homebrew (pide tu contraseña): ver la fila «Homebrew»."}


def por_winget(id_):
    return {"comandos": [f"winget install -e --id {id_} --accept-source-agreements --accept-package-agreements"],
            "lo_hace": "agente",
            "nota": "Windows puede pedirte permiso en una ventana. Después cierra y abre la terminal para que se vea en el PATH."}


def por_apt(paquetes):
    return {"comandos": [f"sudo apt install -y {paquetes}"], "lo_hace": "persona",
            "nota": "Pide tu contraseña: córrelo tú en una terminal."}


def instalar(mac=None, windows=None, linux=None):
    return {"mac": mac, "windows": windows, "linux": linux}[SO]


# --- revisiones -----------------------------------------------------------------------------------
filas = []


def fila(id_, nombre, tipo, para_que, estado, detalle, como=None, notas=()):
    filas.append({"id": id_, "nombre": nombre, "tipo": tipo, "para_que": para_que, "estado": estado,
                  "detalle": detalle, "instalar": como if estado == "falta" else None, "notas": [n for n in notas if n]})


def rev_homebrew():
    if SO != "mac": return
    necesita = [f["nombre"] for f in filas if f["instalar"] and "Homebrew" in f["instalar"].get("nota", "")]
    estado = "ok" if BREW else ("falta" if necesita else "no hace falta")
    fila("homebrew", "Homebrew (instalador de Mac)", "obligatorio" if necesita else "opcional",
         "Instala ffmpeg, Node y Python con un solo comando. Solo hace falta si falta alguno de ellos.",
         estado, BREW or (f"No está instalado. Lo necesitas para: {', '.join(necesita)}." if necesita
                          else "No está instalado, y por ahora no lo necesitas."),
         {"comandos": ['/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'],
          "lo_hace": "persona",
          "nota": "Pide tu contraseña del Mac. Al final copia y corre las 2 líneas de «Next steps» que muestra."})


PYS = []  # Pythons del sistema para buscar Whisper


def rev_python():
    rutas = []
    for c in [sys.executable] + [buscar(n)[0] for n in (["python", "py"] if SO == "windows" else ["python3", "python"])]:
        # Sin resolver enlaces: el python de una .venv es un enlace al Python base, pero tiene otros paquetes
        if c and ejecutable_seguro(c) and os.path.abspath(c) not in [os.path.abspath(r) for r in rutas]:
            if not os.path.abspath(c).startswith(os.path.abspath(KIT / ".venv")):
                rutas.append(c)
    PYS.extend(rutas)
    v = platform.python_version()
    ok = sys.version_info >= (3, 9)
    notas = []
    if importlib.util.find_spec("ensurepip") is None:
        notas.append("Este Python no puede crear entornos (.venv). En Ubuntu/Debian falta python3-venv.")
    fila("python", "Python 3", "obligatorio", "Corre las herramientas del kit (transcribir, cortar, mezclar, revisar).",
         "ok" if ok and not notas else "falta", f"{v} · {sys.executable}",
         instalar(mac=por_brew("python"), windows=por_winget("Python.Python.3.12"),
                  linux=por_apt("python3 python3-venv python3-pip")),
         notas + ([] if ok else ["Hace falta Python 3.9 o más nuevo."]))


def rev_git():
    g, en_path = buscar("git")
    v = version(g) if g else None
    fila("git", "git", "opcional", "Baja el kit y sus actualizaciones (git pull). Sin git se baja en ZIP.",
         "ok" if v else "falta", f"{v} · {g}" if v else "No está instalado.",
         instalar(mac=por_brew("git") if BREW else {"comandos": ["xcode-select --install"], "lo_hace": "persona",
                                                     "nota": "Abre una ventana de Apple: pulsa «Instalar» y espera."},
                  windows=por_winget("Git.Git"), linux=por_apt("git")),
         [] if en_path or not g else [f"Está en {g}, fuera del PATH de esta terminal."])


FF = {}


def rev_ffmpeg():
    ff, ff_path = buscar("ffmpeg")
    fp, fp_path = buscar("ffprobe", junto_a=ff)
    FF.update(ffmpeg=ff, ffprobe=fp)
    vf = version(ff, "-version", patron=r"version\s+(\S+)") if ff else None
    vp = version(fp, "-version", patron=r"version\s+(\S+)") if fp else None
    notas = []
    for n, r, en in (("ffmpeg", ff, ff_path), ("ffprobe", fp, fp_path)):
        if r and not en: notas.append(f"{n} está en {r}, fuera del PATH: los scripts del kit lo encuentran, otros programas quizá no.")
    if ff and "drawtext" not in (correr([ff, "-hide_banner", "-filters"]) or ""):
        notas.append("Este ffmpeg no trae el filtro drawtext (lo usa la skill opcional real-sfx).")
    estado = "falta" if not (vf and vp) else ("aviso" if any("fuera del PATH" in n for n in notas) else "ok")
    det = " · ".join(x for x in [f"ffmpeg {vf} ({ff})" if vf else "ffmpeg: no está",
                                 f"ffprobe {vp} ({fp})" if vp else "ffprobe: no está"])
    fila("ffmpeg", "ffmpeg y ffprobe", "obligatorio",
         "Los ojos y las tijeras: saca fotos del video, lee sus datos, corta, acelera la voz y mezcla.",
         estado, det, instalar(mac=por_brew("ffmpeg"), windows=por_winget("Gyan.FFmpeg"), linux=por_apt("ffmpeg")), notas)


def modulos_en(py):
    """Qué módulos de Whisper tiene un Python, sin importarlos (rápido y sin efectos)."""
    codigo = "import importlib.util as u;print(','.join(m for m in ('mlx_whisper','faster_whisper') if u.find_spec(m)))"
    if os.path.abspath(py) == os.path.abspath(sys.executable):  # sin resolver enlaces (ver rev_python)
        return [m for m in ("mlx_whisper", "faster_whisper") if importlib.util.find_spec(m)]
    out = correr([str(py), "-c", codigo])
    return [m for m in (out or "").strip().split(",") if m]


def rev_whisper():
    paquete = "mlx-whisper" if apple_silicon() else "faster-whisper"
    encontrado = []  # (dónde, ruta, módulos)
    if VENV_PY.exists():
        encontrado.append(("la .venv del kit", str(VENV_PY), modulos_en(VENV_PY)))
    for p in PYS:
        encontrado.append(("el Python del sistema", p, modulos_en(p)))
    usable = [(d, r, m) for d, r, m in encontrado if m]
    if usable:
        d, r, m = usable[0]
        estado, det = "ok", f"{m[0].replace('_', '-')} en {d} ({r})"
    else:
        estado = "falta"
        det = ("Ni la .venv del kit ni el Python del sistema tienen Whisper."
               if VENV_PY.exists() else "No hay .venv en el kit y el Python del sistema no tiene Whisper.")
    notas = []
    if VENV_PY.exists() and not usable:
        notas.append("La .venv del kit existe pero no tiene Whisper: basta con el pip install.")
    # Pistas: Whisper instalado en otro entorno que el kit no usa
    otros = sorted({str(pathlib.Path(x).parents[3]) for pat in (".venvs/*/lib/python*/site-packages/*whisper",
                                                                ".virtualenvs/*/lib/python*/site-packages/*whisper")
                    for x in glob.glob(str(HOME / pat)) if x.endswith(("mlx_whisper", "faster_whisper"))})
    for o in otros:
        notas.append(f"Hay Whisper en otro entorno ({o}), pero los scripts del kit no lo usan.")
    hub = HOME / ".cache/huggingface/hub"
    modelo = "models--mlx-community--whisper-large-v3-turbo" if paquete == "mlx-whisper" else "models--Systran--faster-whisper-large-v3"
    notas.append("El modelo de voz ya está descargado." if (hub / modelo).exists()
                 else f"La primera transcripción baja el modelo ({'~1,6' if paquete == 'mlx-whisper' else '~3'} GB).")
    if SO == "windows":
        crear, pip = "python -m venv .venv", r".venv\Scripts\python -m pip"
    else:
        crear, pip = "python3 -m venv .venv", ".venv/bin/pip"
    como = {"comandos": ([] if VENV_PY.exists() else [crear]) + [f"{pip} install -U pip", f"{pip} install {paquete}"],
            "lo_hace": "agente", "nota": "Se instala dentro del kit (.venv): no toca el Python de tu computadora."}
    fila("whisper", f"Whisper ({paquete})", "obligatorio",
         "Los oídos: convierte tu voz en texto con el tiempo de cada palabra.", estado, det, como, notas)


def rev_node():
    n, n_path = buscar("node")
    m, _ = buscar("npm", junto_a=n)
    vn = version(n) if n else None
    vm = version(m) if m else None
    viejo = vn and int(vn.split(".")[0]) < 18
    estado = "falta" if not (vn and vm) or viejo else ("aviso" if not n_path else "ok")
    det = f"node {vn} · npm {vm} ({n})" if vn and vm else ("node sin npm" if vn else "No está instalado.")
    notas = (["Remotion necesita Node 18 o más nuevo."] if viejo else []) + \
            ([] if n_path or not n else [f"Está en {n}, fuera del PATH de esta terminal."])
    fila("node", "Node.js y npm", "obligatorio", "Corre Remotion, que dibuja títulos, subtítulos y motions y renderiza en 4K.",
         estado, det, instalar(mac=por_brew("node") if BREW else {
             "comandos": ["Descarga el instalador LTS de https://nodejs.org y ábrelo"], "lo_hace": "persona",
             "nota": "Instalador con ventanas: pulsa Continuar hasta el final y escribe tu contraseña del Mac."},
             windows=por_winget("OpenJS.NodeJS.LTS"), linux=por_apt("nodejs npm")), notas)


def rev_remotion():
    nm = PLANTILLA / "node_modules"
    bin_ = nm / ".bin" / ("remotion.cmd" if SO == "windows" else "remotion")
    v = None
    try: v = json.loads((nm / "remotion/package.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError): pass
    ok = bin_.exists() and v
    fila("remotion", "Remotion (plantilla remotion-pasos)", "obligatorio",
         "Las piezas de Remotion que usa la plantilla de pasos. Se instalan dentro de la plantilla.",
         "ok" if ok else "falta", f"remotion {v} en plantillas/remotion-pasos/node_modules" if ok else "Falta node_modules en la plantilla.",
         {"comandos": ["npm install --prefix plantillas/remotion-pasos"], "lo_hace": "agente",
          "nota": "Necesita Node. Baja unos 300 MB. La primera foto o render baja además un Chrome de Remotion (~100 MB)."})


def rev_capcut():
    if SO == "mac":
        rutas = [pathlib.Path("/Applications/CapCut.app"), HOME / "Applications/CapCut.app"]
    elif SO == "windows":
        rutas = [LOCALAPPDATA / "CapCut"]
    else:
        fila("capcut", "CapCut de escritorio", "opcional", "Abres el proyecto una vez para revisar y exportar.",
             "no disponible", "CapCut no tiene versión de escritorio para Linux.", None,
             ["El video final sale igual con Remotion; puedes retocarlo en CapCut web o en el teléfono."])
        return
    hay = next((r for r in rutas if r.exists()), None)
    fila("capcut", "CapCut de escritorio", "opcional",
         "Abres el proyecto que arma el agente CapCut, lo revisas y exportas. El video final sale igual con Remotion.",
         "ok" if hay else "falta", str(hay) if hay else "No está instalado.",
         {"comandos": ["Descarga CapCut de https://www.capcut.com/download e instálalo"
                       + (" (o desde la App Store)" if SO == "mac" else "")], "lo_hace": "persona",
          "nota": "Instalador con ventanas. Ábrelo una vez e inicia sesión con tu cuenta de CapCut."})


def rev_openverse():
    url = "https://api.openverse.org/v1/audio/?q=pop&license=cc0&page_size=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ya-no-edito-diagnostico"})
        with urllib.request.urlopen(req, timeout=10) as r:
            n = json.loads(r.read().decode("utf-8")).get("result_count")
        estado, det = "ok", f"Responde ({n} sonidos «pop» CC0)."
    except Exception as e:  # sin internet, límite de búsquedas (429) o Openverse caído
        estado, det = "falta", f"No responde: {getattr(e, 'code', '') or type(e).__name__} {getattr(e, 'reason', '') or ''}".strip()
    fila("openverse", "Openverse (música y efectos libres)", "obligatorio",
         "La biblioteca gratis donde el agente Música busca canciones y efectos CC0. Es una página: no se instala.",
         estado, det, {"comandos": [], "lo_hace": "persona",
                       "nota": "No se instala nada: revisa tu internet y vuelve a correr el diagnóstico en un minuto."})


def rev_realsfx():
    sitios = [KIT / ".claude/skills/real-sfx", KIT / ".agents/skills/real-sfx", HOME / ".claude/skills/real-sfx"]
    hay = [str(s) for s in sitios if (s / "SKILL.md").exists()]
    if SO == "windows":
        cmds = ['$t = "$env:TEMP\\clipwing-skills"', "git clone --depth 1 https://github.com/Clipwing/skills.git $t",
                'Copy-Item -Recurse "$t\\skills\\real-sfx" .claude\\skills\\', 'Copy-Item -Recurse "$t\\skills\\real-sfx" .agents\\skills\\']
    else:
        cmds = ['t="$(mktemp -d)"', 'git clone --depth 1 https://github.com/Clipwing/skills.git "$t"',
                'cp -R "$t/skills/real-sfx" .claude/skills/', 'cp -R "$t/skills/real-sfx" .agents/skills/']
    fila("real-sfx", "Real SFX (skill de Clipwing)", "opcional",
         "Pone efectos de sonido grabados de verdad en el cuadro exacto. Tú le das tu biblioteca de sonidos.",
         "ok" if hay else "falta", ", ".join(hay) if hay else "No está instalada.",
         {"comandos": cmds, "lo_hace": "agente",
          "nota": "Necesita git. Reinicia Claude Code o Codex después. Para empezar sin biblioteca propia, su README "
                  "propone «python scripts/setup.py init --uisfx --index» (78 sonidos de interfaz CC0). En Mac pide ffmpeg con drawtext."})


def rev_earshot():
    e, _ = buscar("earshot")
    uv, _ = buscar("uv")
    # uv y earshot quedan en ~/.local/bin, que puede no estar en el PATH de esta terminal: se usan con la ruta completa
    if SO == "windows":
        cmds = ([] if uv else ["winget install -e --id astral-sh.uv --accept-source-agreements --accept-package-agreements"])
        uvc = f'& "{uv or LOCALAPPDATA / "Microsoft/WinGet/Links/uv.exe"}"'  # PowerShell: & corre un programa por su ruta
        esc = '& "$HOME\\.local\\bin\\earshot.exe"'
    else:
        cmds = [] if uv else ["curl -LsSf https://astral.sh/uv/install.sh | sh"]
        uvc, esc = (f'"{uv}"' if uv else "~/.local/bin/uv"), "~/.local/bin/earshot"
    cmds += [f'{uvc} tool install "earshot[mcp] @ git+https://github.com/Leonxlnx/earshot"', f"{esc} doctor --fetch"]
    fila("earshot", "Earshot (oídos para la IA)", "opcional",
         "Describe, compara y revisa sonidos y mezclas para que la IA «escuche» el resultado.",
         "ok" if e else "falta", f"{e} (uv: {uv or 'no está'})" if e else f"No está instalado (uv: {uv or 'no está'}).",
         {"comandos": cmds, "lo_hace": "agente",
          "nota": "Se instala desde GitHub con uv (el paquete «earshot» de PyPI es otro). «doctor --fetch» baja 2 modelos (~1,1 GB)."})


def diagnosticar():
    for r in (rev_python, rev_git, rev_ffmpeg, rev_whisper, rev_node, rev_remotion, rev_capcut,
              rev_openverse, rev_realsfx, rev_earshot, rev_homebrew):
        r()
    filas.sort(key=lambda f: f["id"] != "homebrew")  # Homebrew se muestra primero: va antes que lo demás
    oblig = [f for f in filas if f["tipo"] == "obligatorio"]
    return {
        "fecha": datetime.datetime.now().isoformat(timespec="seconds"),
        "sistema": {"so": SO, "detalle": platform.platform(), "apple_silicon": apple_silicon()},
        "kit": str(KIT),
        "ffmpeg": FF.get("ffmpeg"), "ffprobe": FF.get("ffprobe"),
        "venv_python": str(VENV_PY) if VENV_PY.exists() else None,
        "listo": all(f["estado"] in ("ok", "aviso") for f in oblig),
        "faltan_obligatorias": [f["id"] for f in oblig if f["estado"] == "falta"],
        "faltan_opcionales": [f["id"] for f in filas if f["tipo"] == "opcional" and f["estado"] == "falta"],
        "herramientas": filas,
    }


def tabla(d):
    marca = {"ok": "OK", "falta": "FALTA", "aviso": "AVISO", "no disponible": "N/A", "no hace falta": "--"}
    print(f"Diagnóstico del equipo Ya No Edito · {d['sistema']['detalle']}")
    print(f"Carpeta del kit: {d['kit']}\n")
    print(f"{'Estado':<7} {'Herramienta':<38} {'Tipo':<12} Para qué")
    print("-" * 110)
    for tipo in ("obligatorio", "opcional"):
        for f in [f for f in d["herramientas"] if f["tipo"] == tipo]:
            print(f"{marca[f['estado']]:<7} {f['nombre']:<38} {tipo:<12} {f['para_que']}")
    print("\nDetalle")
    for f in d["herramientas"]:
        print(f"\n[{marca[f['estado']]}] {f['nombre']} ({f['tipo']})\n    {f['detalle']}")
        for n in f["notas"]: print(f"    · {n}")
        c = f["instalar"]
        if c:
            quien = "lo puede hacer el agente" if c["lo_hace"] == "agente" else "lo haces tú; el agente te guía"
            print(f"    Cómo instalar ({quien}):")
            for x in c["comandos"]: print(f"      {x}")
            if c.get("nota"): print(f"    {c['nota']}")
    print()
    if d["listo"]:
        print("Resultado: están todas las obligatorias. " + (
            f"Opcionales sin instalar: {', '.join(d['faltan_opcionales'])}." if d["faltan_opcionales"] else ""))
    else:
        print(f"Resultado: faltan obligatorias: {', '.join(d['faltan_obligatorias'])}. "
              f"Opcionales sin instalar: {', '.join(d['faltan_opcionales']) or 'ninguna'}.")
    print("Los comandos se corren desde la carpeta del kit. Este diagnóstico no instaló nada.")


if __name__ == "__main__":
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError): pass
    d = diagnosticar()
    if "--json" in sys.argv: print(json.dumps(d, ensure_ascii=False, indent=1))
    else: tabla(d)
