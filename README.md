# Yo Ya No Edito · Kit de 6 agentes para editar tus videos con IA

Este es el equipo con el que [@soyluchorivero](https://www.instagram.com/soyluchorivero/) edita sus reels, simplificado para que lo uses desde cero. Tú grabas y diriges; seis agentes de IA hacen la edición:

**Pietaje → Transcripción → Corte → Gráficos → Música → CapCut**

| Agente | Qué hace |
|---|---|
| [Pietaje](agentes/01-pietaje.md) | Mira la toma completa y anota qué pasa en cada momento |
| [Transcripción](agentes/02-transcripcion.md) | Escribe lo que dices, palabra por palabra y con su tiempo |
| [Corte](agentes/03-corte.md) | Quita pausas, errores y repeticiones sin cortar ideas |
| [Gráficos](agentes/04-graficos.md) | Pone el título, los subtítulos y los apoyos visuales |
| [Música](agentes/05-musica.md) | Elige la música y la mezcla sin tapar tu voz |
| [CapCut](agentes/06-capcut.md) | Arma el video en 4K y deja el proyecto listo para CapCut |

## Palabras que vas a escuchar

- **Agente:** una IA con una tarea y unas reglas fijas. Cada agente de este kit es un archivo de texto con sus instrucciones.
- **Claude Code / Codex:** programas que ponen a trabajar a la IA dentro de tu computadora. Pueden leer y crear archivos y usar otras herramientas. Claude Code es de Anthropic y Codex es de OpenAI.
- **Pietaje:** revisar todo el material grabado antes de editar.
- **Motion:** un gráfico animado, como un título que entra, un sticker que aparece o un texto que se mueve con la voz.
- **GitHub:** una página para guardar y compartir carpetas de proyectos. De aquí descargas este kit.

## Antes de editar: busca tu estilo

Busca 3 a 5 videos con el estilo que quieres en Instagram, TikTok o Pinterest. Fíjate en cómo son los títulos, los subtítulos, los motions, la música y el ritmo. Guarda los enlaces o las capturas en `referencias/` y pásaselos a tu equipo con el encargo.

## Lo que necesitas instalar

La IA no ve ni escucha un video por sí sola. Necesita herramientas:

| Para | Herramienta | Qué hace |
|---|---|---|
| Pensar y coordinar | **Claude Code** o **Codex** | El cerebro: lee las instrucciones y usa las demás herramientas |
| Ver | **ffmpeg** (incluye ffprobe) | Saca fotogramas del video para que la IA los mire y lee sus datos técnicos |
| Escuchar | **Whisper** (`mlx-whisper` en Mac con chip Apple, o `faster-whisper`) | Convierte tu voz en texto, con el tiempo de cada palabra |
| Cortar y mezclar | **ffmpeg** | Corta, acelera la voz, mezcla la música y mide el volumen |
| Animar (opcional) | **Node.js** + **Remotion** | Crea títulos, subtítulos y motions con código y renderiza en 4K |
| Ajustar y exportar | **CapCut** (escritorio) | Revisas el resultado una vez y exportas |
| Scripts | **Python 3** | Lo usan los agentes para tareas de apoyo |

**Atajo:** abre esta carpeta en Claude Code o Codex y escribe:

> Revisa si tengo ffmpeg, Whisper, Python, Node y CapCut. Dime qué falta y cómo instalarlo en mi computadora, paso a paso.

Claude Code y Codex requieren su propio plan o cuenta. Las demás herramientas son gratuitas.

## Cómo usarlo

1. Descarga el kit: botón verde **Code → Download ZIP**, o `git clone` si usas git.
2. Abre la carpeta como proyecto en Claude Code o en Codex.
3. Pon tu toma en `videos/<nombre>/crudo/`.
4. Pega el texto de [plantillas/ENCARGO.md](plantillas/ENCARGO.md).
5. Revisa el resultado en el teléfono. Corrige con tus palabras y di a qué agente va la corrección. Cada corrección se guarda como regla en [reglas/](reglas/).

## Qué hay dentro

- [AGENTS.md](AGENTS.md): el equipo, el orden de trabajo y las reglas comunes. Codex lo lee directamente; Claude Code lo lee a través de `CLAUDE.md`.
- [agentes/](agentes/): un archivo por agente.
- `.codex/agents/` y `.claude/agents/`: las definiciones para llamar a cada agente por su nombre.
- [reglas/](reglas/): las reglas de edición de Luis, como ejemplo para que escribas las tuyas.
- [plantillas/](plantillas/): el `montaje.json` de ejemplo y tu primer encargo.

Este kit no publica en redes, no compra nada y no se conecta a ninguna cuenta. Tú revisas y decides.

Creado para el workshop en vivo «Yo Ya No Edito», 16 de noviembre de 2026.
