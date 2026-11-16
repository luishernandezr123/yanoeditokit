---
name: estilo-pasos
description: Arma un reel con el estilo «pasos» (cuadrícula clara, pasos numerados, una tarjeta por paso arriba y la cara abajo en un marco, subtítulos en píldora). Úsala cuando el encargo pida ese estilo o una referencia parecida.
---

# Skill · estilo «pasos»

Plantilla de Remotion en `plantillas/remotion-pasos/`. Todo se controla desde `videos/<nombre>/trabajo/montaje.json`.

## 1. Escribe en montaje.json (tiempos en segundos de la toma original)
```json
{
 "velocidad_voz": 1.08,
 "tramos": [{"origen_inicio": 0.7, "origen_fin": 8.0, "motivo": "gancho"}],
 "correcciones": {"cloud,": "Claude,"},
 "frases": [["la gente", "el agente"]],
 "titulo": {"texto": "Título del gancho", "etiqueta": "PALABRA CLAVE", "origen_fin": 7.9},
 "pasos": [
  {"n": 1, "nombre": "Qué es", "origen": 17.2,
   "tarjeta": {"tipo": "terminal", "titulo": "Terminal", "lineas": ["/init", "Archivo creado"], "final": "Frase grande"}},
  {"n": 2, "nombre": "Ejemplo", "origen": 35.2,
   "tarjeta": {"tipo": "archivo", "titulo": "AGENTS.md", "lineas": ["# Título", "- Línea"], "resaltes": [{"linea": 1, "origen": 40.0}]}}
 ]
}
```
Tipos de tarjeta: `terminal`, `chat`, `archivo` y `lista`. Entre 3 y 5 pasos.

## 2. Corre
```
python3 herramientas/cortar.py videos/<nombre>
```
Calcula los tiempos del reel, corrige los subtítulos y crea `base-4k.mp4`.

## 3. Copia a la plantilla y renderiza
Copia `base-4k.mp4` (como `base.mp4`), `musica.wav`, `whoosh.wav`, `pop.wav` y `montaje.json` a `plantillas/remotion-pasos/public/`. Luego:
```
cd plantillas/remotion-pasos && npm install && npx remotion render src/index.tsx Reel out/reel-4K.mp4 --props=public/montaje.json --scale=2
```
Revisa primero 3 o 4 fotogramas con `npx remotion still ... --frame=N` antes del render completo.
