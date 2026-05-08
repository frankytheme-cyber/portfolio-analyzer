"""
Chromatic Language — Portfolio Analyzer Dashboard
Design philosophy: color as primary information system, Josef Albers-inspired
chromatic fields, geometric precision, minimal typography.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe
import numpy as np

# ── Chromatic Language Palette ────────────────────────────────────────────────
# Each color is a semantic category — not decoration
C_BG       = "#0A0C10"       # void — deep background
C_SURFACE  = "#111318"       # lifted surface
C_BOND     = "#1A6B8A"       # bonds — cool cerulean depth
C_BOND_L   = "#22D3EE"       # bonds — luminous edge
C_EQUITY   = "#1A6B47"       # equity — forest field
C_EQUITY_L = "#34D399"       # equity — luminous edge
C_CERT     = "#6B3A8A"       # certificates — violet frequency
C_CERT_L   = "#A78BFA"       # certificates — luminous edge
C_COMM     = "#8A5A1A"       # commodity — amber earth
C_COMM_L   = "#FBBF24"       # commodity — luminous edge
C_OTHER    = "#3A4A5A"       # other — steel muted
C_TEXT     = "#E8ECF1"       # primary text
C_MUTED    = "#4A5568"       # secondary / labels
C_GRID     = "#1A1F2A"       # grid lines

# Asset class data (mock portfolio)
CLASSES = ["BOND", "ETF", "CERTIFICATE", "COMMODITY", "ALTRO"]
VALUES  = [142000, 98000, 54000, 28000, 12000]
COLORS_FIELDS = [C_BOND, C_EQUITY, C_CERT, C_COMM, C_OTHER]
COLORS_LIGHT  = [C_BOND_L, C_EQUITY_L, C_CERT_L, C_COMM_L, "#7A8599"]

# Geography
GEO_LABELS = ["World", "USA", "Europa", "Italia", "Emergenti", "Altro"]
GEO_VALUES = [89000, 76000, 62000, 48000, 31000, 28000]
GEO_COLORS = ["#1E3A5F", "#22D3EE", "#1A6B8A", "#0E3B2A", "#34D399", "#2D3748"]

# Sector
SEC_LABELS = ["Technology", "Finance", "Healthcare", "Energy", "Consumer", "Altro"]
SEC_VALUES  = [84000, 71000, 48000, 44000, 39000, 48000]
SEC_COLORS  = ["#22D3EE", "#A78BFA", "#34D399", "#FBBF24", "#FB7185", "#4A5568"]

TOTAL = sum(VALUES)
N_ASSETS = 24

# ── Canvas ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 13), dpi=150, facecolor=C_BG)

# Precise grid: 20×13 inches → use absolute axes
ax_main = fig.add_axes([0, 0, 1, 1])
ax_main.set_xlim(0, 20)
ax_main.set_ylim(0, 13)
ax_main.axis("off")
ax_main.set_facecolor(C_BG)

def rect(x, y, w, h, color, alpha=1.0, zorder=2):
    ax_main.add_patch(patches.Rectangle((x, y), w, h,
        facecolor=color, alpha=alpha, zorder=zorder, linewidth=0))

def label(x, y, text, size=7, color=C_MUTED, ha="left", va="bottom",
          weight="normal", zorder=5, alpha=1.0):
    ax_main.text(x, y, text, fontsize=size, color=color, ha=ha, va=va,
                 fontweight=weight, zorder=zorder, alpha=alpha,
                 fontfamily="monospace")

def thin_label(x, y, text, size=6.5, color=C_MUTED, ha="left", va="bottom"):
    ax_main.text(x, y, text, fontsize=size, color=color, ha=ha, va=va,
                 fontfamily="monospace", alpha=0.7)

# ── Background grid (subtle) ──────────────────────────────────────────────────
for xi in np.arange(0, 20.1, 1.0):
    ax_main.plot([xi, xi], [0, 13], color=C_GRID, lw=0.3, zorder=0)
for yi in np.arange(0, 13.1, 1.0):
    ax_main.plot([0, 20], [yi, yi], color=C_GRID, lw=0.3, zorder=0)

# ── Header band ───────────────────────────────────────────────────────────────
rect(0, 11.6, 20, 1.4, C_SURFACE)
# Accent bar — thin luminous line at top
rect(0, 12.95, 20, 0.05, C_BOND_L, alpha=0.6)

label(0.5, 12.35, "PORTFOLIO ANALYZER", size=9, color=C_TEXT,
      weight="bold", va="center")
thin_label(0.5, 12.05, "CHROMATIC LANGUAGE  ·  ALLOCATION SYSTEM", size=5.5,
           color=C_MUTED, va="center")

# Date / metadata — right aligned
label(19.5, 12.35, "2026.04.08", size=7, color=C_MUTED, ha="right", va="center")
thin_label(19.5, 12.05, "24 HOLDINGS  ·  ACTIVE", size=5.5,
           color=C_MUTED, ha="right", va="center")

# ── KPI row — three chromatic field cards ─────────────────────────────────────
kpi_y = 10.1
kpi_h = 1.2
gap = 0.25
kpi_w = (20 - 0.5*2 - gap*2) / 3

for i, (val, lbl, col_f, col_l) in enumerate([
    (f"€ {TOTAL/1e6:.2f}M", "CONTROVALORE TOTALE", C_BOND, C_BOND_L),
    (f"{N_ASSETS}", "NUMERO TITOLI", C_EQUITY, C_EQUITY_L),
    (f"{max(VALUES)/TOTAL*100:.1f}%", "PESO MASSIMO", C_CERT, C_CERT_L),
]):
    x0 = 0.5 + i * (kpi_w + gap)
    rect(x0, kpi_y, kpi_w, kpi_h, col_f, alpha=0.18)
    # left accent bar
    rect(x0, kpi_y, 0.04, kpi_h, col_l, alpha=0.9)
    # value
    ax_main.text(x0 + 0.22, kpi_y + kpi_h*0.62, val,
                 fontsize=16, color=col_l, fontweight="bold",
                 fontfamily="monospace", va="center", zorder=5)
    # label
    thin_label(x0 + 0.22, kpi_y + kpi_h*0.22, lbl,
               size=5.8, color=col_l, va="center")

# ── Three donut charts ────────────────────────────────────────────────────────
donut_y = 5.8
donut_h = 3.8

for col_idx, (title, labels, vals, cols) in enumerate([
    ("ASSET CLASS",  CLASSES,     VALUES,     COLORS_FIELDS),
    ("GEOGRAFIA",    GEO_LABELS,  GEO_VALUES, GEO_COLORS),
    ("SETTORE",      SEC_LABELS,  SEC_VALUES, SEC_COLORS),
]):
    x0 = 0.5 + col_idx * (kpi_w + gap)
    rect(x0, donut_y, kpi_w, donut_h, C_SURFACE, alpha=0.5)

    # Section label
    thin_label(x0 + 0.15, donut_y + donut_h - 0.22, title, size=5.8,
               color=C_MUTED, va="center")

    # Embed a real donut via inset_axes
    inset_x = (x0 + kpi_w/2) / 20
    inset_y = (donut_y + donut_h/2 - 0.3) / 13
    inset_w = kpi_w * 0.55 / 20
    inset_h = donut_h * 0.60 / 13

    ax_d = fig.add_axes([inset_x - inset_w/2, inset_y - inset_h/2,
                          inset_w, inset_h])
    ax_d.set_facecolor("none")
    wedges, _ = ax_d.pie(
        vals,
        colors=cols,
        wedgeprops=dict(width=0.38, linewidth=1.2, edgecolor=C_BG),
        startangle=90,
    )
    # center text
    ax_d.text(0, 0, f"{len(labels)}", ha="center", va="center",
              fontsize=10, color=C_TEXT, fontweight="bold",
              fontfamily="monospace")
    ax_d.axis("equal")

    # Legend — color chips + labels
    leg_x = x0 + 0.15
    leg_y_start = donut_y + 1.05
    row_h = 0.30
    for j, (lbl, clr, v) in enumerate(zip(labels, cols, vals)):
        ly = leg_y_start - j * row_h
        if ly < donut_y + 0.12:
            break
        rect(leg_x, ly - 0.07, 0.12, 0.14, clr, alpha=0.9)
        thin_label(leg_x + 0.18, ly - 0.04, lbl[:12], size=5.6,
                   color=C_MUTED, va="center")
        pct = v / sum(vals) * 100
        thin_label(x0 + kpi_w - 0.15, ly - 0.04, f"{pct:.0f}%",
                   size=5.6, color=C_TEXT, ha="right", va="center")

# ── Chromatic allocation bar (full width) ────────────────────────────────────
bar_y = 5.1
bar_h = 0.45
bar_x = 0.5
bar_w = 19.0

# Background
rect(bar_x, bar_y, bar_w, bar_h, C_SURFACE, alpha=0.8)

# Segmented bar
cursor = bar_x
total_val = sum(VALUES)
for val, col_f, col_l, cls in zip(VALUES, COLORS_FIELDS, COLORS_LIGHT, CLASSES):
    seg_w = (val / total_val) * bar_w
    rect(cursor, bar_y, seg_w, bar_h, col_f, alpha=0.85)
    # luminous top edge
    rect(cursor, bar_y + bar_h - 0.025, seg_w, 0.025, col_l, alpha=0.6)
    # label if wide enough
    if seg_w > 1.2:
        pct = val / total_val * 100
        ax_main.text(cursor + seg_w/2, bar_y + bar_h/2, f"{pct:.0f}%",
                     ha="center", va="center", fontsize=6.5,
                     color=col_l, fontweight="bold", fontfamily="monospace",
                     zorder=5)
    cursor += seg_w

# Labels below bar
cursor = bar_x
for val, col_l, cls in zip(VALUES, COLORS_LIGHT, CLASSES):
    seg_w = (val / total_val) * bar_w
    if seg_w > 0.8:
        thin_label(cursor + seg_w/2, bar_y - 0.18, cls,
                   size=5, color=col_l, ha="center")
    cursor += seg_w

# ── Holdings table ─────────────────────────────────────────────────────────────
tbl_y = 0.3
tbl_x = 0.5
tbl_w = 19.0
tbl_row_h = 0.36

HOLDINGS = [
    ("IT0005092166", "BTP 1.45% 2036",           "BOND",        142000, 42.4),
    ("IE00B4L5Y983", "iShares MSCI World UCITS",  "ETF",          54000, 16.1),
    ("IE00B3F81R35", "iShares Nasdaq 100 UCITS",  "ETF",          44000, 13.1),
    ("XS2345678901", "Vontobel Cash Collect",      "CERTIFICATE",  32000,  9.5),
    ("IE00B14X4S71", "iShares Gold ETC Physical", "COMMODITY",    28000,  8.3),
    ("US0378331005", "Apple Inc.",                 "AZIONE",       18000,  5.4),
    ("DE0008404005", "Allianz SE",                 "AZIONE",       16000,  4.8),
]

COLS = ["ISIN", "NOME", "CLASSE", "CONTROVALORE", "PESO %"]
COL_X = [tbl_x, tbl_x + 1.9, tbl_x + 10.5, tbl_x + 14.0, tbl_x + 17.2]
COL_W = [1.8, 8.5, 3.4, 3.1, 1.7]

CLASS_COLOR = {
    "BOND": C_BOND_L, "ETF": C_EQUITY_L, "CERTIFICATE": C_CERT_L,
    "COMMODITY": C_COMM_L, "AZIONE": "#60A5FA",
}

# Header row
rect(tbl_x, tbl_y + len(HOLDINGS)*tbl_row_h, tbl_w,
     tbl_row_h, C_SURFACE, alpha=0.9)
for col_name, cx in zip(COLS, COL_X):
    thin_label(cx + 0.08, tbl_y + len(HOLDINGS)*tbl_row_h + tbl_row_h*0.35,
               col_name, size=5.5, color=C_MUTED, va="center")

# Data rows
for r, (isin, nome, classe, ctv, peso) in enumerate(HOLDINGS):
    row_y = tbl_y + (len(HOLDINGS) - 1 - r) * tbl_row_h
    row_bg = C_BG if r % 2 == 0 else C_SURFACE
    rect(tbl_x, row_y, tbl_w, tbl_row_h, row_bg, alpha=0.6)

    cls_col = CLASS_COLOR.get(classe, C_MUTED)

    # ISIN
    thin_label(COL_X[0] + 0.08, row_y + tbl_row_h*0.35,
               isin, size=5.5, color=C_MUTED, va="center")
    # Nome
    thin_label(COL_X[1] + 0.08, row_y + tbl_row_h*0.35,
               nome[:38], size=5.8, color=C_TEXT, va="center")
    # Classe chip
    rect(COL_X[2] + 0.08, row_y + tbl_row_h*0.18,
         len(classe)*0.072 + 0.16, tbl_row_h*0.6,
         cls_col, alpha=0.12)
    thin_label(COL_X[2] + 0.16, row_y + tbl_row_h*0.35,
               classe, size=5.5, color=cls_col, va="center")
    # Controvalore
    thin_label(COL_X[3] + 0.08, row_y + tbl_row_h*0.35,
               f"€ {ctv:,.0f}", size=5.8, color=C_TEXT, va="center")
    # Peso bar + value
    bar_max = 19.0
    pb_w = (peso / 100) * 1.4
    rect(COL_X[4] + 0.08, row_y + tbl_row_h*0.25,
         1.4, tbl_row_h*0.5, cls_col, alpha=0.08)
    rect(COL_X[4] + 0.08, row_y + tbl_row_h*0.25,
         pb_w, tbl_row_h*0.5, cls_col, alpha=0.5)
    thin_label(COL_X[4] + 1.54, row_y + tbl_row_h*0.35,
               f"{peso:.1f}%", size=5.5, color=cls_col, va="center")

# Bottom separator
rect(tbl_x, tbl_y - 0.02, tbl_w, 0.02, C_BOND_L, alpha=0.2)

# ── Footer ────────────────────────────────────────────────────────────────────
thin_label(0.5, 0.10, "CHROMATIC LANGUAGE  ·  PORTFOLIO ANALYZER  ·  2026",
           size=5, color=C_MUTED, va="center")
thin_label(19.5, 0.10, "COLOR IS INFORMATION", size=5,
           color=C_MUTED, ha="right", va="center")

# ── Save ──────────────────────────────────────────────────────────────────────
out = "/Users/simonepuliti/Progetti/portfolio-analyzer/.claude/canvas-design-workspace/iteration-1/eval-chromatic-layout/with_skill/outputs/chromatic-language-dashboard.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=C_BG,
            pad_inches=0.02)
plt.close()
print(f"Saved: {out}")
