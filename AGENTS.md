# Ya No Edito · Equipo de edición con 6 agentes

Tú diriges y el equipo edita. En este proyecto la sesión principal es la **coordinadora**: recibe el video, reparte el trabajo entre los 6 agentes en orden, junta lo que entregan y te muestra el resultado. La persona que dirige revisa y decide; el equipo no publica nada.

## El equipo

| # | Agente | Qué hace | Archivo |
|---|---|---|---|
| 1 | **Pietaje** | Mira la toma completa y anota qué pasa en cada momento | [agentes/01-pietaje.md](agentes/01-pietaje.md) |
| 2 | **Transcripción** | Escribe lo que dices, palabra por palabra, con su tiempo | [agentes/02-transcripcion.md](agentes/02-transcripcion.md) |
| 3 | **Corte** | Quita pausas, errores y repeticiones; conserva frases completas | [agentes/03-corte.md](agentes/03-corte.md) |
| 4 | **Gráficos** | Pone el título, los subtítulos y los apoyos visuales | [agentes/04-graficos.md](agentes/04-graficos.md) |
| 5 | **Música** | Elige la música y mezcla voz, música y efectos | [agentes/05-musica.md](agentes/05-musica.md) |
| 6 | **CapCut** | Arma el video final en 4K y deja el proyecto listo para ajustar en CapCut | [agentes/06-capcut.md](agentes/06-capcut.md) |

## Orden de trabajo

0. **Estilo.** Antes de editar, revisar los videos o capturas de referencia que haya en `referencias/` o en el encargo (Instagram, TikTok o Pinterest). Gráficos y Música toman de ahí el tipo de títulos, subtítulos, motions, música y ritmo, sin copiar marcas ni contenido ajeno.
1. **Recibir.** Guardar los archivos en `videos/<nombre>/crudo/` sin tocarlos. Si llegan varios archivos juntos, son **tomas de un mismo video**, salvo que se diga otra cosa.
2. **Entender.** Pietaje y Transcripción trabajan en paralelo sobre la toma original.
3. **Cortar.** Corte cruza los dos informes y escribe los tramos en `videos/<nombre>/trabajo/montaje.json`.
4. **Vestir.** Gráficos y Música añaden sus capas al mismo `montaje.json`, sin mover los cortes.
5. **Armar.** CapCut genera el video final y el paquete editable.
6. **Revisar.** La coordinadora comprueba el resultado con la lista de abajo y lo muestra. Cada corrección vuelve **solo** al agente responsable.
7. **Aprender.** Cada corrección de la persona que dirige se guarda en [reglas/APRENDIZAJES.md](reglas/APRENDIZAJES.md) y en el agente responsable, para no repetirla.

## Reglas comunes

- **Un solo montaje.** `montaje.json` es la única fuente de verdad: tiempos, textos, música y capas. Cualquier cambio de velocidad o de cortes se recalcula desde ahí ([plantilla](plantillas/montaje.json)).
- **Edición por fuera.** Se monta y se corrige con archivos y scripts. CapCut se abre **una sola vez**, al final, para revisar y exportar. No se edita a mano en la interfaz para iterar.
- **El original no se toca.** Se trabaja sobre copias en `trabajo/`.
- **Preferencias.** Leer [reglas/MIS_REGLAS.md](reglas/MIS_REGLAS.md) antes de cada encargo. Las indicaciones del encargo actual mandan sobre esas reglas.
- **Honestidad.** Cada agente dice qué comprobó y qué no pudo comprobar. Un archivo creado no es un video revisado. No se inventan datos, herramientas ni resultados.
- **Herramientas.** Usar lo que ya está instalado (ffmpeg, Whisper, Remotion, CapCut). Antes de instalar algo nuevo, pedir permiso. Nada de pagos ni cuentas nuevas sin autorización.
- **Secretos.** No leer ni imprimir claves o tokens.

## Antes de mostrar el video, comprobar

- Que el video dure lo esperado, tenga la resolución pedida (4K: 2160×3840 vertical o 3840×2160 horizontal) y conserve los cuadros por segundo del original.
- Que la voz esté sincronizada con los labios al principio, en el medio y al final.
- Que no queden frases cortadas, falsos arranques ni cuadros congelados.
- Que el título y los subtítulos se lean en el teléfono sin tapar la cara ni los botones de la red.
- Que la música se oiga de fondo y nunca tape la voz.

## Cómo se invoca

- **Codex:** las definiciones están en [.codex/agents/](.codex/agents/). Pide «usa el agente pietaje» o similar. Si la interfaz no lo encuentra, lanza un subagente y pásale la ruta del archivo en `agentes/`.
- **Claude Code:** las definiciones están en [.claude/agents/](.claude/agents/). Claude las usa solo cuando corresponde, o puedes pedirlas por nombre.
- **Cualquier otra IA:** pega el contenido del archivo del agente como instrucción y adjunta la toma o el informe anterior.
