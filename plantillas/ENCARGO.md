# Tu primer encargo

Pon la toma en `videos/<nombre>/crudo/`, abre esta carpeta en Codex o en Claude Code y pega esto:

```
luchoeditor: edita el video de videos/<nombre>/crudo/ para un reel vertical.
Usa la skill estilo-pasos (modo dinámico) y las referencias de referencias/.

1. Pietaje y Transcripción: revisen la toma y anoten errores, pausas y repeticiones.
2. Corte: sin pausas ni repeticiones (parte cada silencio de más de 0,35 s), voz a 1.15. Corre herramientas/cortar.py.
3. Gráficos: título claro, escenas que alternen cara grande y cara chica con tarjeta, 4 a 6 golpes. Muéstrame un fotograma por escena.
4. Música: una pista CC0 movida de Openverse (skill sonido) y herramientas/mezclar.py --bajo 12.
5. CapCut: renderiza primero en 1080 y luego en 4K; deja el video y los audios listos para CapCut.

Antes de entregarme, revisa todo con tu lista y dime qué comprobaste y qué no.
```

## Cuando lo revises

Corrige con tus palabras y di a quién va la corrección:

> «Gráficos: el subtítulo tapa mi boca, súbelo un poco y mantenlo centrado. Guárdalo como regla».

luchoeditor le pasa la corrección al agente responsable, rehace solo esa parte y la anota en `reglas/APRENDIZAJES.md`.
