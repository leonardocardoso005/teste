# Etanol de milho x entressafra da cana (TCC)

Pergunta: nos meses de entressafra da cana (dez–mar), o etanol hidratado
perdeu menos espaço nos estados produtores de etanol de milho (MT, GO, MS)
depois que essa produção ganhou escala (a partir de 2017)?

- Dados: ANP, vendas mensais de combustíveis por UF (m³), `dados/`.
- Script: `python3 analise_etanol_milho.py` (requer pandas, matplotlib, statsmodels).
- Saídas: `resultados/` (tabelas CSV, `resumo.txt` e gráfico `queda_entressafra.png`).

Método: participação do etanol hidratado nas vendas do ciclo Otto
(EH / (EH + gasolina C)), comparando a média da entressafra (dez–mar) com a da
safra (abr–nov) em cada ano-safra; diferença-em-diferenças entre estados do
milho e estados núcleo da cana (SP, MG, PR), antes (2012/13–2016/17) e depois
(2020/21–2024/25).
