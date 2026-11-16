---
name: preparar-equipo
description: Prepara la computadora para el kit Ya No Edito. Revisa qué herramientas hay (Python, ffmpeg, Whisper, Node, Remotion, CapCut, Openverse y las opcionales Real SFX y Earshot), explica lo que falta, pide UN solo permiso, instala solo lo aceptado, hace una prueba corta y crea .equipo-listo. Úsala la primera vez que se abre el kit, cuando no existe .equipo-listo o cuando una herramienta falla.
---

# Skill · preparar-equipo

Objetivo: dejar la computadora lista para editar, sin sorpresas. La persona puede no saber programar: habla claro, sin jerga, y explica cada cosa en una frase.

Reglas que no se rompen:
- **Nada se instala sin un «sí».** Se pregunta una sola vez, con la lista completa.
- **Nunca uses `sudo`.** Lo que pide contraseña o abre un instalador con ventanas lo hace la persona; tú le explicas los pasos.
- No leas ni muestres claves. No compres nada. No cambies nada fuera de la carpeta del kit, salvo lo que la persona aceptó instalar.
- Corre todo desde la carpeta del kit (donde está `AGENTS.md`).

## 1. Diagnóstico
```
python3 herramientas/diagnostico.py --json
```
- En Windows usa `python` (o `py -3`) en vez de `python3`.
- Si no hay Python, el diagnóstico no corre. Explica cómo instalarlo y espera:
  - **Mac:** abre la app Terminal y escribe `xcode-select --install`. Se abre una ventana de Apple: pulsa «Instalar» y espera (trae Python 3 y git).
  - **Windows:** `winget install -e --id Python.Python.3.12`, o el instalador de https://www.python.org marcando «Add python.exe to PATH».
  - **Linux:** `sudo apt install -y python3 python3-venv python3-pip` (lo corre la persona: pide contraseña).
- Lee el campo `herramientas`: cada una trae `estado` (`ok`, `aviso`, `falta`, `no disponible`, `no hace falta`), `tipo` (obligatorio u opcional), `para_que`, `notas` y, si falta, `instalar` con `comandos` y `lo_hace` (`agente` o `persona`).

## 2. Explica y pide UN solo permiso
Muestra una tabla corta y después la pregunta. Ejemplo:

> Revisé tu computadora. Esto es lo que encontré:
>
> | | Herramienta | Para qué |
> |---|---|---|
> | ✅ | ffmpeg | Ve y corta el video |
> | ❌ | Whisper | Escucha tu voz y la pasa a texto |
> | ❌ | Real SFX *(opcional)* | Efectos de sonido grabados de verdad |
>
> **Obligatorias que faltan:** Whisper (se instala dentro del kit, unos 2 GB con su modelo).
> **Opcionales:** Real SFX, Earshot (~1,1 GB).
> **Las haces tú, con mi guía:** ninguna.
>
> ¿Lo instalo? Responde «sí» (obligatorias), «sí, todo» (también las opcionales), o dime cuáles.

- Separa siempre **obligatorias** y **opcionales**. Di los tamaños grandes (modelos de Whisper y Earshot).
- Los `aviso` no se instalan: explícalos en una línea (por ejemplo, «ffprobe está fuera del PATH; el kit lo encuentra igual»).
- Si todo está `ok`, no preguntes nada: pasa al paso 5.
- **Espera la respuesta.** Sin «sí», no instales nada.

## 3. Instala solo lo aceptado
Orden: primero lo que hace la persona (porque lo demás depende de eso), después lo tuyo.

**Lo que hace la persona** (`lo_hace: persona`). Explícalo paso a paso y espera a que diga «listo»:
- **Homebrew (Mac):** 1) Abre la app Terminal. 2) Pega el comando que da el diagnóstico y pulsa Enter. 3) Escribe la contraseña de tu Mac (no se ve mientras escribes; es normal) y Enter. 4) Al final, Homebrew muestra «Next steps» con 2 líneas: cópialas y córrelas. 5) Dime «listo».
- **Node (Mac sin Homebrew):** entra a https://nodejs.org, baja la versión **LTS**, abre el archivo y pulsa Continuar hasta el final; pide tu contraseña.
- **CapCut:** entra a https://www.capcut.com/download (en Mac también está en la App Store), instálalo, ábrelo una vez e inicia sesión.
- **Linux:** los `sudo apt install …` los corre la persona en su terminal.

**Lo que haces tú** (`lo_hace: agente`): corre los `comandos` del diagnóstico tal como vienen, uno por uno, y di qué estás haciendo en palabras simples («Instalo Whisper dentro del kit; tarda unos minutos»).
- Whisper va en `.venv/` dentro del kit: no toca el Python de la computadora. Los scripts del kit usan esa `.venv` solos.
- Remotion: `npm install --prefix plantillas/remotion-pasos`.
- Real SFX se copia a `.claude/skills/real-sfx/` y `.agents/skills/real-sfx/`. Después hay que reiniciar Claude Code o Codex. Lee su `README.md` antes de usarla: necesita una biblioteca de sonidos (o `--uisfx` para empezar con 78 sonidos CC0).
- Earshot se instala desde GitHub con `uv` (nunca `pip install earshot`: ese nombre en PyPI es otro programa). Conectarlo como servidor MCP (`claude mcp add earshot …`) cambia la configuración de Claude Code: pregúntalo aparte; no hace falta para usarlo.
- En Windows, después de un `winget install` cierra y abre la terminal (o la sesión) para que el programa aparezca en el PATH.
- Si un comando falla: lee el error, explícalo en una frase y propón un arreglo. No improvises otro método de instalación sin preguntar. Máximo 2 intentos por herramienta; si sigue fallando, déjalo anotado y sigue con lo demás.

## 4. Vuelve a diagnosticar
```
python3 herramientas/diagnostico.py
```
Comprueba que lo instalado ahora sale `ok`. Si algo sigue faltando, dilo claro.

## 5. Prueba corta
```
python3 herramientas/prueba_equipo.py
```
Hace tres cosas en una carpeta temporal:
1. ffmpeg crea 3 s de audio (voz sintética en Mac, un tono en Windows y Linux).
2. Whisper lo transcribe con `herramientas/transcribir.py`. La primera vez baja el modelo de voz (1,6 a 3 GB): avisa que puede tardar.
3. Remotion saca una foto de la plantilla (`npx remotion still`). La primera vez baja su propio Chrome (~100 MB).

Si todo pasa y las obligatorias están, **crea `.equipo-listo`** en la raíz del kit. Si algo falla, no lo crea: explica qué falló y vuelve al paso 3 solo con eso.
Si solo falla Openverse (sin internet o caído un momento), espera un minuto y repite; si sigue, dilo: lo demás funciona y la música se puede buscar más tarde.

## 6. Cierre
Resume en 3 a 5 líneas:
- Qué quedó instalado y qué no (y por qué).
- Qué hizo o debe hacer todavía la persona.
- Si la prueba pasó y existe `.equipo-listo`.
- Siguiente paso: completar «Mi negocio» en `AGENTS.md` y poner la primera toma en `videos/<nombre>/crudo/`.

No digas que algo funciona si no lo probaste.
