# Registro de versiones del instrumento

**Proyecto:** ¿Quién paga la diferencia? Disposición a pagar por café de especialidad en Chapinero
**Curso:** Haciendo Economía 2026-2 · Universidad del Rosario · Prof. Paul Rodríguez L.

Este registro responde a la retroalimentación de la Entrega 4. Reconstruye cada versión del instrumento con su fecha, dice qué versión se aplicó en campo y verifica en la base si se mezclaron versiones de las preguntas. Las fechas salen del historial del repositorio (cada versión del protocolo quedó en un commit), de los metadatos del formulario en Google Drive y de las marcas temporales de las respuestas.

---

## 1. Versiones y fechas

| Versión | Fecha y evidencia | DAP | Pregunta abierta de DAP | Seguridad del "sí" (E4) | D2 | D3 |
|---|---|---|---|---|---|---|
| **V1** | 28 oct 2026 · protocolo en el commit `fb3821f` | Doble límite con cinco versiones de precio inicial (A a E) | Sí (E5, opcional) | Sí | Café "de origen" | V60 |
| **V2** | 29 oct 2026 · commit `09f7301` · versión revisada por el profesor el 30 de octubre | Escalera de 10 precios: **$18.000 → $1.500** | **Retirada** | Sí | Café "de origen" | V60 |
| **V3** (protocolo final) | 4 nov 2026 · commits `752e006` y `f163f06` ("Correcciones de la tercera entrega") | Escalera de 13 precios: **$50.000 → $1.500** | Retirada | **Retirada** | **Especies** (arábica y robusta) | **Tostión** clara frente a oscura |
| **Formulario aplicado** | 3 al 9 nov 2026 · marcas temporales de Google Forms | Escalera de **10** precios: **$50.000 → $6.000** | No | No | Título de V3, pero con la respuesta correcta de V2 todavía activa | Título de V3, pero con la respuesta correcta de V2 todavía activa |

### Por qué cambió cada cosa

- **De doble límite a escalera (V1 → V2).** El doble límite exigía asignar al azar cinco versiones del precio inicial y daba un intervalo con solo dos preguntas. La escalera da el intervalo de cada persona en todos los precios y simplifica el campo. La pregunta abierta se retiró porque produce ceros y valores extremos, y con la escalera completa ya no aporta.
- **De $18.000 a $50.000 como primer precio (V2 → V3).** Empezar en $18.000 dejaba sin techo a quien aceptaba el primer precio y convertía ese precio en un ancla cercana a los precios reales. Se agregaron $50.000, $35.000 y $25.000 arriba para que el primer número fuera improbable.
- **E4 retirada (V3).** El plan de análisis no la usaba en ninguna tabla ni prueba.
- **D2 y D3 nuevas (V3).** El escenario de la escalera describe un café filtrado en V60 "de una finca o región identificada". Las preguntas anteriores (café "de origen" y V60) le daban al encuestado parte de la respuesta y contaminaban la medida de conocimiento. Se cambiaron por dos preguntas neutrales: especies y tostión.

### Cuándo se decidió el cambio de escalera

La primera encuesta registrada (3 de noviembre, 13:30) ya empieza en $50.000. Por eso, el formulario tenía la escalera nueva **antes del inicio del campo**. El cambio se decidió entre la revisión del 30 de octubre y el 3 de noviembre, y quedó escrito en el protocolo subido el 4 de noviembre. El formulario se armó con 10 de los 13 precios: no incluyó $4.000, $2.500 ni $1.500.

---

## 2. ¿Se mezclaron versiones en la base?

### Escalera de DAP: no

| Verificación | Resultado |
|---|---|
| Columnas de precios en la exportación | 10, de E1.1 ($50.000) a E1.10 ($6.000); ninguna de $4.000, $2.500 o $1.500 |
| Escaleras aplicadas que empiezan en $50.000 | 85 de 85 (las 4 restantes no llegaron a la escalera) |
| Escaleras que empiezan en $18.000 (V2) | 0 |
| Respuestas después del primer "sí" | 0: todas se detienen en el primer "sí" |
| Columnas de la pregunta abierta (E5) o de E4 | No existen en la exportación |

Todas las DAP se midieron con la misma escalera. La única diferencia con el protocolo es que la escalera aplicada termina en $6.000, así que quien rechaza todo queda con DAP menor a $6.000 (3 casos, censura a la izquierda).

### Reto cafetero (D2 y D3): sí

| Pregunta | Respuestas con la opción de V2 | Válidas afectadas |
|---|---|---|
| D2 (especies) | 12 eligieron "De una finca o región identificada", respuesta correcta de la antigua D2 (café "de origen") | 12 de 81 |
| D3 (tostión) | 13 eligieron "Un método de preparación por filtrado", respuesta correcta de la antigua D3 (V60) | 13 de 81 |
| D2 o D3 | Al menos una de las dos | **23 de 81** |

Estas opciones no responden a las preguntas actuales ("¿cuáles son las dos especies…?", "una tostión clara suele tener…"). Aparecen en todo el campo, del 3 al 9 de noviembre, mezcladas con respuestas de la versión nueva, incluso dentro de la misma encuesta. Hoy el formulario ya no las muestra (Google Drive registra su última modificación el 10 de noviembre, después del campo). Con la exportación no se puede saber qué texto vio cada persona. Tampoco se puede saber a qué versión respondió quien dijo "No sé", porque esa opción existe en las dos.

**D4 y D5 fueron idénticas en todas las versiones** y no tienen respuestas fuera de sus opciones.

---

## 3. Qué se corrigió

| Antes (Entrega 4) | Ahora |
|---|---|
| `conocimiento` = aciertos en D2 a D5 (0 a 4) | `conocimiento` = aciertos en **D4 y D5** (0 a 2), las dos preguntas iguales para todos |
| Grupos 0–1, 2–3 y 4 aciertos | Grupos 0, 1 y 2 aciertos |
| Sin marca de versión | `flag_d2_version_anterior` y `flag_d3_version_anterior` |
| — | `conocimiento_4items`: D2 a D5 solo para las 58 válidas sin respuestas de V2; se usa como sensibilidad |

El cambio está en `Scripts/01_limpieza.R` (sección de conocimiento).

**Otra corrección en la misma revisión.** `prima_min_veces_tinto` se calculaba como `dap_L ÷ tinto`, que no es la prima sino la DAP en veces el tinto. Ahora es `(dap_L − tinto) ÷ tinto`, como pide el plan de análisis (mediana: 3 tintos), y la DAP en veces el tinto quedó aparte en `dap_veces_tinto` (mediana: 4 tintos).

Fuera de estas variables, nada cambió en la base: se comparó columna por columna con la versión de la Entrega 4.

**Efecto en los resultados.** Con la medida anterior, el conocimiento parecía separar con claridad la DAP: a $12.000 compraría el 59 % del grupo con 0–1 aciertos y el 100 % del grupo con 4 (χ², p = 0,04). Con la medida corregida, la diferencia se reduce y deja de ser significativa: 68 % (0 aciertos), 66 % (1 acierto) y 89 % (2 aciertos), con p = 0,18. En la sensibilidad con las cuatro preguntas, que solo usa las 58 válidas sin respuestas de la versión anterior, el gradiente se mantiene (52 %, 76 % y 100 %; p = 0,03), pero el grupo de 4 aciertos tiene solo 8 personas y una casilla esperada queda por debajo de 5. **Conclusión: hay indicios de que quien sabe más paga más, pero no son robustos. La medida comparable para toda la muestra no muestra una diferencia clara.**

---

## 4. Cobertura: plan frente a lo ejecutado

La tabla completa, tienda por tienda, está en `Datos/limpios/cobertura_por_tienda.csv` y la genera el script de limpieza.

| Concepto | Plan | Ejecutado |
|---|---|---|
| Cafeterías principales | 16 (T01–T08 y T14–T21) | 16 de 16 con encuestas válidas |
| Reservas | 11 | 4 visitadas (T09, T22, T24, T25); T24 sin encuestas válidas (1 no elegible y 1 duplicada) |
| Adicionales | 0 | 1, Diosa (T28), fuera de la ruta |
| Cafeterías con registros | — | 21 |
| Cafeterías con encuestas válidas | — | **20** (4,05 válidas por cafetería) |
| Encuestas | 160 (10 por principal) | 89 registradas, **81 válidas** (50,6 %) |
| Fechas | 2 al 6 nov, dos jornadas | Campo el 3, 4 y 8 nov; marcas temporales hasta el 9 nov (registros posteriores y 3 encuestas por QR) |

**Ajustes frente al informe de la Entrega 4.** Ese informe dice "21 cafeterías" y "3,9 encuestas válidas por cafetería" (81 ÷ 21). Las 81 válidas están en **20** cafeterías: T24 se visitó, pero sus dos registros se excluyeron. Por eso el promedio es 4,05.

**Encuestas con fecha del 9 de noviembre (30).** Ese día no hubo salida de campo.

- **27** son visitas del 8 de noviembre que se registraron en Google Forms al día siguiente.
- **3**, de Diosa (T28), las diligenciaron clientes con el código QR que el equipo dejó en la cafetería, con apoyo del mesero y sin un integrante presente. Es una desviación del protocolo, que preveía encuestas aplicadas por el equipo. En Z1 aparece quien registró la encuesta, no quien la aplicó. Se conservan en la muestra con la variable `modalidad`. Si se excluyen (n = 78), a $12.000 compraría el 73 % (72 % con las 81) y la mitad sigue dejando de comprar entre $14.000 y $16.000.

La columna `autodiligenciadas_qr` de `cobertura_por_tienda.csv` registra estos 3 casos.

**Sobre la meta de 160.** La meta suponía 10 encuestas por cafetería en una jornada. La tasa real fue de 0 a 10 por tienda (mediana 4). El informe de campo menciona, entre otras dificultades, la de abordar a clientes que estaban comiendo. El análisis trabaja con 81 válidas y reporta siempre el n de cada grupo.
