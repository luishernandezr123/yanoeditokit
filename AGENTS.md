# Ya No Edito · Equipo de edición con 7 agentes

Tú diriges y el equipo edita. **luchoeditor** es el orquestador: recibe tu encargo, reparte el trabajo entre los 6 agentes en orden, revisa cada entrega y te devuelve el video terminado. Nadie publica nada.

## Primer arranque
Si en la raíz del kit **no existe `.equipo-listo`**, lo primero, antes de cualquier encargo, es la skill **`preparar-equipo`** (`.claude/skills/` o `.agents/skills/`): revisa la computadora con `herramientas/diagnostico.py`, explica qué falta, pide un solo permiso, instala solo lo aceptado y hace una prueba corta. **No se instala nada sin el «sí»** de la persona. Cuando todo funciona, la skill crea `.equipo-listo`.

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
- `herramientas/diagnostico.py`: revisa qué herramientas hay y qué falta (solo mira, no instala). `--json` para el agente.
- `herramientas/prueba_equipo.py`: prueba corta de ffmpeg, Whisper y Remotion; si pasa, crea `.equipo-listo`.
- Skill `preparar-equipo`: el primer arranque (diagnóstico, permiso, instalación y prueba).
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

## Pedidos en palabras simples
La persona no tiene que saber qué herramienta usar. Si te pide algo así, haz esto. Si dice «mi video de videos/clase», el video está en `videos/clase/crudo/`.

| Si te piden… | Haz esto |
|---|---|
| «Instala el kit… y prepara mi equipo» | Copia el repositorio (`git clone`, o el ZIP con curl si no hay git) y sigue la skill `preparar-equipo`. |
| «Preséntame a tu equipo» / «Lee mi negocio y mira mi estilo» | Presenta a los 7 agentes; lee «Mi negocio» y `referencias/`; resume el estilo en 5 puntos y elige la plantilla (normalmente `estilo-pasos`). |
| «Hazme preguntas para llenar mi negocio» | Pregunta, de una en una: marca, a quién le habla, tipo de videos y redes. Guarda las respuestas en «Mi negocio» de este archivo. |
| «Analiza este video y dime cómo es su estilo: [link]» | Intenta bajar el video a `referencias/` (por ejemplo con `yt-dlp`, si está; pide permiso antes de instalarlo). Saca fotos con ffmpeg y describe el estilo en 5 puntos: cómo abre, textos, colores, ritmo y sonido. Si el link no se puede abrir, pide a la persona que guarde el video o capturas en `referencias/`. Se copia el estilo, no el contenido. |
| «Transcribe mi video» / «Dime dónde hay pausas o errores» | `herramientas/transcribir.py videos/<nombre>` y luego Pietaje: pausas, errores y repeticiones con sus tiempos. |
| «Córtalo» / «Quítale lo que sobra» / «Solo en los silencios» / «Voz más rápida» | Corte: bloques de voz reales, `velocidad_voz` 1.15, tramos en `montaje.json` y `herramientas/cortar.py`. Sin avisos «⚠». |
| «Ponle título, recuadros y palabras grandes» (o «tarjetas y golpes») / «con el estilo del video que analizaste» / «Muéstrame una foto de cada parte» | Gráficos con la skill `estilo-pasos` y lo analizado en `referencias/`. «Recuadro» = tarjeta; «palabra grande» = golpe. Escenas cara/tarjeta y una foto por escena con `npx remotion still`. |
| «Ponle música… que no tape mi voz» / «y efectos» / «sonidos en los cambios» | Música con la skill `sonido` (Openverse CC0) y `herramientas/mezclar.py --bajo 15`. Guarda los créditos. |
| «Revisa todo antes de entregarme» | `herramientas/revisar.py videos/<nombre>`. Si no dice APROBADO, corrige y revisa otra vez. |
| «Haz el video final» / «Renderízalo en 1080» / «Déjamelo como proyecto en CapCut» | Render de Remotion en calidad normal, 1080 (`--scale=1`), salvo que pidan máxima calidad (4K, `--scale=2`), en `videos/<nombre>/exportados/`; luego `herramientas/capcut_borrador.py`, primero sin `--instalar` y con CapCut cerrado para instalar. |

## Reglas comunes
- `montaje.json` es la única fuente de verdad ([plantilla](plantillas/montaje.json)).
- El original no se toca; se trabaja sobre copias.
- Leer `reglas/MIS_REGLAS.md` antes de cada encargo.
- Decir siempre qué se comprobó y qué no. No inventar datos ni resultados.
- Pedir permiso antes de instalar algo, pagar o publicar. No leer ni mostrar claves.
