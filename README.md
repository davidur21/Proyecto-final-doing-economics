# Proyecto-final-doing-economics
# ☕ ¿Quién paga la diferencia?
### Disposición a pagar por café de especialidad en Chapinero, Bogotá

![Universidad del Rosario](https://img.shields.io/badge/Universidad%20del%20Rosario-Haciendo%20Econom%C3%ADa%202026--2-8B1E2D)
![Eje](https://img.shields.io/badge/Eje-Demanda%20y%20comportamiento%20del%20consumidor-1F4E5F)
![Estado](https://img.shields.io/badge/Estado-Datos%20recolectados-5A6B70)

**Profesor:** Paul Rodríguez L.
**Estudiantes:** Santiago Gómez, Camilo Ospina, Emily Rodríguez y David Pascagaza

---

## 📌 Sobre el proyecto

En Bogotá, el café está en todas partes: lo vende un tintero en la esquina, una panadería, una cadena o una cafetería de especialidad. Un mismo consumidor puede pagar por un tinto en la calle una fracción de lo que cuesta un filtrado de origen en una barra de especialidad. **¿Quién está dispuesto a pagar esa diferencia y por qué?**

La prensa económica reporta que en Colombia el sabor desplazó al precio como principal criterio para elegir café (Jaimes, 2026), pero ese cambio está **descrito, no cuantificado**. Este proyecto lo lleva a la cafetería de especialidad, donde la prima se paga en la práctica.

## ❓ Pregunta de investigación

> ¿Cómo varía la disposición a pagar por una bebida de especialidad y la prima que esta implica frente al tinto tradicional según el nivel socioeconómico, el conocimiento del café y los hábitos de consumo de los clientes de cafeterías de especialidad en Chapinero, Bogotá?

## 🎯 Objetivos específicos

1. Establecer cómo se distribuye la disposición a pagar (DAP) por una bebida de referencia y qué prima representa sobre un tinto tradicional.
2. Caracterizar a los clientes según su nivel socioeconómico, su conocimiento del café y sus hábitos de consumo.
3. Comparar la DAP y la prima entre esos grupos.
4. Describir qué atributos (sabor, origen, método, precio, ambiente, servicio) priorizan los clientes con mayor y menor DAP.

## 🧭 Enfoque

| | |
|---|---|
| **Tipo de estudio** | Descriptivo y cuantitativo |
| **Población** | Personas de 18 años o más que compran una bebida en cafeterías de especialidad de Chapinero |
| **Unidad de observación** | Cliente encuestado en una visita |
| **Marco teórico** | Bienes como canasta de características (Lancaster, 1966), DAP y curva de demanda, bienes de experiencia y credibilidad (Nelson, 1970; Darby y Karni, 1973), calidad percibida (Zeithaml, 1988) y adicción racional (Becker y Murphy, 1988) |
| **Revisión de literatura** | Protocolo PRISMA 2020: 86 registros identificados, 32 fuentes incluidas |
| **Instrumento** | Encuesta presencial en Google Forms; DAP con una escalera de 13 precios, de $50.000 a $1.500 |
| **Trabajo de campo** | 3 al 8 de noviembre de 2026 · 21 cafeterías visitadas (16 principales, 4 reservas y 1 adicional) · 89 encuestas registradas, **81 válidas** (meta: 160) |

## 📂 Estructura del repositorio

```
Proyecto-final-doing-economics/
├── Documentacion/   # Entregas, informe final, plan de ruta, protocolo e informe de trabajo de campo
│   └── evidencia_campo/   # Fotos del trabajo de campo
├── Encuesta/        # Enlace y estructura de la encuesta en Google Forms
├── Datos/
│   ├── crudos/      # Datos raw del formulario y datos raw + coordenadas geográficas
│   ├── limpios/     # Base limpia, base de análisis, flujo de casos y registro de limpieza
│   ├── hoja_tiendas.csv, diccionario_variables.csv, base_estructura_fila_ficticia.csv
├── Scripts/
│   └── 01_limpieza.R   # Limpieza y variables derivadas (R base, sin paquetes)
├── Resultados/      # Mapa de cafeterías visitadas
└── README.md
```

## ▶️ Cómo reproducir la limpieza

```r
# Desde la raíz del repositorio (R >= 4.0, sin paquetes adicionales)
source("Scripts/01_limpieza.R")
```

o en la terminal: `Rscript Scripts/01_limpieza.R`. El script lee `Datos/crudos/base_cruda_formulario.csv` y `Datos/hoja_tiendas.csv`, y escribe `Datos/crudos/base_cruda_con_coordenadas.csv` y todo `Datos/limpios/`. Tiene chequeos `stopifnot()` en cada paso.

## 📄 Informe en línea

👉 [Proyecto doing economics (Google Docs)](https://docs.google.com/document/d/1PkB5qy2evG1l__ezohFwlZ4ZUDXRLuW0qEzWvx5aUZw/edit?usp=sharing)

---

<sub>Universidad del Rosario · Haciendo Economía · 2026-2</sub>
