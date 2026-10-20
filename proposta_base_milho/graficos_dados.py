"""
Gráficos com dados reais para a proposta da base do milho em MT.

Fontes (extraídas do projeto público github.com/bruno-portfolio/dbt-agrobr,
pasta painel/dados, gerado em 16/10/2026 com o pacote agrobr):
  - Conab, Acompanhamento da Safra: produção de milho por UF e safra.
  - IBGE, Produção Agrícola Municipal (PAM): produção de milho por município.
  - IBGE: malha municipal (só MT).
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PatchCollection
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Polygon

BASE = Path(__file__).resolve().parent
DADOS = BASE / "dados"
SAIDA = BASE / "figuras"
SAIDA.mkdir(exist_ok=True)

COR = "#2a78d6"
TEXTO = "#52514e"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": TEXTO, "axes.labelcolor": TEXTO,
                     "xtick.color": TEXTO, "ytick.color": TEXTO})


def producao_mt():
    """4. Produção de milho em MT por safra e participação no Brasil (Conab)."""
    d = pd.read_csv(DADOS / "milho_producao_mt_conab.csv")
    d = d[d["safra"] != "2026/27"]  # 1º levantamento, ainda é previsão
    d["mt_mi_t"] = d["conab_producao_mt_t"] / 1e6
    d["part"] = d["conab_producao_mt_t"] / d["conab_producao_brasil_t"] * 100

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    x = np.arange(len(d))
    ax.bar(x, d["mt_mi_t"], color=COR, width=0.7)
    for xi, v, p in zip(x, d["mt_mi_t"], d["part"]):
        ax.text(xi, v + 0.8, f"{v:.0f}", ha="center", fontsize=9, color="#0b0b0b")
        ax.text(xi, v / 2, f"{p:.0f}%", ha="center", fontsize=8, color="white")
    i17 = list(d["safra"]).index("2017/18")
    ax.axvline(i17 - 0.5, color=TEXTO, lw=0.8, ls=":")
    ax.text(i17 - 0.45, d["mt_mi_t"].max() * 0.97, "1ª usina de milho (ago/2017)",
            fontsize=8, color=TEXTO)
    ax.set_xticks(x)
    ax.set_xticklabels(d["safra"], rotation=45)
    ax.set_ylabel("Milhões de toneladas")
    ax.set_title("Produção de milho em Mato Grosso (no meio da barra: % do Brasil)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e5e4e0", lw=0.6)
    ax.set_axisbelow(True)
    fig.text(0.99, 0.01, "Fonte: Conab, Acompanhamento da Safra Brasileira de Grãos",
             ha="right", fontsize=8, color=TEXTO)
    fig.tight_layout()
    fig.savefig(SAIDA / "4_producao_milho_mt.png", dpi=150)
    d[["safra", "mt_mi_t", "part"]].round(1).to_csv(SAIDA / "4_producao_milho_mt.csv", index=False)


def mapa_municipios(anos=(2015, 2025)):
    """5. Mapa da produção de milho por município de MT (IBGE/PAM)."""
    geo = json.load(open(DADOS / "municipios_mt.geojson"))
    pam = pd.read_csv(DADOS / "milho_producao_municipios_mt_pam.csv")

    limites = [0, 50e3, 200e3, 500e3, 1e6, 2e6, 6e6]
    rotulos = ["0", "50 mil", "200 mil", "500 mil", "1 mi", "2 mi", "6 mi"]
    cmap = ListedColormap(["#eef4fc", "#c6dbf5", "#8fb9ea", "#4f8fdc", "#2a6fc4", "#163f7a"])
    norm = BoundaryNorm(limites, cmap.N)

    fig, axs = plt.subplots(1, len(anos), figsize=(10, 4.4))
    for ax, ano in zip(axs, anos):
        prod = pam[pam["ano"] == ano].set_index("cod_municipio")["producao_t"]
        patches, valores = [], []
        for f in geo["features"]:
            cod = int(f["properties"]["codarea"])
            g = f["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for poly in polys:
                patches.append(Polygon(np.array(poly[0]), closed=True))
                valores.append(prod.get(cod, 0) or 0)
        pc = PatchCollection(patches, cmap=cmap, norm=norm, edgecolor="white", linewidth=0.3)
        pc.set_array(np.array(valores))
        ax.add_collection(pc)
        ax.autoscale_view()
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{ano}: {prod.sum() / 1e6:.0f} milhões de t", fontsize=11)
    cb = fig.colorbar(pc, ax=axs, orientation="horizontal", fraction=0.04, pad=0.02,
                      ticks=limites)
    cb.ax.set_xticklabels(rotulos, fontsize=8)
    cb.outline.set_visible(False)
    cb.set_label("Produção de milho por município (t)", fontsize=9, color=TEXTO)
    fig.suptitle("Onde o milho de Mato Grosso é produzido", fontsize=12, y=1.04)
    fig.text(0.99, 0.01, "Fonte: IBGE, Produção Agrícola Municipal", ha="right",
             fontsize=8, color=TEXTO)
    fig.savefig(SAIDA / "5_mapa_milho_municipios.png", dpi=150, bbox_inches="tight")


if __name__ == "__main__":
    producao_mt()
    mapa_municipios()
