# **DATOS**

**Universidad del Rosario · Haciendo Economía 2026-2**
**Profesor:** Paul Rodríguez L.
**Estudiantes:** Santiago Gómez, Camilo Ospina, Emily Rodríguez y David Pascagaza

---

Esta carpeta tiene la **estructura de la base de datos** de la encuesta, lista antes del trabajo de campo. Muestra cómo queda una observación una vez se exportan las respuestas de Google Forms, qué significa cada columna y cómo se enlaza cada encuesta con la cafetería donde se hizo.

> ⚠️ **La única fila de `base_estructura_fila_ficticia.csv` es inventada.** No es una respuesta real ni un piloto: sirve solo para mostrar la estructura. Lleva `registro_ficticio = Sí` y se borra antes del análisis. Las respuestas reales no se suben a este repositorio; solo se publican resultados agregados (Ley 1581 de 2012).

## 📄 Archivos

| Archivo | Contenido |
|---|---|
| `base_estructura_fila_ficticia.csv` | La base: una fila por encuesta y una columna por variable (54), en el orden del cuestionario, con una observación ficticia |
| `diccionario_variables.csv` | Cada variable con el título de su pregunta en el formulario, el tipo, los valores permitidos, el valor de la fila ficticia y su origen (formulario o derivada) |
| `hoja_tiendas.csv` | Las 27 cafeterías de la ruta con su código (T01 a T27), día, zona, rol (principal o reserva), pareja y turno, y las columnas de verificación del criterio que se llenan en campo |

## 🔑 Identificadores

| Identificador | Cómo se construye | Para qué sirve |
|---|---|---|
| `id_encuesta` | Código de la tienda (Z2) + iniciales del encuestador (Z1) + consecutivo del encuestador en el día. Ejemplo: `T01-DP-01` | Identifica cada encuesta de forma única |
| `z2_tienda` | Código T01 a T27 de la lista del formulario | Enlaza la base con `hoja_tiendas.csv` |
| `marca_temporal` | La registra Google Forms al enviar | Ordena el consecutivo y la franja |

## 🧮 Así queda una observación

| Variable | Valor ficticio | Lectura |
|---|---|---|
| `id_encuesta` | T01-DP-01 | Tienda T01, encuestador David Pascagaza, primera encuesta del día |
| `d2` a `d5` (reto cafetero) | 3 de 4 aciertos | Se pregunta **antes** de la escalera de DAP |
| `e1_01` a `e1_06` ($50.000 a $14.000) | No | Rechaza los seis primeros precios |
| `e1_07` ($12.000) | Sí | Primer "sí": la escalera se detiene |
| `e1_08` a `e1_13` | (vacío) | No se preguntaron |
| `b5_precio_tinto` | 2000 | Precio habitual del tinto |
| `dap_L` · `dap_U` · `dap_tipo` | 12000 · 14000 · intervalo | La DAP está entre $12.000 y $14.000 |
| `prima_min` | 10000 | `dap_L` menos el precio del tinto |

Las variables derivadas (`dap_L`, `dap_U`, `dap_tipo`, `prima_min` y `conocimiento`) se calculan con un script en la limpieza, nunca a mano. Los montos que la persona no recuerda o no quiere decir quedan **vacíos**: no se escribe 0 ni un valor estimado.

El detalle de la escalera, la meta de 160 encuestas y el plan de análisis está en [`Documentacion/Protocolo de trabajo de campo.pdf`](../Documentacion/Protocolo%20de%20trabajo%20de%20campo.pdf).
