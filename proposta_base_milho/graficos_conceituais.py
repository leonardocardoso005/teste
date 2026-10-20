"""
Gráficos CONCEITUAIS (ilustrativos, sem dados reais) para a proposta:
"A usina na porteira: o etanol de milho e o desconto do milho de Mato Grosso".

Servem para mostrar a intuição antes de existir a análise com dados.
Os eixos não têm números de propósito.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SAIDA = Path(__file__).resolve().parent / "figuras"
SAIDA.mkdir(exist_ok=True)

ANTES = "#2a78d6"    # azul
DEPOIS = "#eb6834"   # laranja
TEXTO = "#52514e"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": TEXTO, "axes.labelcolor": TEXTO,
                     "xtick.color": TEXTO, "ytick.color": TEXTO})


def limpar(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])


def nota(fig):
    fig.text(0.99, 0.01, "Ilustrativo: não são dados reais", ha="right",
             fontsize=8, color=TEXTO, style="italic")


# 1) Preço do milho conforme se afasta do porto
x = np.linspace(0, 1, 200)            # 0 = porto, 1 = Médio-Norte de MT
antes = 1 - 0.6 * x                   # preço = porto - frete x distância
usina = 0.8
depois = np.maximum(antes, 0.62 - 0.35 * np.abs(x - 1) * 2.2)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(x, antes, color=ANTES, lw=2, label="Antes das usinas: preço = porto − frete")
ax.plot(x, depois, color=DEPOIS, lw=2, ls="--", label="Depois: usina compra o milho no próprio estado")
ax.annotate("", xy=(1, antes[-1]), xytext=(1, 1), arrowprops=dict(arrowstyle="<->", color=ANTES))
ax.text(0.985, 0.72, "desconto\nantes", ha="right", color=ANTES, fontsize=9)
ax.annotate("", xy=(0.93, depois[-1]), xytext=(0.93, 1), arrowprops=dict(arrowstyle="<->", color=DEPOIS))
ax.text(0.905, 0.86, "desconto\ndepois", ha="right", color=DEPOIS, fontsize=9)
ax.axhline(1, color=TEXTO, lw=0.8, ls=":")
ax.text(0.01, 1.01, "preço no porto (Paranaguá/Santos)", color=TEXTO, fontsize=8, va="bottom")
ax.set_xlabel("Distância do porto  →  (porto ... Sorriso/Lucas do Rio Verde)")
ax.set_ylabel("Preço do milho recebido pelo produtor")
ax.set_ylim(0.3, 1.08)
ax.set_title("1. Por que o milho de MT vale menos: o frete até o porto")
ax.legend(frameon=False, loc="lower left", fontsize=9)
limpar(ax)
nota(fig)
fig.tight_layout()
fig.savefig(SAIDA / "1_preco_vs_distancia.png", dpi=150)

# 2) Base (preço MT / preço referência) ao longo do tempo
rng = np.random.default_rng(1)
t = np.arange(2010, 2026, 1 / 12)
saz = -np.cos(2 * np.pi * (t % 1 - 0.62))          # desconto maior na colheita da safrinha (jul-set)
nivel = np.where(t < 2017.6, 0.62, 0.62 + 0.14 * (1 - np.exp(-(t - 2017.6) / 2.5)))
amp = np.where(t < 2017.6, 0.08, 0.08 - 0.04 * (1 - np.exp(-(t - 2017.6) / 2.5)))
base = nivel + amp * saz + rng.normal(0, 0.012, t.size)
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(t[t < 2017.6], base[t < 2017.6], color=ANTES, lw=2)
ax.plot(t[t >= 2017.6], base[t >= 2017.6], color=DEPOIS, lw=2)
ax.axvline(2017.6, color=TEXTO, lw=0.8, ls=":")
ax.text(2017.7, 0.5, "1ª usina de milho\n(Lucas do Rio Verde, 2017)", color=TEXTO, fontsize=8)
ax.text(2010.3, 0.77, "antes: desconto grande,\nainda pior na colheita da safrinha", color=ANTES, fontsize=9)
ax.text(2021, 0.86, "depois: desconto menor\ne mais estável", color=DEPOIS, fontsize=9)
ax.axhline(1, color=TEXTO, lw=0.8, ls=":")
ax.text(2010, 1.005, "preço igual ao de Campinas", color=TEXTO, fontsize=8, va="bottom")
ax.set_ylim(0.45, 1.05)
ax.set_xticks([2010, 2014, 2017.6, 2022, 2025])
ax.set_xticklabels(["2010", "2014", "2017", "2022", "2025"])
ax.set_yticks([])
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylabel("Preço do milho em MT ÷ preço em Campinas")
ax.set_title("2. O que esperamos ver na série da base")
nota(fig)
fig.tight_layout()
fig.savefig(SAIDA / "2_base_no_tempo.png", dpi=150)

# 3) Diferença-em-diferenças: regiões com e sem usina
fig, ax = plt.subplots(figsize=(6.5, 4.5))
xs = [0, 1]
com = [0.60, 0.78]
sem = [0.55, 0.62]
contraf = [0.60, 0.67]
ax.plot(xs, com, color=DEPOIS, lw=2, marker="o", ms=8, label="Regiões de MT com usina")
ax.plot(xs, sem, color=ANTES, lw=2, marker="o", ms=8, label="Regiões de MT sem usina")
ax.plot(xs, contraf, color=DEPOIS, lw=1.2, ls=":", label="Com usina, se nada tivesse mudado")
ax.annotate("", xy=(1.04, com[1]), xytext=(1.04, contraf[1]),
            arrowprops=dict(arrowstyle="<->", color=TEXTO))
ax.text(1.07, (com[1] + contraf[1]) / 2, "efeito\nda usina", va="center", color=TEXTO, fontsize=9)
ax.set_xticks(xs)
ax.set_xticklabels(["Antes de 2017", "Depois de 2017"])
ax.set_xlim(-0.2, 1.35)
ax.set_yticks([])
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylabel("Preço local ÷ preço de referência")
ax.set_title("3. A comparação que identifica o efeito")
ax.legend(frameon=False, loc="upper left", fontsize=9)
nota(fig)
fig.tight_layout()
fig.savefig(SAIDA / "3_did.png", dpi=150)
