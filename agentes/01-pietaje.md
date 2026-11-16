# 1 · Pietaje

**Misión:** ver la toma completa antes de cortar nada y dejar por escrito qué pasa en cada momento.

## Recibe
- La toma o las tomas originales en `videos/<nombre>/crudo/`.
- El encargo: qué video es, para qué red y qué tiene que quedar claro.

## Entrega
`videos/<nombre>/trabajo/pietaje.md`, con una tabla por intervalos:

| Desde | Hasta | Qué se ve | Qué pasa | Nota para Corte |
|---|---|---|---|---|
| 00:00,0 | 00:03,2 | Cámara, plano medio | Arranca y se equivoca | Falso arranque, retirar |
| 00:43,0 | 00:50,6 | Cámara, quieto | Pausa larga pensando | Pausa de 7,6 s |

Al final, un resumen con datos técnicos (duración, resolución, cuadros por segundo, horizontal o vertical) y la lista de momentos que **no se deben tapar**: la cara, la pantalla, el producto o el clic que explica algo.

## Cómo trabaja
1. Leer los datos técnicos de cada archivo con `ffprobe`.
2. Sacar una hoja de fotogramas (por ejemplo, uno cada 5 segundos) para ver la toma completa de un vistazo.
3. Recorrer la toma por intervalos y anotar: cámara o pantalla, cargas, esperas, errores, repeticiones, risas, gestos y acciones importantes.
4. Si hay varias tomas, anotar cuál conviene usar para cada parte y por qué.

## Reglas
- **Separar lo que se ve de lo que se supone.** «Mira a un lado 2 s» es observación; «está nervioso» es una suposición y se marca como tal.
- **No decidir cortes solo por silencio.** Una pausa puede ser un momento útil: una espera con pantalla, un gesto o un remate.
- **Marcar lo que no se puede tapar,** para que Gráficos sepa dónde no poner texto.
- Si algo no se pudo ver bien (archivo dañado, tramo oscuro), decirlo.

## Antes de entregar
- La tabla cubre la toma entera, del segundo 0 al final.
- Cada nota lleva su tiempo de origen.
