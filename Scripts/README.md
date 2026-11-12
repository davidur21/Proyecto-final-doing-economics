# **SCRIPTS**

| Script | Qué hace | Entradas | Salidas |
|---|---|---|---|
| `01_limpieza.R` | Une los datos raw con las coordenadas, renombra variables, crea `id_encuesta`, corrige montos, calcula `dap_L`, `dap_U`, `dap_tipo`, `prima_min`, la prima en tintos y `conocimiento` (corregido: D4 y D5), define la muestra válida, el flujo de casos y la cobertura por tienda | `Datos/crudos/base_cruda_formulario.csv`, `Datos/hoja_tiendas.csv` | `Datos/crudos/base_cruda_con_coordenadas.csv`, `Datos/limpios/*` |
| `02_visualizaciones.py` | Genera las 6 figuras principales (lenguaje sencillo, para cualquier público) y las 2 del anexo técnico que pide el plan de análisis (curvas por grupo con χ² y distribución de la DAP por intervalo), más las tablas de apoyo | `Datos/limpios/base_analisis.csv` | `Resultados/figuras/*.png` y `*.pdf`, `Resultados/figuras/anexo/`, `Resultados/tablas/*.csv` |

**Orden:** primero `01_limpieza.R`, después `02_visualizaciones.py`.

`01_limpieza.R` solo usa R base. Se ubica solo (funciona con `source()` en RStudio o con `Rscript`), y se detiene con `stopifnot()` si algo no cuadra (filas, códigos de tienda, identificadores únicos, coherencia de la escalera, límites de la DAP, cobertura).

`02_visualizaciones.py` usa pandas, numpy, matplotlib y scipy (`python Scripts/02_visualizaciones.py` desde cualquier carpeta). También se ubica solo y tiene `assert` en los puntos clave: 81 válidas, conocimiento entre 0 y 2, intervalos de DAP coherentes y cruce del 50 % entre $14.000 y $16.000. Ninguna cifra de los títulos está escrita a mano. Por qué se eligió cada gráfica: [`Documentacion/Entrega 5 - Visualizaciones.pdf`](../Documentacion/Entrega%205%20-%20Visualizaciones.pdf).
