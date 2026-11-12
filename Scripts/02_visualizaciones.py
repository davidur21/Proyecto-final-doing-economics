# -*- coding: utf-8 -*-
"""
02_visualizaciones.py
¿Quién paga la diferencia? Disposición a pagar (DAP) por café de especialidad en Chapinero
Haciendo Economía 2026-2 · Universidad del Rosario · Prof. Paul Rodríguez L.

Genera las figuras del proyecto. Hay dos grupos:

  Figuras principales (Resultados/figuras/): pensadas para entenderse a primera vista,
  también por un público que no es de economía (por ejemplo, estudiantes de colegio).
    fig1_quienes_respondieron      ¿Quiénes respondieron?
    fig2_hasta_cuanto_pagarian     Curva de aceptación (resultado principal)
    fig3_cuantos_tintos_vale       La taza de filtrado en número de tintos
    fig4_pagarian_lo_que_pagaron   DAP frente a lo que pagaron hoy (gráfico de 100 cuadros)
    fig5_quien_paga_mas            % que compraría a $12.000, por grupo
    fig6_que_buscan                Atributos según la DAP quede por encima o por debajo de $12.000

  Anexo técnico (Resultados/figuras/anexo/): lo que pide el plan de análisis del protocolo.
    A1_curvas_por_grupo            Curvas de aceptación por grupo, con χ² y la sensibilidad
                                   del conocimiento con cuatro preguntas
    A2_distribucion_dap            Distribución de la DAP por intervalo de la escalera

Entrada : Datos/limpios/base_analisis.csv (la genera Scripts/01_limpieza.R)
Salidas : figuras en PNG (300 dpi) y PDF; tablas de apoyo en Resultados/tablas/

Reglas que sigue el código (plan de análisis, sección 9 del protocolo):
  - La DAP es un intervalo [dap_L, dap_U); nunca se usa el punto medio.
  - Curva de aceptación con la muestra completa en cada precio; IC 95 % = p ± 1,96·√(p(1−p)/n).
  - Precio de referencia para comparar grupos: $12.000.
  - Conocimiento = aciertos en D4 y D5 (corregido tras la Entrega 4; ver
    Documentacion/Registro de versiones del instrumento.md).

Uso:  python Scripts/02_visualizaciones.py      (desde cualquier carpeta)
Requiere: pandas, numpy, matplotlib, scipy
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter, PercentFormatter
from scipy import stats

# ---------------------------------------------------------------------------
# 0. Rutas (el script se ubica solo)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATOS = BASE_DIR / "Datos" / "limpios" / "base_analisis.csv"
FIG_DIR = BASE_DIR / "Resultados" / "figuras"
ANEXO_DIR = FIG_DIR / "anexo"
TAB_DIR = BASE_DIR / "Resultados" / "tablas"
for carpeta in (FIG_DIR, ANEXO_DIR, TAB_DIR):
    carpeta.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Estilo: gris para el contexto, color solo para el mensaje
# ---------------------------------------------------------------------------
# Paleta validada (luminosidad, croma, separación para daltonismo y contraste)
VINO = "#B5363F"      # el hallazgo (color de la Universidad del Rosario)
AZUL = "#0F7FA8"      # el contraste
CARAMELO = "#B07A2A"  # el tinto
TINTA = "#1F2328"
TINTA2 = "#5A6470"
GRIS = "#A7AFB7"
GRIS_CLARO = "#E4E7EA"
FONDO = "#FFFFFF"
RAMPA = {2: ["#D98990", "#8E1E28"], 3: ["#E3A3A8", "#B5363F", "#6A1119"]}  # grupos ordenados

_familias = {f.name for f in font_manager.fontManager.ttflist}
FUENTE = "Inter" if "Inter" in _familias else "DejaVu Sans"

plt.rcParams.update({
    "font.family": FUENTE, "font.size": 12,
    "axes.edgecolor": GRIS, "axes.labelcolor": TINTA2, "axes.labelsize": 12,
    "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.8,
    "axes.titlesize": 13, "axes.titleweight": "semibold", "axes.titlecolor": TINTA,
    "axes.titlelocation": "left",
    "xtick.color": TINTA2, "ytick.color": TINTA2, "xtick.labelsize": 11, "ytick.labelsize": 11,
    "xtick.major.size": 0, "ytick.major.size": 0,
    "grid.color": GRIS_CLARO, "grid.linewidth": 0.8,
    "legend.frameon": False, "legend.fontsize": 11,
    "figure.facecolor": FONDO, "axes.facecolor": FONDO, "savefig.facecolor": FONDO,
    "pdf.fonttype": 42,
    "text.parse_math": False,  # los "$" de los precios no son LaTeX
})

FUENTE_DATOS = ("Fuente: encuesta a clientes de cafeterías de especialidad de Chapinero (Bogotá), "
                "noviembre de 2026. Elaboración propia.")


def pesos(v):
    """12000 -> '$12.000'"""
    return "$" + f"{v:,.0f}".replace(",", ".")


def coma(x, dec=1):
    return f"{x:.{dec}f}".replace(".", ",")


def encabezado(fig, titulo, subtitulo):
    """Título que dice el hallazgo y subtítulo que dice qué se mide (alturas en pulgadas)."""
    alto = fig.get_size_inches()[1]
    fig.text(0.045, 1 - 0.30 / alto, titulo, ha="left", va="top", fontsize=20,
             fontweight="bold", color=TINTA)
    fig.text(0.045, 1 - 0.78 / alto, subtitulo, ha="left", va="top", fontsize=13, color=TINTA2)


def pie(fig, nota=""):
    texto = FUENTE_DATOS if not nota else f"{nota}\n{FUENTE_DATOS}"
    fig.text(0.045, 0.02, texto, ha="left", va="bottom", fontsize=9, color=TINTA2, linespacing=1.45)


def guardar(fig, nombre, carpeta=FIG_DIR):
    for ext in ("png", "pdf"):
        fig.savefig(carpeta / f"{nombre}.{ext}", dpi=300)
    plt.close(fig)
    print(f"  ✓ {carpeta.relative_to(BASE_DIR)}/{nombre}")


# ---------------------------------------------------------------------------
# 2. Datos
# ---------------------------------------------------------------------------
d = pd.read_csv(DATOS)
N = len(d)
assert N == 81, f"Se esperaban 81 observaciones válidas, hay {N}"
assert (d["valida"] == 1).all()
assert d["conocimiento"].dropna().between(0, 2).all(), "conocimiento debe ser D4+D5 (0 a 2)"

ESCALERA = [50000, 35000, 25000, 18000, 16000, 14000, 12000, 10000, 8000, 6000]
P_REF = 12000

# Límites de la DAP: censura a la izquierda -> L = 0; censura a la derecha -> U = infinito
L = d["dap_L"].fillna(0).to_numpy()
U = d["dap_U"].fillna(np.inf).to_numpy()
assert (L < U).all()
assert ((d["dap_tipo"] == "censura_izquierda") == d["dap_L"].isna()).all()
assert ((d["dap_tipo"] == "censura_derecha") == d["dap_U"].isna()).all()

d["nivel_12"] = np.select([L > P_REF, L == P_REF], ["Por encima", "En $12.000"], default="Por debajo")
ORDEN_NIVEL = ["Por debajo", "En $12.000", "Por encima"]


def curva(mask=None):
    """% que acepta cada precio (con la muestra completa del grupo) e IC 95 %."""
    l_ = L if mask is None else L[mask]
    n = len(l_)
    filas = []
    for p in sorted(ESCALERA):
        prop = (l_ >= p).mean()
        ee = np.sqrt(prop * (1 - prop) / n)
        filas.append({"precio": p, "n": n, "acepta": prop,
                      "ic_inf": max(prop - 1.96 * ee, 0), "ic_sup": min(prop + 1.96 * ee, 1)})
    return pd.DataFrame(filas)


def ji2(var):
    """Ji cuadrado grupo × DAP en tres niveles; si una esperada < 5, dos niveles (acepta $12.000 o no)."""
    sub = d[d[var].notna()]
    tab = pd.crosstab(sub[var].astype(str), sub["nivel_12"]).reindex(columns=ORDEN_NIVEL, fill_value=0)
    niveles = 3
    if (stats.contingency.expected_freq(tab.values) < 5).any():
        tab = pd.DataFrame({"no": tab["Por debajo"], "si": tab["En $12.000"] + tab["Por encima"]})
        niveles = 2
    chi2, p, gl, esp = stats.chi2_contingency(tab.values, correction=False)
    return chi2, p, gl, niveles, bool((esp < 5).any())


def p_texto(p):
    return "p < 0,01" if p < 0.01 else f"p = {coma(p, 2)}"


print("Generando figuras…")

# ===========================================================================
# FIGURA 1. ¿Quiénes respondieron?
# ===========================================================================
paneles = [
    ("g1_edad", "Edad", ["18 a 24", "25 a 34", "35 a 44", "45 a 54", "55 o más"],
     {"18 a 24": "18 a 24 años", "25 a 34": "25 a 34", "35 a 44": "35 a 44", "45 a 54": "45 a 54",
      "55 o más": "55 o más"}),
    ("g5_estrato", "Estrato de su vivienda", ["2", "3", "4", "5", "6"],
     {"2": "Estrato 2", "3": "3", "4": "4", "5": "5", "6": "6"}),
    ("c2_frec_tienda", "¿Viene seguido a esa cafetería?",
     ["Es la primera vez", "Menos de una vez al mes", "1 a 3 veces al mes", "1 vez por semana o más"],
     {"Es la primera vez": "Primera vez", "Menos de una vez al mes": "Menos de 1 vez al mes",
      "1 a 3 veces al mes": "1 a 3 veces al mes", "1 vez por semana o más": "Cada semana"}),
    ("b1_bebida", "¿Qué compró?",
     ["Café con leche (capuchino, latte…)", "Café filtrado (V60, Chemex u otro)",
      "Espresso o americano", "Bebida fría de café", "Bebida sin café"],
     {"Café con leche (capuchino, latte…)": "Café con leche", "Café filtrado (V60, Chemex u otro)": "Café filtrado",
      "Espresso o americano": "Espresso o americano", "Bebida fría de café": "Bebida fría de café",
      "Bebida sin café": "Bebida sin café"}),
]
fig, axes = plt.subplots(2, 2, figsize=(13, 8.6))
fig.subplots_adjust(left=0.19, right=0.96, top=0.80, bottom=0.08, wspace=0.75, hspace=0.42)
for ax, (var, titulo, orden, etiq) in zip(axes.flat, paneles):
    serie = d[var].astype(str).str.replace(r"\.0$", "", regex=True)
    pct = serie.value_counts(normalize=True).reindex(orden).fillna(0)
    pos = np.arange(len(orden))[::-1]
    top = pct.idxmax()
    ax.barh(pos, pct.values, color=[VINO if o == top else GRIS for o in orden], height=0.7)
    for y, (o, v) in zip(pos, pct.items()):
        ax.text(v + 0.012, y, f"{v:.0%}", va="center", fontsize=12,
                color=TINTA if o == top else TINTA2, fontweight="bold" if o == top else "normal")
    ax.set_yticks(pos, [etiq[o] for o in orden], fontsize=12)
    ax.set_xlim(0, pct.max() * 1.3)
    ax.xaxis.set_visible(False)
    for s in ("bottom", "left"):
        ax.spines[s].set_visible(False)
    ax.set_title(titulo, pad=10, fontsize=14)
edad_joven = (d["g1_edad"].isin(["18 a 24", "25 a 34"])).mean()
encabezado(fig, f"{edad_joven:.0%} de los clientes tiene menos de 35 años",
           f"Así son las {N} personas que respondieron la encuesta en 20 cafeterías de Chapinero")
pie(fig, "En vino, la respuesta más común de cada pregunta. Porcentajes sobre las 81 encuestas válidas.")
guardar(fig, "fig1_quienes_respondieron")

# ===========================================================================
# FIGURA 2. ¿Hasta cuánto pagarían? (curva de aceptación)
# ===========================================================================
c_tot = curva()
c_tot.round(4).to_csv(TAB_DIR / "curva_aceptacion.csv", index=False)
p_si = c_tot[c_tot.acepta >= 0.5].precio.max()
p_no = c_tot[c_tot.acepta < 0.5].precio.min()
assert (p_si, p_no) == (14000, 16000)
tinto_med = d["b5_precio_tinto"].median()
pagado_med = d["b2_precio_pagado"].median()

fig, ax = plt.subplots(figsize=(13, 7.6))
fig.subplots_adjust(left=0.10, right=0.96, top=0.81, bottom=0.16)
ax.fill_between(c_tot.precio, c_tot.ic_inf, c_tot.ic_sup, color=VINO, alpha=0.12, lw=0)
ax.plot(c_tot.precio, c_tot.acepta, color=VINO, lw=3, zorder=3)
ax.scatter(c_tot.precio, c_tot.acepta, s=60, color=VINO, edgecolor=FONDO, lw=2, zorder=4)
ax.axhline(0.5, color=TINTA2, lw=1, ls=(0, (4, 3)), zorder=1)
ax.text(51500, 0.5, "La mitad", ha="right", va="bottom", fontsize=11, color=TINTA2)

for p, dy in [(6000, 0.05), (12000, 0.055), (14000, 0.05), (16000, -0.03), (25000, 0.05), (50000, 0.05)]:
    v = c_tot.loc[c_tot.precio == p, "acepta"].item()
    ax.text(p + (900 if p == 16000 else 450), v + dy, f"{round(v * 100):.0f} de 100", fontsize=12, color=TINTA, fontweight="bold",
            ha="left" if p < 50000 else "center")
ax.annotate(f"Entre {pesos(p_si)} y {pesos(p_no)}\nse va la mitad de los clientes",
            xy=((p_si + p_no) / 2, 0.5), xytext=(26000, 0.80), fontsize=13, color=VINO,
            fontweight="bold", ha="left", va="center",
            arrowprops=dict(arrowstyle="-|>", color=VINO, lw=1.4, connectionstyle="arc3,rad=0.15"))
for x, col, txt in [(tinto_med, CARAMELO, f"Un tinto\n{pesos(tinto_med)}"),
                    (pagado_med, AZUL, f"Lo que pagaron hoy\n{pesos(pagado_med)}")]:
    ax.axvline(x, color=col, lw=2, ymax=0.9, zorder=2)
    ax.text(x, 1.065, txt, ha="center", va="bottom", fontsize=11.5, color=col, fontweight="bold",
            linespacing=1.15)
ax.set_xlim(0, 52500)
ax.set_ylim(0, 1.18)
ax.set_xticks([0] + sorted(ESCALERA))
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v/1000:.0f}"))
ax.set_xlabel("Precio de una taza de café filtrado (miles de pesos)")
ax.set_ylabel("Clientes que la comprarían (de cada 100)")
ax.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0", "25", "50", "75", "100"])
ax.grid(axis="y")
ax.set_axisbelow(True)
encabezado(fig, f"La mitad de los clientes pagaría hasta {pesos(p_si)} por un café filtrado",
           "Cuántos clientes de cada 100 comprarían una taza de café filtrado a cada precio")
pie(fig, "Se preguntó del precio más alto al más bajo y la pregunta se detuvo en el primer “sí”. La franja clara "
         "es el margen de error (intervalo de confianza al 95 %). n = 81.")
guardar(fig, "fig2_hasta_cuanto_pagarian")

# ===========================================================================
# FIGURA 3. ¿Cuántos tintos vale un filtrado?
# ===========================================================================
veces = d["dap_veces_tinto"].dropna()
n_v = len(veces)
med_v = veces.median()
cortes = [0, 2, 4, 6, np.inf]
etiquetas = ["Menos de\n2 tintos", "De 2 a menos\nde 4 tintos", "De 4 a menos\nde 6 tintos", "6 tintos\no más"]
grupos_v = pd.cut(veces, cortes, labels=etiquetas, right=False).value_counts(sort=False) / n_v
pd.DataFrame({"grupo": [e.replace("\n", " ") for e in etiquetas], "pct": grupos_v.values.round(4),
              "n": (grupos_v.values * n_v).round().astype(int)}).to_csv(TAB_DIR / "tintos_por_filtrado.csv",
                                                                     index=False)
pct_4omas = (veces >= 4).mean()
assert abs(pct_4omas - grupos_v.values[2:].sum()) < 1e-9

fig, ax = plt.subplots(figsize=(13, 7.6))
fig.subplots_adjust(left=0.07, right=0.97, top=0.79, bottom=0.22)
x = np.arange(len(etiquetas))
colores = [GRIS, GRIS, VINO, VINO]
ax.bar(x, grupos_v.values, color=colores, width=0.62)
for xi, v in zip(x, grupos_v.values):
    ax.text(xi, v + 0.012, f"{round(v * 100):.0f} de 100", ha="center", va="bottom", fontsize=14,
            fontweight="bold", color=TINTA)
ax.set_xticks(x, etiquetas, fontsize=13)
ax.set_ylim(0, grupos_v.max() * 1.25)
ax.yaxis.set_visible(False)
ax.spines["left"].set_visible(False)
# Llave sobre las dos barras de "4 o más"
ytop = grupos_v.max() * 1.15
ax.plot([1.7, 1.7, 3.3, 3.3], [ytop - 0.015, ytop, ytop, ytop - 0.015], color=VINO, lw=1.5)
ax.text(2.5, ytop + 0.008, f"{round(pct_4omas * 100):.0f} de 100 pagarían por un filtrado lo de 4 tintos o más",
        ha="center", va="bottom", fontsize=12.5, color=VINO, fontweight="bold")
encabezado(fig, f"Para más de la mitad de los clientes, un café filtrado vale {med_v:.0f} tintos o más",
           "Cuántos tintos de los que suele tomar cada cliente equivalen a lo que pagaría por un filtrado")
pie(fig, f"Se divide el precio más alto que cada cliente aceptó por lo que paga por un tinto en la calle o en una "
         f"panadería (mediana {pesos(tinto_med)}). n = {n_v}: no incluye\na quien no dio el precio del tinto ni "
         "a quien rechazó todos los precios.")
guardar(fig, "fig3_cuantos_tintos_vale")

# ===========================================================================
# FIGURA 4. ¿Pagarían lo que pagaron hoy? (gráfico de 100 cuadros)
# ===========================================================================
B = d["b2_precio_pagado"].to_numpy()
pos_b = np.select([np.isnan(B), L >= B, U <= B], ["sin dato", "mas", "menos"], default="duda")
con_dato = pos_b[pos_b != "sin dato"]
n_b = len(con_dato)
cats = [("mas", VINO, "Pagaría por un filtrado lo mismo o más\nde lo que pagó por su bebida"),
        ("duda", GRIS, "No se puede saber con la escalera"),
        ("menos", AZUL, "Pagaría menos de lo que pagó")]
props = np.array([(con_dato == c).mean() for c, *_ in cats])
cuadros = np.floor(props * 100).astype(int)
for i in np.argsort(-(props * 100 - cuadros))[: 100 - cuadros.sum()]:
    cuadros[i] += 1  # redondeo de mayor residuo: siempre suman 100
assert cuadros.sum() == 100

fig = plt.figure(figsize=(13, 7.4))
ax = fig.add_axes([0.05, 0.12, 0.47, 0.66])
colores_q = np.repeat([c[1] for c in cats], cuadros)
for k in range(100):
    fila, col = divmod(k, 10)
    ax.add_patch(FancyBboxPatch((col + 0.08, 9 - fila + 0.08), 0.84, 0.84,
                                boxstyle="round,pad=0,rounding_size=0.12", color=colores_q[k], lw=0))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect("equal")
ax.axis("off")
axl = fig.add_axes([0.55, 0.12, 0.42, 0.66])
axl.axis("off")
for i, ((c, colr, txt), q) in enumerate(zip(cats, cuadros)):
    y = 0.86 - i * 0.30
    axl.add_patch(FancyBboxPatch((0, y - 0.035), 0.06, 0.07, boxstyle="round,pad=0,rounding_size=0.01",
                                 color=colr, transform=axl.transAxes, lw=0))
    axl.text(0.10, y + 0.01, f"{q} de 100", fontsize=24, fontweight="bold", color=colr if c != "duda" else TINTA2,
             va="bottom", transform=axl.transAxes)
    axl.text(0.10, y - 0.005, txt, fontsize=12.5, color=TINTA, va="top", transform=axl.transAxes,
             linespacing=1.3)
encabezado(fig, f"{cuadros[0]} de cada 100 pagarían por un filtrado lo que pagaron hoy, o más",
           "Cada cuadro es un cliente de cada 100: lo que pagaría por una taza de filtrado frente a lo que pagó por su bebida")
pie(fig, f"n = {n_b}: no incluye a {int((pos_b == 'sin dato').sum())} personas que no recordaron el precio. Entre quienes "
         "compraron justo un filtrado (n = 20), 55 de 100 pagarían\nlo mismo o más y 40 de 100 pagarían menos.")
guardar(fig, "fig4_pagarian_lo_que_pagaron")
# Chequeo del dato de la nota (filtrado)
filt = d["b1_bebida"].str.startswith("Café filtrado").to_numpy() & (pos_b != "sin dato")
assert round((pos_b[filt] == "mas").mean() * 100) == 55 and round((pos_b[filt] == "menos").mean() * 100) == 40

# ===========================================================================
# FIGURA 5. ¿Quién paga más? (% que compraría a $12.000, por grupo)
# ===========================================================================
grupos = [
    ("grupo_estrato", "Estrato", ["3 o menos", "4", "5 o más"],
     {"3 o menos": "Estrato 3 o menos", "4": "Estrato 4", "5 o más": "Estrato 5 o más"}),
    ("grupo_ingreso", "Ingreso del hogar", ["Hasta 4 SMMLV", "Más de 4 SMMLV"],
     {"Hasta 4 SMMLV": "Hasta 4 salarios mínimos", "Más de 4 SMMLV": "Más de 4 salarios mínimos"}),
    ("grupo_conocimiento", "Cuánto sabe de café", ["0 aciertos", "1 acierto", "2 aciertos"],
     {"0 aciertos": "0 de 2 preguntas bien", "1 acierto": "1 de 2 bien", "2 aciertos": "2 de 2 bien"}),
    ("grupo_educacion", "Educación", ["Sin pregrado", "Pregrado", "Posgrado"],
     {"Sin pregrado": "Sin pregrado terminado", "Pregrado": "Pregrado", "Posgrado": "Posgrado"}),
    ("grupo_frecuencia", "Qué tan seguido toma café", ["Menos de semanal", "Semanal o más"],
     {"Menos de semanal": "Menos de una vez a la semana", "Semanal o más": "Cada semana o más"}),
]
filas = []
for var, nombre, orden, _ in grupos:
    chi2, p, gl, niveles, aviso = ji2(var)
    for g in orden:
        m = (d[var].astype(str) == g).to_numpy()
        filas.append({"variable": var, "dimension": nombre, "grupo": g, "n": int(m.sum()),
                      "acepta_12000": round((L[m] >= P_REF).mean(), 4), "ji2": round(chi2, 3), "gl": gl,
                      "p_valor": round(p, 4), "niveles_dap": niveles, "esperada_menor_5": aviso})
comp = pd.DataFrame(filas)

# Sensibilidad del conocimiento: D2 a D5 solo para quien no tiene respuestas de la versión anterior
d["grupo_conoc4"] = pd.cut(d["conocimiento_4items"], [-np.inf, 1, 3, 4], labels=["0-1", "2-3", "4"]).astype(str)
d.loc[d["conocimiento_4items"].isna(), "grupo_conoc4"] = np.nan
chi2, p, gl, niveles, aviso = ji2("grupo_conoc4")
for g in ["0-1", "2-3", "4"]:
    m = (d["grupo_conoc4"] == g).to_numpy()
    comp.loc[len(comp)] = {"variable": "conocimiento_4items (sensibilidad)", "dimension": "Conocimiento, 4 preguntas",
                           "grupo": g, "n": int(m.sum()), "acepta_12000": round((L[m] >= P_REF).mean(), 4),
                           "ji2": round(chi2, 3), "gl": gl, "p_valor": round(p, 4), "niveles_dap": niveles,
                           "esperada_menor_5": aviso}
comp.to_csv(TAB_DIR / "comparaciones_grupos.csv", index=False)

fig, ax = plt.subplots(figsize=(13, 9.6))
fig.subplots_adjust(left=0.30, right=0.90, top=0.84, bottom=0.10)
y = 0
yticks, ylabels = [], []
for var, nombre, orden, etiq in grupos:
    sub = comp[comp.variable == var]
    p = sub.p_valor.iloc[0]
    clara = p < 0.05
    y -= 0.55
    ax.text(-0.005, y, nombre, transform=ax.get_yaxis_transform(), ha="right", va="center",
            fontsize=13, fontweight="bold", color=TINTA)
    ax.text(1.0, y, "Diferencia clara" if clara else "Diferencia pequeña o al azar",
            transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=11,
            color=VINO if clara else TINTA2, fontweight="bold" if clara else "normal")
    y -= 0.2
    for _, r in sub.iterrows():
        y -= 0.8
        col = VINO if clara else GRIS
        ax.barh(y, r.acepta_12000, color=col, height=0.6)
        ax.text(r.acepta_12000 + 0.012, y, f"{round(r.acepta_12000 * 100):.0f}", va="center", fontsize=13,
                fontweight="bold", color=TINTA)
        yticks.append(y)
        ylabels.append(f"{etiq[r.grupo]}  (n = {r.n})")
    y -= 0.75
ax.set_yticks(yticks, ylabels, fontsize=11.5)
ax.set_xlim(0, 1)
ax.set_ylim(y + 0.3, 0.2)
ax.xaxis.set_visible(False)
for s in ("bottom", "left"):
    ax.spines[s].set_visible(False)
ax.axvline(0.5, color=GRIS_CLARO, lw=1, zorder=0)
encabezado(fig, "El estrato y el ingreso marcan la diferencia; saber de café, no tanto",
           "De cada 100 clientes de cada grupo, cuántos comprarían una taza de filtrado a $12.000")
pie(fig, "“Diferencia clara”: prueba ji cuadrado con p < 0,05. Las preguntas de conocimiento son D4 y D5, las únicas "
         "iguales para todos los encuestados (ver el registro de versiones).\nEl ingreso excluye a 12 personas que no lo "
         "reportaron. Son asociaciones, no causas.")
guardar(fig, "fig5_quien_paga_mas")

# ===========================================================================
# FIGURA 6. ¿Qué buscan los que pagarían más?
# ===========================================================================
ATRIB = ["Sabor", "Aroma", "Método de preparación", "Origen del café (finca o región)",
         "Ambiente del lugar", "Atención o servicio", "Precio"]
filas_at = []
for niv in ORDEN_NIVEL:
    sub = d[d["nivel_12"] == niv]
    for a in ATRIB:
        filas_at.append({"nivel": niv, "n": len(sub), "atributo": a,
                         "pct": ((sub["f1_atributo1"] == a) | (sub["f2_atributo2"] == a)).mean()})
at = pd.DataFrame(filas_at)
at.round(4).to_csv(TAB_DIR / "atributos_por_dap.csv", index=False)
piv = at.pivot(index="atributo", columns="nivel", values="pct")
piv["brecha"] = piv["Por encima"] - piv["Por debajo"]
piv = piv.sort_values("brecha")
n_niv = at.groupby("nivel")["n"].first()

fig, ax = plt.subplots(figsize=(13, 7.8))
fig.subplots_adjust(left=0.22, right=0.97, top=0.76, bottom=0.14)
yy = np.arange(len(piv))
nombres = {"Origen del café (finca o región)": "Origen del café", "Método de preparación": "Cómo lo preparan",
           "Ambiente del lugar": "Ambiente del lugar", "Atención o servicio": "Atención"}
for yi, (_, r) in zip(yy, piv.iterrows()):
    a, b = r["Por debajo"], r["Por encima"]
    ax.annotate("", xy=(b, yi), xytext=(a, yi),
                arrowprops=dict(arrowstyle="-", color=GRIS_CLARO, lw=6, shrinkA=0, shrinkB=0), zorder=1)
    ax.scatter([a], [yi], s=170, color=AZUL, edgecolor=FONDO, lw=2, zorder=3)
    ax.scatter([b], [yi], s=170, color=VINO, edgecolor=FONDO, lw=2, zorder=3)
    for val, colr in ((a, AZUL), (b, VINO)):
        lado = 1 if val == max(a, b) else -1
        ax.text(val + lado * 0.022, yi, f"{round(val * 100):.0f}", va="center",
                ha="left" if lado > 0 else "right", fontsize=12, fontweight="bold", color=colr)
ax.set_yticks(yy, [nombres.get(a, a) for a in piv.index], fontsize=13)
ax.set_xlim(0, 0.68)
ax.xaxis.set_visible(False)
for s in ("bottom", "left"):
    ax.spines[s].set_visible(False)
ax.scatter([], [], s=150, color=VINO, label=f"Pagarían más de $12.000  (n = {n_niv['Por encima']})")
ax.scatter([], [], s=150, color=AZUL, label=f"Pagarían menos de $12.000  (n = {n_niv['Por debajo']})")
ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, fontsize=12, handletextpad=0.3,
          columnspacing=1.6)
encabezado(fig, "Los que pagarían más buscan origen y sabor; los demás, ambiente y atención",
           "De cada 100 clientes de cada grupo, cuántos ponen cada aspecto entre los dos más importantes al elegir café")
pie(fig, f"Cada persona eligió dos aspectos, por eso cada grupo suma 200. No se muestran las {n_niv['En $12.000']} "
         "personas cuyo precio máximo fue justo $12.000 (están en la tabla de apoyo).")
guardar(fig, "fig6_que_buscan")

# ===========================================================================
# ANEXO A1. Curvas de aceptación por grupo (plan de análisis)
# ===========================================================================
anexo = [
    ("grupo_estrato", "Estrato", ["3 o menos", "4", "5 o más"]),
    ("grupo_ingreso", "Ingreso del hogar", ["Hasta 4 SMMLV", "Más de 4 SMMLV"]),
    ("grupo_educacion", "Educación", ["Sin pregrado", "Pregrado", "Posgrado"]),
    ("grupo_conocimiento", "Conocimiento: aciertos en D4 y D5 (medida principal)",
     ["0 aciertos", "1 acierto", "2 aciertos"]),
    ("grupo_frecuencia", "Frecuencia en cafeterías de especialidad", ["Menos de semanal", "Semanal o más"]),
    ("grupo_conoc4", "Sensibilidad: aciertos en D2 a D5, sin respuestas de V2", ["0-1", "2-3", "4"]),
]
fig, axes = plt.subplots(2, 3, figsize=(16, 10), sharey=True)
fig.subplots_adjust(left=0.06, right=0.98, top=0.83, bottom=0.155, wspace=0.12, hspace=0.48)
for ax, (var, titulo, orden) in zip(axes.flat, anexo):
    serie = d[var].astype(str)
    ns = []
    for g, colr in zip(orden, RAMPA[len(orden)]):
        m = (serie == g).to_numpy()
        c = curva(m)
        ns.append(int(m.sum()))
        ax.plot(c.precio, c.acepta, color=colr, lw=2.2, marker="o", ms=4.5, markeredgecolor=FONDO,
                label=f"{g} (n = {int(m.sum())})")
    ax.axvline(P_REF, color=TINTA2, lw=0.9, ls=(0, (4, 3)))
    sub = comp[comp.variable == (var if var != "grupo_conoc4" else "conocimiento_4items (sensibilidad)")]
    pv = sub.p_valor.iloc[0]
    ext = f"A $12.000: {sub.acepta_12000.iloc[0]:.0%} vs {sub.acepta_12000.iloc[-1]:.0%} · χ² {p_texto(pv)}"
    if sub.esperada_menor_5.iloc[0] or min(ns) < 10:
        ext += " · ⚠ casilla pequeña"
    ax.set_title(titulo, pad=24, fontsize=12)
    ax.text(0, 1.03, ext, transform=ax.transAxes, fontsize=10, color=VINO if pv < 0.05 else TINTA2,
            fontweight="semibold" if pv < 0.05 else "normal")
    ax.set_xlim(4000, 52000)
    ax.set_xticks([6000, 12000, 18000, 25000, 35000, 50000])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v/1000:.0f}"))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_ylim(0, 1.04)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.legend(loc="upper right", fontsize=9.5)
for ax in axes[1, :]:
    ax.set_xlabel("Precio ofrecido (miles de pesos)")
for ax in axes[:, 0]:
    ax.set_ylabel("Compraría la taza")
encabezado(fig, "Anexo A1. Curvas de aceptación por grupo",
           "Porcentaje que compraría la taza a cada precio · línea punteada: precio de referencia de $12.000 · "
           "más oscuro = nivel más alto")
pie(fig, "χ²: grupo frente a la DAP en tres niveles (debajo, en o encima de $12.000); si una casilla esperada es menor "
         "que 5 se usan dos niveles (acepta $12.000 o no). En vino, p < 0,05.\nLas respuestas de una persona en la "
         "escalera no son independientes. La sensibilidad usa las 58 válidas sin respuestas de la versión anterior "
         "en D2 o D3.")
guardar(fig, "A1_curvas_por_grupo", ANEXO_DIR)

# ===========================================================================
# ANEXO A2. Distribución de la DAP por intervalo (sin punto medio)
# ===========================================================================
def etiqueta_intervalo(l, u):
    if l == 0:
        return f"Menos de\n{pesos(u)}"
    if np.isinf(u):
        return f"{pesos(l)}\no más"
    return f"{pesos(l)}\na {pesos(u)}"


iv = pd.DataFrame({"L": L, "U": U}).value_counts().reset_index(name="n").sort_values("L").reset_index(drop=True)
iv["pct"] = iv["n"] / N
iv["intervalo"] = [etiqueta_intervalo(l, u) for l, u in zip(iv.L, iv.U)]
assert iv["n"].sum() == N
iv.assign(intervalo=iv.intervalo.str.replace("\n", " "), pct=iv.pct.round(4)).to_csv(
    TAB_DIR / "distribucion_dap.csv", index=False)
moda = iv["n"].idxmax()
fig, ax = plt.subplots(figsize=(14, 7.2))
fig.subplots_adjust(left=0.07, right=0.98, top=0.80, bottom=0.21)
xx = np.arange(len(iv))
ax.bar(xx, iv["pct"], color=[VINO if i == moda else GRIS for i in xx], width=0.72)
for xi, v in zip(xx, iv["pct"]):
    ax.text(xi, v + 0.004, f"{v:.0%}", ha="center", va="bottom", fontsize=11,
            color=TINTA if xi == moda else TINTA2, fontweight="bold" if xi == moda else "normal")
ax.set_xticks(xx, iv["intervalo"], fontsize=10)
ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
ax.set_yticks(np.arange(0, iv.pct.max() * 1.2, 0.05))
ax.set_ylim(0, iv["pct"].max() * 1.2)
ax.grid(axis="y")
ax.set_axisbelow(True)
ax.set_ylabel("Clientes")
ax.set_xlabel("Intervalo de la DAP: precio aceptado – precio rechazado inmediatamente superior")
prom_L = d["dap_L"].fillna(0).mean()
encabezado(fig, f"Anexo A2. El intervalo más común es de {pesos(iv.L[moda])} a {pesos(iv.U[moda])} "
                f"({iv.pct[moda]:.0%} de los clientes)",
           f"Distribución de la DAP según el peldaño donde dijo “sí” · promedio de los límites inferiores = "
           f"{pesos(round(prom_L, -2))} (es un mínimo)")
pie(fig, "No se usa el punto medio del intervalo. “Menos de $6.000”: rechazó toda la escalera aplicada, que llegó "
         "hasta $6.000 (ver el registro de versiones). n = 81.")
guardar(fig, "A2_distribucion_dap", ANEXO_DIR)

print(f"Listo: 6 figuras principales, 2 de anexo y {len(list(TAB_DIR.glob('*.csv')))} tablas de apoyo.")
