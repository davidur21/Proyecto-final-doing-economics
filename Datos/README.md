# **DATOS**

**Universidad del Rosario · Haciendo Economía 2026-2**
**Profesor:** Paul Rodríguez L.
**Estudiantes:** Santiago Gómez, Camilo Ospina, Emily Rodríguez y David Pascagaza

---

Esta carpeta tiene la **estructura de la base de datos** de la encuesta, lista antes del trabajo de campo. Muestra cómo queda una observación una vez se exportan las respuestas de Google Forms, qué significa cada columna y cómo se enlaza cada encuesta con la cafetería donde se hizo.

> ⚠️ **La única fila de `base_estructura_fila_ficticia.csv` es inventada.** No es una respuesta real ni un piloto: sirve solo para mostrar la estructura.
>
> 🔒 **Datos reales (Entrega 4).** Las respuestas del trabajo de campo se suben porque la entrega lo exige. La encuesta es anónima: no tiene nombres, teléfonos, correos ni documentos, y la edad, el ingreso y el estrato van en rangos (Ley 1581 de 2012).

## 📄 Archivos

| Archivo | Contenido |
|---|---|
| `crudos/base_cruda_formulario.csv` | **Datos raw**: exportación de Google Forms tal como salió (89 filas × 43 columnas). No se edita nunca |
| `crudos/base_cruda_con_coordenadas.csv` | **Datos raw unidos a las coordenadas geográficas** de cada cafetería (dirección, latitud, longitud, zona, rol). La genera `Scripts/01_limpieza.R` |
| `limpios/base_limpia.csv` | Las 89 filas con nombres cortos, `id_encuesta`, montos corregidos, variables derivadas, banderas de calidad, `valida` y `motivo_exclusion` |
| `limpios/base_analisis.csv` | Solo las 81 observaciones válidas (`valida = 1`) |
| `limpios/flujo_casos.csv` | De 89 registros a 81 válidas, con cada motivo de exclusión |
| `limpios/resumen_por_tienda.csv` | Encuestas registradas y válidas por cafetería, con coordenadas |
| `limpios/cobertura_por_tienda.csv` | Las 28 tiendas de la hoja: rol, día del plan, meta, encuestas registradas y válidas, fechas de registro en Forms y estado (con válidas, visitada sin válidas o no visitada) |
| `limpios/registro_limpieza.txt` | Registro de cada corrección que hizo el script |
| `base_estructura_fila_ficticia.csv` | La base: una fila por encuesta y una columna por variable (54), en el orden del cuestionario, con una observación ficticia |
| `diccionario_variables.csv` | Cada variable con el título de su pregunta en el formulario, el tipo, los valores permitidos, el valor de la fila ficticia y su origen (formulario o derivada) |
| `hoja_tiendas.csv` | Las 27 cafeterías de la ruta (T01 a T27) más Diosa (T28), agregada en campo, con su código, dirección, coordenadas y enlace de Google Maps, día, zona, rol (principal o reserva), pareja y turno, y las columnas de verificación del criterio que se llenan en campo. Coincide con `Documentacion/Plan de ruta.pdf` |

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

Las variables derivadas (`dap_L`, `dap_U`, `dap_tipo`, `prima_min`, `prima_min_veces_tinto`, `dap_veces_tinto` y `conocimiento`) se calculan con [`Scripts/01_limpieza.R`](../Scripts/01_limpieza.R), nunca a mano. Los montos que la persona no recuerda o no quiere decir quedan **vacíos**: no se escribe 0 ni un valor estimado.

El detalle de la escalera, la meta de 160 encuestas y el plan de análisis está en [`Documentacion/Protocolo de trabajo de campo.pdf`](../Documentacion/Protocolo%20de%20trabajo%20de%20campo.pdf).

## 🧹 Reglas de limpieza (`Scripts/01_limpieza.R`)

| Regla | Qué se hace |
|---|---|
| Elegibilidad | Se excluye quien no compró bebida (A3 = No, 2) o ya había respondido (A4 = Sí, 3) |
| Escalera | Se detiene en el primer "Sí": `dap_L` = precio aceptado, `dap_U` = precio rechazado inmediatamente superior. "No está seguro" = "No" (con `flag_no_seguro`). "No responde" o huecos = `faltante` (2, excluidas) |
| Escalera de 10 precios | El formulario aplicado llegó hasta $6.000 (no tuvo $4.000, $2.500 ni $1.500). Quien rechaza todo queda como `censura_izquierda` con `dap_U` = 6.000 (3 casos) |
| Protesta | Rechazo total con motivo de protesta en E3 → `protesta` (1, excluida) |
| Montos B2, B3, B5 | 0 → vacío (el protocolo prohíbe escribir 0). Valores < 100 se leen en miles (12 → 12.000; 2,5 → 2.500). Se marcan con `flag_monto_corregido` |
| Atípicos | Se conservan con bandera: tinto > $6.000 (`flag_tinto_atipico`, 6), gasto total < $1.000 (`flag_b3_atipico`, 1), gasto total < precio pagado (`flag_b3_menor_b2`, 1) |
| Ingreso | "Hasta $1,75 millones" y "Menos de $1,75 millones" se unen |
| `id_encuesta` | Tienda-iniciales-consecutivo; el consecutivo se cuenta por encuestador dentro de cada tienda para que no se repita entre días |
| Conocimiento (corregido) | D2 y D3 mezclan versiones: el formulario conservó la respuesta correcta de las preguntas anteriores ("de origen" y V60), que eligieron 12 personas en D2 y 13 en D3. Por eso `conocimiento` = aciertos en **D4 y D5** (0 a 2), las únicas iguales para todos; "No sé" = no acierto. Las respuestas viejas se marcan con `flag_d2_version_anterior` y `flag_d3_version_anterior`, y `conocimiento_4items` (D2 a D5) solo se calcula para quien no tiene ninguna, como sensibilidad. Ver [`Registro de versiones del instrumento.md`](../Documentacion/Registro%20de%20versiones%20del%20instrumento.md) |
| Prima en tintos (corregida) | `prima_min_veces_tinto` = (`dap_L` − tinto) ÷ tinto, como pide el plan; antes era `dap_L` ÷ tinto. Esa razón quedó aparte en `dap_veces_tinto` |
| Modalidad | `modalidad` marca las 3 encuestas de Diosa (T28) del 9 de noviembre, que hicieron clientes con el código QR que el equipo dejó en la cafetería, con apoyo del mesero y sin un integrante presente. Se conservan en la muestra; si se excluyen, la mitad de los clientes sigue dejando de comprar entre $14.000 y $16.000. Las demás encuestas con fecha del 9 son visitas del 8 registradas en Forms al día siguiente |
| Grupos | `grupo_estrato`, `grupo_ingreso`, `grupo_educacion`, `grupo_conocimiento` y `grupo_frecuencia`, como en el plan de análisis. Con la medida corregida, `grupo_conocimiento` es 0, 1 o 2 aciertos (antes 0-1, 2-3 y 4) |

**Resultado:** 89 registros → **81 observaciones finales válidas** (74 intervalos cerrados, 4 con censura a la derecha, 3 con censura a la izquierda).

**Coordenadas.** Las de T02 (Café de los Tres) y T03 (Cráneo Sacral) estaban erradas (caían a 5 km y 1,7 km de su dirección) y se corrigieron; la de Diosa (T28) se agregó. Las tres son aproximadas por la cuadrícula de calles y conviene confirmarlas en Google Maps (ver columna `observaciones`).
