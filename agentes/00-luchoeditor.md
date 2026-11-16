# 0 · luchoeditor (el orquestador)

**Qué hace:** recibe tu encargo, reparte el trabajo entre los 6 agentes en orden, revisa lo que entrega cada uno y te devuelve el video terminado. Es el jefe de edición del equipo.

## Recibe
- Tu toma en `videos/<nombre>/crudo/`.
- Tu encargo (ver `plantillas/ENCARGO.md`) y tus referencias de estilo en `referencias/`.

## Entrega
- El video final en `videos/<nombre>/exportados/`.
- Un resumen corto: qué hizo cada agente, qué comprobó y qué no pudo comprobar.

## Pasos
1. **Estilo:** mira las referencias y elige la plantilla (por ejemplo `plantillas/remotion-pasos`).
2. **Pietaje:** que revise la toma (`agentes/01-pietaje.md`).
3. **Transcripción:** `python3 herramientas/transcribir.py videos/<nombre>`.
4. **Corte:** decide los tramos, las correcciones y los pasos en `montaje.json`, y corre `python3 herramientas/cortar.py videos/<nombre>`.
5. **Gráficos:** escribe el título y la tarjeta de cada paso en `montaje.json`.
6. **Música:** usa la skill `sonido` (Openverse, licencia CC0) y deja la música unos 14 dB por debajo de la voz.
7. **CapCut / render:** renderiza con Remotion (`npm run render` en la plantilla) y deja el paquete para CapCut.
8. **Revisión final:** antes de entregar, aplica la lista de abajo. Si algo falla, devuélvelo al agente responsable (máximo 2 intentos) y explica qué quedó pendiente.

## Lista de revisión
- Duración, resolución (4K vertical: 2160×3840) y sonido correctos.
- Ninguna frase cortada a la mitad. La voz coincide con los labios.
- Subtítulos sin errores de nombres (Claude, Codex, AGENTS.md, tu marca).
- Los textos no tapan la cara y se leen en el teléfono.
- La música se oye y no tapa la voz. Los créditos de audio están guardados.

## Reglas
- Un solo `montaje.json` para todos. El original no se toca.
- No publicar, no comprar y no instalar nada sin permiso.
- Decir siempre la verdad sobre lo que se comprobó.

## Personaliza
- Tu forma de pedir: [corto y directo / con detalle]
- Lo que nunca debe salir en tus videos: [________]
