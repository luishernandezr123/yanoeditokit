# Ya No Edito · Equipo de edición con 7 agentes

Tú diriges y el equipo edita. **luchoeditor** es el orquestador: recibe tu encargo, reparte el trabajo entre los 6 agentes en orden, revisa cada entrega y te devuelve el video terminado. Nadie publica nada.

## Mi negocio (complétalo)
- Marca o nombre: [________]
- A quién le hablo: [________]
- Tipo de videos: [tutoriales, ventas, opinión, lifestyle…]
- Redes donde publico: [Instagram, TikTok, YouTube Shorts]

## El equipo
```
                Tú (das la idea y revisas)
                          │
                    luchoeditor
             (reparte, revisa y entrega)
                          │
  ┌──────────┬────────────┼───────────┬──────────┬─────────┐
Pietaje  Transcripción  Corte     Gráficos    Música    CapCut
 mira      escucha     recorta    títulos    música y   arma el
 la toma   y escribe   la voz     y motions  efectos    video 4K
```

| # | Agente | Qué hace | Archivo |
|---|---|---|---|
| 0 | luchoeditor | Orquesta, revisa y entrega | [agentes/00-luchoeditor.md](agentes/00-luchoeditor.md) |
| 1 | Pietaje | Revisa la toma completa | [agentes/01-pietaje.md](agentes/01-pietaje.md) |
| 2 | Transcripción | Pasa la voz a texto con tiempos | [agentes/02-transcripcion.md](agentes/02-transcripcion.md) |
| 3 | Corte | Quita pausas, errores y repeticiones | [agentes/03-corte.md](agentes/03-corte.md) |
| 4 | Gráficos | Título, subtítulos y motions | [agentes/04-graficos.md](agentes/04-graficos.md) |
| 5 | Música | Música y efectos sin tapar la voz | [agentes/05-musica.md](agentes/05-musica.md) |
| 6 | CapCut | Video final y paquete para CapCut | [agentes/06-capcut.md](agentes/06-capcut.md) |

## Herramientas y recetas
- `herramientas/transcribir.py`: voz a texto con el tiempo de cada palabra (Whisper).
- `herramientas/cortar.py`: aplica los cortes de `montaje.json` (cada corte al silencio más cercano y alineado al cuadro) y crea el video base vertical.
- `herramientas/mezclar.py`: voz, música (15 dB bajo la voz) y efectos en pistas separadas.
- `herramientas/revisar.py`: luchoeditor escucha, mide y mira el video antes de entregarlo. Sin APROBADO no se entrega.
- Skill `sonido`: música y efectos con licencia libre (Openverse).
- Skill `estilo-pasos` y `plantillas/remotion-pasos/`: el estilo de pasos numerados, en Remotion.
- Las skills están en `.claude/skills/` (Claude Code) y en `.agents/skills/` (Codex).

## Orden de trabajo
0. **Estilo:** mirar las referencias de `referencias/` (Instagram, TikTok o Pinterest) y elegir la plantilla.
1. **Recibir:** la toma va en `videos/<nombre>/crudo/` y no se toca. Varios archivos juntos son tomas de un mismo video.
2. **Entender:** Pietaje y Transcripción revisan la toma.
3. **Cortar:** Corte escribe los tramos en `videos/<nombre>/trabajo/montaje.json` y corre `herramientas/cortar.py`.
4. **Vestir:** Gráficos y Música añaden sus capas al mismo `montaje.json`.
5. **Armar:** CapCut renderiza el video final.
6. **Revisar:** luchoeditor aplica su lista de revisión y dice qué se comprobó y qué no.
7. **Aprender:** cada corrección se guarda en `reglas/APRENDIZAJES.md` y en el agente responsable.

## Reglas comunes
- `montaje.json` es la única fuente de verdad ([plantilla](plantillas/montaje.json)).
- El original no se toca; se trabaja sobre copias.
- Leer `reglas/MIS_REGLAS.md` antes de cada encargo.
- Decir siempre qué se comprobó y qué no. No inventar datos ni resultados.
- Pedir permiso antes de instalar algo, pagar o publicar. No leer ni mostrar claves.
