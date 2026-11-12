# =============================================================================
# 01_limpieza.R
# ¿Quién paga la diferencia? DAP por café de especialidad en Chapinero
# Haciendo Economía 2026-2 · Universidad del Rosario · Prof. Paul Rodríguez L.
#
# Qué hace:
#   1. Lee la exportación cruda de Google Forms (Datos/crudos/), SIN modificarla.
#   2. Une la base cruda con la hoja de tiendas (coordenadas geográficas)
#      -> Datos/crudos/base_cruda_con_coordenadas.csv  (entrega 4, punto ii)
#   3. Renombra las columnas con los nombres cortos del diccionario.
#   4. Crea id_encuesta (tienda-iniciales-consecutivo del día).
#   5. Limpia montos (B2, B3, B5): 0 -> vacío; valores < 100 se leen en miles.
#   6. Armoniza categorías (rangos de ingreso duplicados).
#   7. Calcula las variables derivadas del protocolo: dap_L, dap_U, dap_tipo,
#      prima_min, conocimiento (+ banderas de calidad). El conocimiento se
#      corrigió tras la Entrega 4: D2 y D3 mezclan versiones, así que la medida
#      principal usa D4 y D5 (iguales para todos) y se marcan las respuestas
#      de la versión anterior.
#   8. Define la muestra analítica (valida = 1), el flujo de casos y la
#      cobertura por tienda (plan frente a lo ejecutado).
#   9. Exporta la base limpia, el flujo de casos y un registro de limpieza.
#
# Solo usa R base (no requiere instalar paquetes).
# Requisito: R >= 4.0. Los archivos se leen y escriben en UTF-8.
# Cómo correrlo: abrir el .Rproj o fijar el directorio de trabajo en la raíz
# del repositorio y ejecutar  source("Scripts/01_limpieza.R")
# o desde la terminal:        Rscript Scripts/01_limpieza.R
# =============================================================================

rm(list = ls())

# Asegurar lectura UTF-8 (tildes y "ñ") también fuera de RStudio/Windows
if (!isTRUE(l10n_info()[["UTF-8"]]) && .Platform$OS.type != "windows") {
  invisible(Sys.setlocale("LC_CTYPE", "C.UTF-8"))
}

# --- 0. Rutas (el script se ubica solo) --------------------------------------
ubicar_raiz <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  f <- sub("^--file=", "", args[grep("^--file=", args)])
  if (length(f) == 1) return(normalizePath(file.path(dirname(f), "..")))
  if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
    p <- rstudioapi::getSourceEditorContext()$path
    if (nzchar(p)) return(normalizePath(file.path(dirname(p), "..")))
  }
  getwd()
}
RAIZ <- ubicar_raiz()
setwd(RAIZ)
stopifnot(file.exists("Datos/crudos/base_cruda_formulario.csv"),
          file.exists("Datos/hoja_tiendas.csv"))
dir.create("Datos/limpios", showWarnings = FALSE)

# --- 1. Lectura ---------------------------------------------------------------
crudo   <- read.csv("Datos/crudos/base_cruda_formulario.csv", check.names = FALSE,
                    na.strings = c("", "NA"), fileEncoding = "UTF-8", stringsAsFactors = FALSE)
tiendas <- read.csv("Datos/hoja_tiendas.csv", check.names = FALSE,
                    na.strings = c("", "NA"), fileEncoding = "UTF-8", stringsAsFactors = FALSE)
stopifnot(nrow(crudo) == 89, ncol(crudo) == 43)

registro <- character(0)
anotar <- function(...) { msg <- paste0(...); registro <<- c(registro, msg); message(msg) }
anotar("Filas en la exportación cruda: ", nrow(crudo))

# --- 2. Base cruda + coordenadas (entrega 4, ii) -----------------------------
codigo_tienda <- sub("^(T[0-9]+).*$", "\\1", crudo[["Z2. Cafetería"]])
stopifnot(all(grepl("^T[0-9]{2}$", codigo_tienda)),
          all(codigo_tienda %in% tiendas[["código"]]))   # toda encuesta tiene tienda con coordenadas
geo <- tiendas[match(codigo_tienda, tiendas[["código"]]),
               c("código", "dirección", "latitud", "longitud", "zona", "rol")]
names(geo) <- c("tienda_codigo", "tienda_direccion", "latitud", "longitud", "tienda_zona", "tienda_rol")
cruda_geo <- cbind(crudo, geo)
write.csv(cruda_geo, "Datos/crudos/base_cruda_con_coordenadas.csv", row.names = FALSE, fileEncoding = "UTF-8")
stopifnot(!anyNA(cruda_geo$latitud), !anyNA(cruda_geo$longitud))

# --- 3. Nombres cortos (Diccionario de variables) ------------------------------
# El formulario aplicado tuvo 10 peldaños (E1.1 a E1.10, de $50.000 a $6.000);
# los peldaños $4.000, $2.500 y $1.500 del protocolo no se incluyeron en Forms.
nuevos <- c("marca_temporal", "z1_encuestador", "z2_tienda_texto", "z3_franja",
            "a1_consiente", "a2_mayor18", "a3_compro", "a4_ya_respondio",
            "b1_bebida", "c1_frec_especialidad", "c2_frec_tienda", "c3_lugar_habitual", "c4_motivo",
            "d1_autoeval", "d2_especies", "d3_tostion", "d4_proceso", "d5_puntaje85",
            "e1_01_50000", "e1_02_35000", "e1_03_25000", "e1_04_18000", "e1_05_16000",
            "e1_06_14000", "e1_07_12000", "e1_08_10000", "e1_09_8000", "e1_10_6000",
            "e3_razon", "b2_precio_pagado", "b3_gasto_total", "b4_incluye_otros", "b5_precio_tinto",
            "f1_atributo1", "f2_atributo2", "g1_edad", "g2_educacion", "g3_ocupacion",
            "g4_ingreso", "g5_estrato", "z6_atencion", "z7_escucho", "z8_interrupcion")
stopifnot(length(nuevos) == ncol(crudo),
          startsWith(names(crudo)[19], "E1.1 "), startsWith(names(crudo)[28], "E1.10"),
          startsWith(names(crudo)[30], "B2."), startsWith(names(crudo)[43], "Z8."))
d <- crudo
names(d) <- nuevos

# Texto: quitar espacios sobrantes
for (v in names(d)) if (is.character(d[[v]])) d[[v]] <- trimws(d[[v]])

d$marca_temporal <- as.POSIXct(d$marca_temporal, format = "%d/%m/%Y %H:%M:%S", tz = "America/Bogota")
stopifnot(!anyNA(d$marca_temporal))
d$fecha <- as.Date(d$marca_temporal, tz = "America/Bogota")

d$z2_tienda   <- codigo_tienda
d$tienda_nombre <- trimws(sub("^T[0-9]+\\s*·\\s*", "", d$z2_tienda_texto))
d$latitud     <- geo$latitud
d$longitud    <- geo$longitud
d$tienda_zona <- geo$tienda_zona
d$tienda_rol  <- geo$tienda_rol

# --- 4. id_encuesta -----------------------------------------------------------
# Formato: tienda-iniciales-consecutivo. El protocolo proponía el consecutivo "del día",
# pero hubo tiendas visitadas en dos fechas por el mismo encuestador, lo que generaba
# identificadores repetidos. Por eso el consecutivo se cuenta por encuestador dentro de
# cada tienda, en orden de la marca temporal (sigue siendo único y legible).
iniciales <- c("Santiago Gómez" = "SG", "Camilo Ospina" = "CO",
               "David Pascagaza" = "DP", "Emily Rodríguez" = "ER")
stopifnot(all(d$z1_encuestador %in% names(iniciales)))
d <- d[order(d$marca_temporal), ]
d$consec <- ave(seq_len(nrow(d)), d$z1_encuestador, d$z2_tienda, FUN = seq_along)
d$id_encuesta <- sprintf("%s-%s-%02d", d$z2_tienda, iniciales[d$z1_encuestador], d$consec)
stopifnot(!anyDuplicated(d$id_encuesta))
d$registro_ficticio <- "No"

# --- 5. Montos ----------------------------------------------------------------
# Protocolo: si no recuerda, el campo queda vacío; nunca 0. Un 0 se trata como faltante.
# Valores < 100 se interpretan como miles digitados sin ceros (p. ej., 12 -> 12.000;
# 2,5 -> 2.500). Se marca cada corrección en flag_monto_corregido.
limpiar_monto <- function(x, var) {
  x <- suppressWarnings(as.numeric(x))
  n0 <- sum(x == 0, na.rm = TRUE); nk <- sum(x > 0 & x < 100, na.rm = TRUE)
  anotar(sprintf("%s: %d ceros -> vacío; %d valores < 100 multiplicados por 1.000", var, n0, nk))
  corr <- !is.na(x) & (x == 0 | x < 100)
  x[!is.na(x) & x == 0] <- NA
  x[!is.na(x) & x < 100] <- x[!is.na(x) & x < 100] * 1000
  list(x = x, corr = corr)
}
d$flag_monto_corregido <- 0L
for (v in c("b2_precio_pagado", "b3_gasto_total", "b5_precio_tinto")) {
  r <- limpiar_monto(d[[v]], v); d[[v]] <- r$x
  d$flag_monto_corregido <- d$flag_monto_corregido | r$corr
}
d$flag_monto_corregido <- as.integer(d$flag_monto_corregido)
# Valores atípicos que se conservan pero se marcan para revisión
d$flag_b3_atipico    <- as.integer(!is.na(d$b3_gasto_total) & d$b3_gasto_total < 1000)     # p. ej. 800
d$flag_tinto_atipico <- as.integer(!is.na(d$b5_precio_tinto) & d$b5_precio_tinto > 6000)  # tinto > $6.000
d$flag_b3_menor_b2   <- as.integer(!is.na(d$b2_precio_pagado) & !is.na(d$b3_gasto_total) &
                                   d$b3_gasto_total < d$b2_precio_pagado)
anotar("Montos atípicos marcados (no se borran): B3 < $1.000 = ", sum(d$flag_b3_atipico),
       "; tinto > $6.000 = ", sum(d$flag_tinto_atipico), "; B3 < B2 = ", sum(d$flag_b3_menor_b2))

# --- 6. Categorías ------------------------------------------------------------
# El formulario tuvo dos etiquetas para el rango más bajo de ingreso.
d$g4_ingreso[d$g4_ingreso %in% c("Hasta $1,75 millones", "Menos de $1,75 millones")] <- "Menos de $1,75 millones"
orden_ingreso <- c("Menos de $1,75 millones", "De $1,75 a $3,5 millones", "De $3,5 a $7 millones",
                   "De $7 a $10,5 millones", "De $10,5 a $17,5 millones", "Más de $17,5 millones",
                   "No sabe", "Prefiere no responder")
stopifnot(all(na.omit(d$g4_ingreso) %in% orden_ingreso))

# --- 7. Variables derivadas ----------------------------------------------------
precios <- c(50000, 35000, 25000, 18000, 16000, 14000, 12000, 10000, 8000, 6000)
E <- sprintf("e1_%02d_%d", 1:10, precios)
stopifnot(all(E %in% names(d)))
validos_E <- c("Sí", "No", "No está seguro", "No responde")
stopifnot(all(unlist(d[E])[!is.na(unlist(d[E]))] %in% validos_E))

d$dap_L <- NA_real_; d$dap_U <- NA_real_; d$dap_tipo <- NA_character_
d$flag_no_seguro <- 0L; d$flag_escalera_incompleta <- 0L
for (i in seq_len(nrow(d))) {
  r <- unlist(d[i, E])
  if (all(is.na(r))) { d$dap_tipo[i] <- "no_aplicada"; next }
  if (any(r == "No está seguro", na.rm = TRUE)) d$flag_no_seguro[i] <- 1L    # se trata como "No"
  k_si <- which(r == "Sí")[1]; k_nr <- which(r == "No responde")[1]
  k_fin <- min(c(k_si, k_nr, 99), na.rm = TRUE)
  # Coherencia: antes del primer Sí / No responde no puede haber huecos, y después todo vacío
  hasta <- if (k_fin == 99) length(r) else k_fin
  if (anyNA(r[seq_len(hasta)])) { d$dap_tipo[i] <- "faltante"; d$flag_escalera_incompleta[i] <- 1L; next }
  if (k_fin < 99 && k_fin < length(r)) stopifnot(all(is.na(r[(k_fin + 1):length(r)])))
  if (!is.na(k_si) && k_si == k_fin) {                       # primer "Sí"
    d$dap_L[i] <- precios[k_si]
    if (k_si == 1) { d$dap_tipo[i] <- "censura_derecha" } else {
      d$dap_U[i] <- precios[k_si - 1]; d$dap_tipo[i] <- "intervalo" }
  } else if (!is.na(k_nr) && k_nr == k_fin) {                # "No responde" corta la escalera
    d$dap_tipo[i] <- "faltante"
    if (k_nr > 1) d$dap_U[i] <- precios[k_nr - 1]
  } else {                                                   # rechazó los 10 precios
    d$dap_U[i] <- min(precios)
    d$dap_tipo[i] <- ifelse(grepl("protesta", d$e3_razon[i], ignore.case = TRUE),
                            "protesta", "censura_izquierda")
  }
}
stopifnot(!anyNA(d$dap_tipo),
          all(is.na(d$dap_L) | is.na(d$dap_U) | d$dap_L < d$dap_U))

# Prima mínima frente al tinto (límite inferior de la DAP menos el tinto)
d$prima_min <- d$dap_L - d$b5_precio_tinto
# Corrección (Entrega 5): antes esta variable era dap_L / tinto, que no es la prima.
# Ahora la prima en veces el tinto es (dap_L - tinto) / tinto, como pide el plan,
# y la DAP en veces el tinto queda aparte, en dap_veces_tinto.
d$prima_min_veces_tinto <- round(d$prima_min / d$b5_precio_tinto, 2)
d$dap_veces_tinto <- round(d$dap_L / d$b5_precio_tinto, 2)
stopifnot(isTRUE(all.equal(d$dap_veces_tinto - d$prima_min_veces_tinto,
                           ifelse(is.na(d$prima_min), NA, 1), tolerance = 0.02)))

# Conocimiento (corregido tras la retroalimentación de la Entrega 4)
# D2 y D3 mezclan versiones: durante el campo el formulario conservó la respuesta
# correcta de las preguntas anteriores (V2 del protocolo: D2 café "de origen",
# D3 V60). Quien eligió esas opciones no respondió la pregunta actual, y quien
# respondió "No sé" pudo ver cualquiera de las dos versiones. Ver
# Documentacion/Registro de versiones del instrumento.md
OPCION_V2_D2 <- "De una finca o región identificada"
OPCION_V2_D3 <- "Un método de preparación por filtrado"
d$flag_d2_version_anterior <- as.integer(!is.na(d$d2_especies) & d$d2_especies == OPCION_V2_D2)
d$flag_d3_version_anterior <- as.integer(!is.na(d$d3_tostion) & d$d3_tostion == OPCION_V2_D3)
anotar("Reto cafetero: respuestas de la versión anterior en D2 = ", sum(d$flag_d2_version_anterior),
       "; en D3 = ", sum(d$flag_d3_version_anterior))

acierto <- function(x, correcta) ifelse(is.na(x), NA, x == correcta)
a2 <- acierto(d$d2_especies,  "Arábica y robusta")
a3 <- acierto(d$d3_tostion,   "Más acidez y notas frutales")
a4 <- acierto(d$d4_proceso,   "Cómo se procesó el grano después de la cosecha")
a5 <- acierto(d$d5_puntaje85, "Su calificación de calidad en taza, dada por catadores")

# Medida principal: aciertos en D4 y D5 (0 a 2), las dos preguntas que fueron
# idénticas para todos los encuestados en todas las versiones. "No sé" = no acierto.
d$conocimiento <- ifelse(is.na(a4) & is.na(a5), NA, rowSums(cbind(a4, a5), na.rm = TRUE))
stopifnot(all(na.omit(d$conocimiento) %in% 0:2))

# Sensibilidad: aciertos de D2 a D5 (0 a 4), solo para quien no tiene ninguna
# respuesta de la versión anterior en D2 o D3; NA para el resto.
version_ok <- d$flag_d2_version_anterior == 0 & d$flag_d3_version_anterior == 0
d$conocimiento_4items <- ifelse(version_ok & !(is.na(a2) & is.na(a3) & is.na(a4) & is.na(a5)),
                                rowSums(cbind(a2, a3, a4, a5), na.rm = TRUE), NA)
stopifnot(all(na.omit(d$conocimiento_4items) %in% 0:4),
          all(is.na(d$conocimiento_4items[!version_ok])))

# Grupos definidos en el plan de análisis
d$grupo_estrato <- cut(as.numeric(d$g5_estrato), c(-Inf, 3, 4, Inf), labels = c("3 o menos", "4", "5 o más"))
d$grupo_ingreso <- ifelse(d$g4_ingreso %in% orden_ingreso[1:3], "Hasta 4 SMMLV",
                   ifelse(d$g4_ingreso %in% orden_ingreso[4:6], "Más de 4 SMMLV", NA))
d$grupo_educacion <- ifelse(d$g2_educacion %in% c("Bachillerato o menos", "Técnico o tecnológico", "Pregrado en curso"), "Sin pregrado",
                     ifelse(d$g2_educacion == "Pregrado completo", "Pregrado",
                     ifelse(d$g2_educacion == "Posgrado", "Posgrado", NA)))
# Conocimiento: los grupos 0-1 / 2-3 / 4 del plan suponían 4 preguntas; con la medida
# corregida (D4 y D5) los grupos son 0, 1 y 2 aciertos.
d$grupo_conocimiento <- factor(d$conocimiento, levels = 0:2,
                               labels = c("0 aciertos", "1 acierto", "2 aciertos"))
d$grupo_frecuencia <- ifelse(d$c1_frec_especialidad %in% c("Menos de una vez al mes", "1 a 3 veces al mes"), "Menos de semanal",
                      ifelse(is.na(d$c1_frec_especialidad), NA, "Semanal o más"))

# --- 8. Muestra analítica y flujo de casos --------------------------------------
d$motivo_exclusion <- NA_character_
d$motivo_exclusion[d$a1_consiente != "Sí" | d$a2_mayor18 != "Sí"] <- "No consiente o menor de edad"
d$motivo_exclusion[is.na(d$motivo_exclusion) & d$a3_compro == "No"] <- "No compró bebida (no elegible)"
d$motivo_exclusion[is.na(d$motivo_exclusion) & !is.na(d$a4_ya_respondio) & d$a4_ya_respondio == "Sí"] <- "Ya había respondido (duplicado)"
d$motivo_exclusion[is.na(d$motivo_exclusion) & d$dap_tipo == "no_aplicada"] <- "Sin escalera de DAP"
d$motivo_exclusion[is.na(d$motivo_exclusion) & d$dap_tipo == "faltante"] <- "Escalera incompleta"
d$motivo_exclusion[is.na(d$motivo_exclusion) & d$dap_tipo == "protesta"] <- "Respuesta de protesta (E3)"
d$valida <- as.integer(is.na(d$motivo_exclusion))

flujo <- data.frame(
  concepto = c("Registros en el formulario", "No compró bebida (no elegible)",
               "Ya había respondido (duplicado)", "Sin escalera de DAP", "Escalera incompleta",
               "Respuesta de protesta (E3)", "Observaciones finales válidas"),
  n = c(nrow(d),
        sum(d$motivo_exclusion == "No compró bebida (no elegible)", na.rm = TRUE),
        sum(d$motivo_exclusion == "Ya había respondido (duplicado)", na.rm = TRUE),
        sum(d$motivo_exclusion == "Sin escalera de DAP", na.rm = TRUE),
        sum(d$motivo_exclusion == "Escalera incompleta", na.rm = TRUE),
        sum(d$motivo_exclusion == "Respuesta de protesta (E3)", na.rm = TRUE),
        sum(d$valida)))
stopifnot(sum(flujo$n[2:6]) + flujo$n[7] == flujo$n[1])
write.csv(flujo, "Datos/limpios/flujo_casos.csv", row.names = FALSE, fileEncoding = "UTF-8")
anotar("Flujo de casos: ", paste(flujo$concepto, flujo$n, sep = " = ", collapse = " | "))

# Resumen por tienda (encuestas registradas y válidas)
por_tienda <- aggregate(cbind(registradas = 1, validas = d$valida) ~ z2_tienda + tienda_nombre + latitud + longitud,
                        data = d, FUN = sum)
write.csv(por_tienda[order(por_tienda$z2_tienda), ], "Datos/limpios/resumen_por_tienda.csv",
          row.names = FALSE, fileEncoding = "UTF-8")

# Cobertura: plan de ruta frente a lo ejecutado, para las 28 tiendas de la hoja.
# Incluye las tiendas sin encuestas, el rol, la meta y las fechas en que se
# registraron las encuestas en Google Forms (que pueden ser posteriores a la visita).
fechas_tienda <- tapply(format(d$fecha), d$z2_tienda, function(x) paste(sort(unique(x)), collapse = "; "))
cobertura <- data.frame(codigo = tiendas[["código"]], tienda = tiendas[["tienda (plan de ruta)"]],
                        rol = tiendas[["rol"]], dia_plan = tiendas[["día"]], zona = tiendas[["zona"]],
                        meta = tiendas[["meta"]], stringsAsFactors = FALSE)
cobertura$registradas <- as.integer(table(factor(d$z2_tienda, levels = cobertura$codigo)))
cobertura$validas <- as.integer(tapply(d$valida, factor(d$z2_tienda, levels = cobertura$codigo), sum))
cobertura$validas[is.na(cobertura$validas)] <- 0L
cobertura$fechas_registro_forms <- unname(fechas_tienda[cobertura$codigo])
cobertura$estado <- ifelse(cobertura$validas > 0, "Con encuestas válidas",
                    ifelse(cobertura$registradas > 0, "Visitada, sin encuestas válidas", "No visitada"))
stopifnot(sum(cobertura$registradas) == nrow(d), sum(cobertura$validas) == sum(d$valida),
          all(cobertura$registradas == tiendas[["logradas"]]))
write.csv(cobertura, "Datos/limpios/cobertura_por_tienda.csv", row.names = FALSE,
          fileEncoding = "UTF-8", na = "")
anotar("Cobertura: ", sum(cobertura$registradas > 0), " cafeterías con registros, ",
       sum(cobertura$validas > 0), " con encuestas válidas; principales cubiertas = ",
       sum(cobertura$rol == "Principal" & cobertura$validas > 0), " de ", sum(cobertura$rol == "Principal"))

# --- 9. Exportar ----------------------------------------------------------------
orden <- c("id_encuesta", "registro_ficticio", "marca_temporal", "fecha", "z1_encuestador",
           "z2_tienda", "tienda_nombre", "tienda_zona", "tienda_rol", "latitud", "longitud", "z3_franja",
           "a1_consiente", "a2_mayor18", "a3_compro", "a4_ya_respondio", "b1_bebida",
           "c1_frec_especialidad", "c2_frec_tienda", "c3_lugar_habitual", "c4_motivo",
           "d1_autoeval", "d2_especies", "d3_tostion", "d4_proceso", "d5_puntaje85", E, "e3_razon",
           "b2_precio_pagado", "b3_gasto_total", "b4_incluye_otros", "b5_precio_tinto",
           "f1_atributo1", "f2_atributo2", "g1_edad", "g2_educacion", "g3_ocupacion",
           "g4_ingreso", "g5_estrato", "z6_atencion", "z7_escucho", "z8_interrupcion",
           "dap_L", "dap_U", "dap_tipo", "prima_min", "prima_min_veces_tinto", "dap_veces_tinto",
           "conocimiento",
           "conocimiento_4items",
           "grupo_estrato", "grupo_ingreso", "grupo_educacion", "grupo_conocimiento", "grupo_frecuencia",
           "flag_d2_version_anterior", "flag_d3_version_anterior",
           "flag_no_seguro", "flag_escalera_incompleta", "flag_monto_corregido",
           "flag_b3_atipico", "flag_tinto_atipico", "flag_b3_menor_b2", "valida", "motivo_exclusion")
stopifnot(all(orden %in% names(d)))
limpia <- d[, orden]
limpia$marca_temporal <- format(limpia$marca_temporal, "%Y-%m-%d %H:%M:%S")
write.csv(limpia, "Datos/limpios/base_limpia.csv", row.names = FALSE, fileEncoding = "UTF-8", na = "")
write.csv(limpia[limpia$valida == 1, ], "Datos/limpios/base_analisis.csv", row.names = FALSE,
          fileEncoding = "UTF-8", na = "")

anotar("Tipos de DAP (todas las filas): ", paste(names(table(d$dap_tipo)), table(d$dap_tipo), sep = " = ", collapse = "; "))
anotar("Fechas con encuestas: ", paste(names(table(d$fecha)), table(d$fecha), sep = " = ", collapse = "; "))
anotar("Base limpia: ", nrow(limpia), " filas x ", ncol(limpia), " columnas; válidas = ", sum(limpia$valida))
writeLines(c(paste("Registro de limpieza -", format(Sys.time(), "%Y-%m-%d %H:%M")), registro),
           "Datos/limpios/registro_limpieza.txt", useBytes = TRUE)
