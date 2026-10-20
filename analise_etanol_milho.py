"""
Etanol de milho x entressafra da cana: o consumo de etanol hidratado caiu menos
na entressafra nos estados produtores de etanol de milho depois que essa
produção ganhou escala?

Fonte: ANP - Vendas de derivados de petróleo e biocombustíveis (m³), mensal por UF.
Arquivo: dados/vendas-combustiveis-m3-1990-2025.csv

Ideia (diferença-em-diferenças simples):
  - Indicador: participação do etanol hidratado nas vendas do ciclo Otto
        part = EH / (EH + gasolina C)
    Usar a participação (e não o volume) controla o crescimento da frota e da
    demanda total de combustível.
  - Ano-safra da cana (Centro-Sul): abril do ano t a março de t+1.
    Safra = abr-nov; entressafra = dez-mar.
  - "Queda na entressafra" = part. média na entressafra / part. média na safra - 1
    (calculada por UF e ano-safra).
  - Grupos: estados do polo de milho (MT, GO, MS) x estados núcleo da cana
    no Centro-Sul (SP, MG, PR).
  - Períodos: antes do milho (safras 2012/13-2016/17; a 1ª usina full de milho
    começou em ago/2017 em MT) x depois (safras 2020/21-2024/25).
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf

BASE = Path(__file__).resolve().parent
ARQ = BASE / "dados" / "vendas-combustiveis-m3-1990-2025.csv"
SAIDA = BASE / "resultados"
SAIDA.mkdir(exist_ok=True)

MESES = {"JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAI": 5, "JUN": 6,
         "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12}
SIGLA = {"MATO GROSSO": "MT", "GOIÁS": "GO", "MATO GROSSO DO SUL": "MS",
         "SÃO PAULO": "SP", "MINAS GERAIS": "MG", "PARANÁ": "PR",
         "RONDÔNIA": "RO", "ACRE": "AC", "AMAZONAS": "AM", "PARÁ": "PA",
         "TOCANTINS": "TO", "RORAIMA": "RR", "AMAPÁ": "AP", "DISTRITO FEDERAL": "DF"}
MILHO = ["MT", "GO", "MS"]
CANA = ["SP", "MG", "PR"]
# Estados do Norte abastecidos principalmente a partir de MT (análise extra)
NORTE = ["RO", "AC", "AM", "PA", "TO", "RR", "AP"]
ENTRESSAFRA = [12, 1, 2, 3]
PRE = range(2012, 2017)   # safras 2012/13 ... 2016/17
POS = range(2020, 2025)   # safras 2020/21 ... 2024/25


def carregar():
    d = pd.read_csv(ARQ, sep=";", decimal=",", encoding="utf-8-sig")
    d = d[d["PRODUTO"].isin(["ETANOL HIDRATADO", "GASOLINA C"])]
    d["mes"] = d["MÊS"].map(MESES)
    d["uf"] = d["UNIDADE DA FEDERAÇÃO"].map(SIGLA)
    d = d.dropna(subset=["uf"])
    t = d.pivot_table(index=["uf", "ANO", "mes"], columns="PRODUTO",
                      values="VENDAS", aggfunc="sum").reset_index()
    t.columns = ["uf", "ano", "mes", "eh", "gc"]
    t["part"] = t["eh"] / (t["eh"] + t["gc"])
    t["safra"] = t["ano"].where(t["mes"] >= 4, t["ano"] - 1)
    t["entressafra"] = t["mes"].isin(ENTRESSAFRA)
    return t


def queda_por_safra(t):
    g = (t.groupby(["uf", "safra", "entressafra"])["part"].mean()
         .unstack().rename(columns={False: "part_safra", True: "part_entre"}))
    n = t.groupby(["uf", "safra"]).size()
    g = g[n == 12]  # só anos-safra completos
    g["queda_pct"] = (g["part_entre"] / g["part_safra"] - 1) * 100
    return g.reset_index()


def grupo(uf):
    if uf in MILHO:
        return "Milho (MT, GO, MS)"
    if uf in CANA:
        return "Cana (SP, MG, PR)"
    if uf in NORTE:
        return "Norte (RO, AC, AM, PA, TO, RR, AP)"
    return None


def main():
    t = carregar()
    q = queda_por_safra(t)
    q["grupo"] = q["uf"].map(grupo)
    q = q.dropna(subset=["grupo"])
    q["periodo"] = None
    q.loc[q["safra"].isin(PRE), "periodo"] = "Antes (2012/13-2016/17)"
    q.loc[q["safra"].isin(POS), "periodo"] = "Depois (2020/21-2024/25)"

    # 1) Tabela por UF
    por_uf = (q.dropna(subset=["periodo"])
              .pivot_table(index=["grupo", "uf"], columns="periodo", values="queda_pct"))
    por_uf["mudança (p.p.)"] = por_uf.iloc[:, 1] - por_uf.iloc[:, 0]
    por_uf = por_uf.round(1)
    por_uf.to_csv(SAIDA / "queda_entressafra_por_uf.csv")

    # 2) Tabela diferença-em-diferenças (média simples das UFs do grupo)
    did = (q.dropna(subset=["periodo"])
           .groupby(["grupo", "periodo"])["queda_pct"].mean().unstack())
    did["mudança (p.p.)"] = did.iloc[:, 1] - did.iloc[:, 0]
    did = did.round(1)
    did.to_csv(SAIDA / "tabela_did.csv")

    # 3) Regressão DiD: queda ~ milho*depois + efeitos fixos de UF e de safra,
    #    erros-padrão agrupados por UF
    r = q[q["grupo"].isin(["Milho (MT, GO, MS)", "Cana (SP, MG, PR)"])].dropna(subset=["periodo"]).copy()
    r["milho"] = r["uf"].isin(MILHO).astype(int)
    r["depois"] = r["safra"].isin(POS).astype(int)
    m = smf.ols("queda_pct ~ milho:depois + C(uf) + C(safra)", data=r).fit(
        cov_type="cluster", cov_kwds={"groups": r["uf"]})
    coef, ep, p = m.params["milho:depois"], m.bse["milho:depois"], m.pvalues["milho:depois"]
    # Com só 6 clusters o EP agrupado é frágil; reporta-se também o EP robusto (HC1)
    m_hc = smf.ols("queda_pct ~ milho:depois + C(uf) + C(safra)", data=r).fit(cov_type="HC1")

    # 4) Gráfico: queda na entressafra por ano-safra, por grupo
    serie = q[q["safra"] >= 2010].groupby(["safra", "grupo"])["queda_pct"].mean().unstack()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    cores = {"Milho (MT, GO, MS)": "#d9a400", "Cana (SP, MG, PR)": "#2a7f3f",
             "Norte (RO, AC, AM, PA, TO, RR, AP)": "#7a7a7a"}
    for g_, s in serie.items():
        ax.plot(s.index, s.values, marker="o", label=g_, color=cores[g_],
                lw=2.4 if "Norte" not in g_ else 1.4,
                ls="-" if "Norte" not in g_ else "--")
    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(2017, color="gray", lw=0.8, ls=":")
    ax.text(2017.1, ax.get_ylim()[0] * 0.95, "1ª usina de milho (MT)", fontsize=8, color="gray")
    ax.set_xlabel("Ano-safra (abr/t a mar/t+1)")
    ax.set_ylabel("Variação da participação (%)")
    ax.set_title("Participação do etanol hidratado na entressafra (dez-mar) vs. safra (abr-nov)")
    ax.set_xticks(serie.index)
    ax.set_xticklabels([f"{a % 100:02d}/{(a + 1) % 100:02d}" for a in serie.index], rotation=45)
    ax.legend(frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(SAIDA / "queda_entressafra.png", dpi=150)

    serie.round(1).to_csv(SAIDA / "queda_entressafra_por_safra.csv")

    with open(SAIDA / "resumo.txt", "w") as f:
        f.write("Queda da participação do etanol na entressafra (%), por UF\n")
        f.write(por_uf.to_string() + "\n\n")
        f.write("Diferença-em-diferenças (média das UFs)\n")
        f.write(did.to_string() + "\n\n")
        f.write(f"Regressão DiD (EF de UF e safra), coef milho x depois = {coef:.1f} p.p.\n")
        f.write(f"  EP agrupado por UF = {ep:.1f} (p = {p:.3f}); "
                f"EP robusto HC1 = {m_hc.bse['milho:depois']:.1f} "
                f"(p = {m_hc.pvalues['milho:depois']:.3f}); N = {int(m.nobs)}\n\n")
        f.write("Série por ano-safra (média das UFs do grupo)\n")
        f.write(serie.round(1).to_string() + "\n")
    print((SAIDA / "resumo.txt").read_text())


if __name__ == "__main__":
    main()
