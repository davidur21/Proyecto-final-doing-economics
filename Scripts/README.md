# **SCRIPTS**

| Script | Qué hace | Entradas | Salidas |
|---|---|---|---|
| `01_limpieza.R` | Une los datos raw con las coordenadas, renombra variables, crea `id_encuesta`, corrige montos, calcula `dap_L`, `dap_U`, `dap_tipo`, `prima_min` y `conocimiento`, define la muestra válida y el flujo de casos | `Datos/crudos/base_cruda_formulario.csv`, `Datos/hoja_tiendas.csv` | `Datos/crudos/base_cruda_con_coordenadas.csv`, `Datos/limpios/*` |

Solo usa R base. Se ubica solo (funciona con `source()` en RStudio o con `Rscript`), y se detiene con `stopifnot()` si algo no cuadra (filas, códigos de tienda, identificadores únicos, coherencia de la escalera, límites de la DAP).
