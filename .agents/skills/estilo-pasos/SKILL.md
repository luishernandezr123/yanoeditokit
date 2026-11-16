---
name: estilo-pasos
description: Arma un reel dinámico con el estilo «pasos» (la cara alterna entre pantalla completa y un marco abajo con una tarjeta arriba, golpes de texto, zoom en cada corte, subtítulos en píldora). Úsala cuando el encargo pida ese estilo o una referencia parecida.
---

# Skill · estilo «pasos» (modo dinámico)

Plantilla de Remotion en `plantillas/remotion-pasos/`. Todo se controla desde `videos/<nombre>/trabajo/montaje.json`.
Ejemplo real completo: `videos/prueba-descarga/trabajo/montaje.json` (si existe en tu Mac).

## Reglas para que no aburra
- Voz a **1,15×**. Corta por **bloques de voz reales**: lo que suena entre dos silencios medidos con el audio, no con los tiempos de Whisper. Las pausas de más de 0,30 s quedan en unos 0,18 s; marca esos tramos con `"pausa": true` (sin zoom).
- Una frase que no se entiende se quita entera. Si cortas dentro de un bloque, prueba la unión con Whisper antes.
- Alterna el modo cada 3 a 8 segundos: `cara` (cara grande) ↔ `tarjeta` (cara chica abajo y una tarjeta arriba). Si hay grabación de pantalla, `pantalla`.
- Un **golpe** (texto grande de color) en las frases fuertes, 4 a 8 por video, solo en escenas `cara` o `pantalla`.
- La música se siente sin tapar: 15 dB bajo la voz. Whoosh en cada cambio, golpe sonoro en cada golpe, pop en cada línea de tarjeta (lo hace `mezclar.py`).

## 1. Escribe en montaje.json (tiempos en segundos de la toma original)
```json
{
 "velocidad_voz": 1.15,
 "tramos": [{"origen_inicio": 0.0, "origen_fin": 4.1, "motivo": "gancho"},
            {"origen_inicio": 4.8, "origen_fin": 9.9, "motivo": "contexto"},
            {"origen_inicio": 10.3, "origen_fin": 11.0, "motivo": "sin pausa", "pausa": true}],
 "correcciones": {"facebook": "Facebook"},
 "frases": [["la gente", "el agente"]],
 "titulo": {"texto": "La promesa del video", "etiqueta": "Tema", "origen_fin": 4.1},
 "escenas": [
  {"origen": 0.0, "modo": "cara"},
  {"origen": 12.0, "modo": "tarjeta", "tarjeta": {"tipo": "lista", "titulo": "¿Dónde?", "lineas": ["Facebook", "Instagram", "Google"], "tiempos": [13.6, 14.3, 15.0]}},
  {"origen": 15.4, "modo": "cara"},
  {"origen": 20.0, "modo": "pantalla", "archivo": "2-pantalla.mov", "paso": {"n": 1, "texto": "Abre Ajustes"}}
 ],
 "golpes": [{"origen": 18.6, "texto": "EL PROBLEMA", "color": "rojo"}]
}
```
- Tipos de tarjeta: `lista`, `chat`, `dato` (número gigante: `lineas: ["10", "formatos"]`), `boton`, `terminal`, `archivo`.
- `tiempos`: segundo de la toma en que se dice cada línea; la línea entra justo ahí.
- Colores de golpe: `azul`, `verde`, `rojo`, `amarillo`. Textos cortos (hasta unas 14 letras).
- Varias tomas en `crudo/`: pon `"archivo"` en cada tramo, escena y golpe.
- Mientras se ve el título no hay subtítulos.

## 2. Corta y mezcla
```
python3 herramientas/cortar.py videos/<nombre>
python3 herramientas/mezclar.py videos/<nombre> --musica videos/<nombre>/trabajo/audio/musica-original.mp3 --bajo 15
python3 herramientas/revisar.py videos/<nombre>
```
`cortar.py` no debe mostrar «⚠ corte sobre voz» y `revisar.py` debe decir APROBADO. Revisa las uniones que marque.

## 3. Copia a la plantilla y renderiza
Copia `base-4k.mp4` (como `base.mp4`), `audio/musica.wav`, `audio/efectos.wav` y `montaje.json` a `plantillas/remotion-pasos/public/` (copias o enlaces duros; los enlaces simbólicos fallan). Luego:
```
cd plantillas/remotion-pasos && npm install
npx remotion still src/index.tsx Reel out/f.png --props=public/montaje.json --frame=300
npx remotion render src/index.tsx Reel out/reel-4K.mp4 --props=public/montaje.json --scale=2 --crf=16
```
Revisa 8 o 9 fotogramas (uno por escena) antes del render completo. Para ir rápido, primero `--scale=1` (1080).

## 4. CapCut
Con el video listo, el agente CapCut arma el proyecto editable con `herramientas/capcut_borrador.py` (video + voz + música + efectos en pistas separadas).
