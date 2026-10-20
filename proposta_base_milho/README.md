# A usina na porteira: o etanol de milho e o desconto do milho de Mato Grosso

Títulos alternativos:
- *Menos frete, mais preço: o etanol de milho e a base do milho em Mato Grosso*
- *Do porto à porteira: a demanda das usinas de etanol e o preço do milho em MT*

## A história

1. **O problema.** Mato Grosso colhe muito mais milho do que consome. Antes das
   usinas de etanol, o excedente tinha que viajar mais de 2.000 km até os portos
   (Santos, Paranaguá, Arco Norte). O preço que o produtor recebe é, grosso modo,
   o preço no porto menos o frete. Por isso o milho de MT vale bem menos que o
   de Campinas: essa diferença é a **base**.
2. **O agravante sazonal.** A colheita do milho safrinha (jun–set) disputa
   caminhão e armazém com a soja ainda em escoamento. O frete sobe e o desconto
   fica ainda maior justamente quando o produtor mais precisa vender.
3. **A mudança.** Desde 2017 (FS Bioenergia em Lucas do Rio Verde) surgiram
   várias usinas de etanol de milho no estado. Elas compram milho o ano todo,
   na porta da fazenda, e uma parte crescente da produção de MT deixou de
   depender do frete até o porto.
4. **A hipótese.** Com um comprador local, o preço do milho em MT passou a
   depender menos do frete: **a base ficou menor** (o milho de MT ficou mais
   perto do preço de Campinas), **e a queda de preço na colheita da safrinha
   ficou mais suave.** O efeito deve ser maior nas regiões de MT que receberam
   usinas.

## Gráficos de intuição (ilustrativos, em `figuras/`)

| Figura | O que mostra |
|---|---|
| `1_preco_vs_distancia.png` | Preço do milho cai com a distância do porto (custo de frete). A usina cria um "porto" dentro de MT e levanta o preço local. |
| `2_base_no_tempo.png` | O que se espera ver na série: base baixa e com quedas fortes na safrinha antes de 2017; base mais alta e mais estável depois. |
| `3_did.png` | A comparação que identifica o efeito: regiões de MT com usina x sem usina, antes x depois. |

São esquemas, não dados. Gerados por `graficos_conceituais.py`.

## Gráficos com dados (a construir)

1. **Quanto do milho de MT as usinas absorvem**: produção de milho em MT (Conab)
   e milho processado pelas usinas (UNEM/IMEA), 2015–2025. Mostra que o choque
   de demanda é grande.
2. **Base ao longo do tempo**: preço do milho em MT (IMEA) ÷ indicador
   CEPEA/ESALQ (Campinas), mensal, com linha vertical em 2017.
3. **Perfil sazonal da base**: média por mês do ano, antes (2010–2016) x depois
   (2019–2025). Esperado: a "barriga" de jul–set fica mais rasa.
4. **Diferença-em-diferenças**: base nas macrorregiões do IMEA com usina
   x sem usina, antes x depois.

## Dados necessários

- IMEA: preço do milho por macrorregião de MT e frete MT → portos (imea.com.br).
- CEPEA/ESALQ: indicador do milho (Campinas) (cepea.esalq.usp.br).
- Conab: produção de milho por UF.
- UNEM / IMEA: milho processado e localização das usinas de etanol de milho.

## Cuidados

- O frete e o câmbio também mexem na base. Controle com a série de frete do IMEA
  ou declare como limitação.
- No mesmo período, a ferrovia (Rumo, terminal de Rondonópolis desde 2013) e
  os portos do Arco Norte também reduziram o custo de escoamento. A comparação entre regiões com e sem usina
  ajuda a separar esse efeito.
