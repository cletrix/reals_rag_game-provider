---
name: gates-of-olympus
description: >
  Conhecimento técnico e de produto sobre o slot Gates of Olympus (Pragmatic Play),
  conhecido no Brasil como "Veio do Raio" ou "Velho do Raio". Use este skill sempre
  que precisar raciocinar sobre mecânicas de jogo, paytable, lógica de FreeSpin,
  comportamento de multiplicadores, ou desenvolver simulações, relatórios, dashboards
  e ferramentas relacionadas a este título de iGaming.
tags: [igaming, slot, pragmatic-play, vlt, paytable, freespin, brasil]
---

# Gates of Olympus — Skill de Conhecimento de Produto

> **Apelido brasileiro:** Veio do Raio / Velho do Raio  
> **Desenvolvedora:** Pragmatic Play  
> **Lançamento:** Fevereiro de 2021  
> **Prêmio:** Game of the Year — EGR Operator Awards 2021 · #1 slot mais jogado globalmente em 2022–2023

---

## 1. Visão Geral

| Atributo              | Valor                          |
|-----------------------|--------------------------------|
| Grid                  | 6 colunas × 5 linhas (30 pos.) |
| Sistema de pagamento  | Scatter Pays / Pay Anywhere    |
| Mínimo para ganhar    | 8 símbolos idênticos           |
| RTP padrão            | 96,50%                         |
| Volatilidade          | Alta (5/5)                     |
| Ganho máximo          | 5.000× a aposta                |
| Wild                  | Não existe                     |
| Paylines fixas        | Não existem                    |
| Mecânica de cascata   | Sim (Tumble)                   |
| Multiplicadores base  | 2× a 500× (orbs)               |

---

## 2. Símbolos e Paytable Completa

Existem **9 símbolos regulares** + 1 símbolo especial (Scatter Zeus) + Orbs multiplicadores.  
Os pagamentos abaixo são expressos como **multiplicador da aposta total** (× bet).

### 2.1 Símbolos de Baixo Pagamento — Gemas (5 tipos)

| Símbolo        | Cor     | 8–9 símbolos | 10–11 símbolos | 12–30 símbolos |
|----------------|---------|:------------:|:--------------:|:--------------:|
| 💎 Gema Azul   | Azul    |    0,25×     |     0,75×      |      2×        |
| 💜 Gema Verde  | Verde   |    0,40×     |     0,90×      |      4×        |
| 💛 Gema Amarela| Amarela |    0,50×     |     1,00×      |      5×        |
| 💙 Gema Roxa   | Roxa    |    0,80×     |     1,20×      |      8×        |
| ❤️ Gema Vermelha| Vermelha|    1,00×     |     1,50×      |     10×        |

### 2.2 Símbolos de Alto Pagamento — Relíquias Gregas (4 tipos)

| Símbolo           | Item          | 8–9 símbolos | 10–11 símbolos | 12–30 símbolos |
|-------------------|---------------|:------------:|:--------------:|:--------------:|
| 🏆 Taça / Cálice  | Goblet/Cup    |    1,50×     |      2×        |     12×        |
| 💍 Anel            | Ring          |    2,00×     |      5×        |     15×        |
| ⏳ Ampulheta       | Hourglass     |    2,50×     |     10×        |     25×        |
| 👑 Coroa Dourada  | Crown/Diadem  |   10,00×     |     25×        |     50×        |

> **A Coroa Dourada é o símbolo regular de maior pagamento:** até 50× a aposta com 12+ no grid.

### 2.3 Símbolo Especial — Zeus (Scatter)

| Scatters no grid | Pagamento instantâneo | Ação                        |
|:----------------:|:---------------------:|:----------------------------|
| 4 scatters       | 3×                    | Ativa Free Spins (15 giros) |
| 5 scatters       | 5×                    | Ativa Free Spins (15 giros) |
| 6 scatters       | 100×                  | Ativa Free Spins (15 giros) |

> **Retrigger:** 3 Scatters durante o Free Spin concedem +5 giros adicionais (sem limite de retriggers).

### 2.4 Orbs Multiplicadores (símbolo especial flutuante)

Os Orbs **não formam clusters por si só** — só funcionam quando há uma vitória simultânea no grid.

| Valores possíveis dos Orbs |
|:--------------------------:|
| 2×, 3×, 4×, 5×, 6×, 8×, 10×, 12×, 15×, 20×, 25×, 50×, 100×, 250×, 500× |

- **Múltiplos Orbs são SOMADOS**, nunca multiplicados entre si.
  - Exemplo: Orb 50× + Orb 100× = **150× total** (não 5.000×)
- No jogo base: aplicam ao tumble atual e **resetam para 1×** após.
- No Free Spin: acumulam em um **Multiplicador Global persistente** (ver Seção 4).

---

## 3. Mecânica da Grade — Múltiplos Prêmios e Tumble (Cascata)

### 3.1 Dois tipos de "múltiplos prêmios" — distinção crítica

O jogo permite ganhar múltiplos prêmios num mesmo giro de **duas formas diferentes**:

**TIPO A — Clusters simultâneos no grid inicial (raro)**

Com 30 posições e mínimo de 8 por cluster, o teto teórico é `⌊30 ÷ 8⌋ = 3` clusters
simultâneos. Todos são avaliados e pagos ao mesmo tempo, antes de qualquer Tumble.

```
GRID INICIAL com 2 clusters simultâneos:

Col:  1    2    3    4    5    6
L1 [ 👑   👑   💎   💎   💎   💎 ]
L2 [ 👑   👑   💎   💎   💎   💎 ]   Cluster A: 10× Coroa (cols 1-2)
L3 [ 👑   👑   💎   💎   💎   🎭 ]   → paga 25× bet
L4 [ 👑   👑   🎭   🎭   🎭   🎭 ]   Cluster B: 10× Gema Azul (cols 3-5)
L5 [ 👑   👑   🎭   🎭   🎭   🎭 ]   → paga 0,75× bet
                                      Ambos pagos SIMULTANEAMENTE
```

**TIPO B — Múltiplos prêmios via Tumble (comum — é o coração do jogo)**

Após cada cluster vencedor ser removido, novos símbolos caem e podem formar
novos clusters — tudo dentro do **mesmo giro pago**, sem custo adicional.
Não há limite de iterações por giro.

```
GIRO 1 (inicial)      TUMBLE 1              TUMBLE 2
Col: 1 2 3 4 5 6      Col: 1 2 3 4 5 6      Col: 1 2 3 4 5 6
[ A A B B C C ]       [ N N B B C C ]       [ N N N N C C ]
[ A A B B C C ]       [ N N B B C C ]       [ N N N N C C ]
[ A A B B C C ]  →    [ N N B B C C ]  →    [ N N N N C C ]
[ A A 🎭 🎭 🎭 🎭 ]   [ 🎭 🎭 B B C C ]   [ N N B B C C ]
[ 🎭 🎭 🎭 🎭 🎭 🎭 ] [ 🎭 🎭 🎭 🎭 🎭 🎭 ] [ 🎭 🎭 🎭 🎭 🎭 🎭 ]

Prêmio 1: 8× A        Prêmio 2: 8× B        Prêmio 3: 8× C
                       (novos N caíram)       (novos N caíram)
← ─────────────── tudo no mesmo giro pago ─────────────────── →
```

### 3.2 O que tem e o que NÃO tem limite

| O que tem limite                        | O que NÃO tem limite               |
|-----------------------------------------|------------------------------------|
| Clusters simultâneos no grid inicial: **3** | Número de Tumbles por giro     |
| Posições no grid: **30**               | Iterações de cascata               |
| Orb máximo individual: **500×**        | Retriggers no Free Spin            |
| Ganho máximo total: **5.000× bet**     | Clusters acumulados via Tumble     |

> **Consequência prática:** embora o teto seja 3 clusters simultâneos no grid inicial,
> uma sequência de Tumbles pode gerar **muito mais de 3 prêmios por giro** — cada
> nova "gaveta" repovoada com 30 símbolos frescos cria potencialmente novos clusters.
> Jogadores chamam isso de **"chain"** (corrente).

### 3.3 Fluxo completo do Tumble

```
Spin pago
    │
    ▼
Avalia grid inteiro
    │
Encontrou 1+ cluster de 8+? ── NÃO ──→ Giro encerrado (sem prêmio)
    │
   SIM
    │
    ▼
Paga TODOS os clusters encontrados (podem ser 1, 2 ou 3 simultâneos)
Aplica Orbs presentes (somados)
    │
    ▼
Remove símbolos vencedores
Símbolos restantes caem
Novos símbolos preenchem o topo
    │
    ▼
Avalia grid novamente ──→ volta ao início (sem custo)
    │
Nenhum cluster → Giro encerrado
```

---

## 4. Free Spins — Comportamento Detalhado com Exemplos

### 4.1 Diferença fundamental: Base Game vs. Free Spins

```
BASE GAME                         FREE SPINS
─────────────────────────         ─────────────────────────
Giro → Vitória + Orb 10×          Giro → Vitória + Orb 10×
Multiplicador aplicado: 10×        Multiplicador ACUMULA: +10×
Próximo giro: reset → 1×           Próximo giro: mult já é 10×
                                   Giro → Vitória + Orb 25×
                                   Multiplicador ACUMULA: +25×
                                   Total: 35× (10+25)
                                   Próximo giro: mult já é 35×
                                   Giro → Vitória + Orb 2×
                                   Total: 37× — aplicado a TODOS os wins
```

### 4.2 Simulação de Sessão de Free Spin (15 giros)

```
╔═══════════════════════════════════════════════════════════════════════╗
║              GATES OF OLYMPUS — SIMULAÇÃO FREE SPIN                  ║
║              Aposta: R$ 1,00 | Free Spins: 15 + 5 (retrigger)        ║
╠═══╦══════════════════════════════╦══════════╦════════════╦═══════════╣
║ # ║ Evento do Giro               ║ Orb Caiu ║ Mult Total ║ Ganho (R$)║
╠═══╬══════════════════════════════╬══════════╬════════════╬═══════════╣
║ 1 ║ 9× Gema Azul                 ║  nenhum  ║    1×      ║  R$ 0,25  ║
║ 2 ║ sem vitória                  ║  nenhum  ║    1×      ║  R$ 0,00  ║
║ 3 ║ 10× Gema Verde + Orb         ║   +8×    ║    9×      ║  R$ 8,10  ║
║   ║   └ tumble: 8× Gema Roxa     ║  nenhum  ║    9×      ║  R$ 13,50 ║
║ 4 ║ sem vitória                  ║  nenhum  ║    9×      ║  R$ 0,00  ║
║ 5 ║ 11× Coroa Dourada + Orb      ║  +25×    ║   34×      ║  R$ 850,00║
║   ║   └ tumble: 9× Anel          ║  nenhum  ║   34×      ║  R$ 68,00 ║
║ 6 ║ 3× Zeus → RETRIGGER +5 spins ║  nenhum  ║   34×      ║  R$ 0,00  ║
║ 7 ║ 8× Ampulheta + Orb           ║ +100×    ║  134×      ║  R$ 335,00║
║ 8 ║ 12× Coroa Dourada + Orb      ║  +50×    ║  184×      ║  R$ 9.200 ║
║...║ ...demais giros...           ║  ...     ║  ...       ║  ...      ║
╠═══╩══════════════════════════════╩══════════╩════════════╩═══════════╣
║ NOTA: Multiplicador Global (184×) se aplica a TODOS os wins seguintes ║
║ Teto máximo de ganho: 5.000× a aposta = R$ 5.000,00 (encerra rodada) ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### 4.3 Como o Multiplicador Global se Acumula (ASCII)

```
Início do Free Spin
Mult Global = 1×
        │
        ▼
┌───────────────────┐
│  Giro ocorre      │
└────────┬──────────┘
         │
    Vitória? ──── NÃO ──→ próximo giro (mult NÃO reseta)
         │
        SIM
         │
    Orb caiu? ─── NÃO ──→ Win pago × Mult atual
         │
        SIM
         ▼
  Mult += valor_orb
         │
    Win pago × Mult novo
         │
    Tumble novo?
         │
        SIM → loop (Orbs do mesmo giro continuam somando)
         │
        NÃO → próximo giro (Mult NUNCA reseta até fim do bonus)
```

---

## 5. Features Opcionais

### Ante Bet
- Custo adicional: **+25% por giro**
- Efeito: **dobra a chance** de acionar o Free Spin
- Frequência base de Free Spin: ~1 a cada 448 giros
- Com Ante Bet: ~1 a cada 224 giros
- Indicado para sessões focadas em volume de Free Spins

### Bonus Buy
- Custo: **100× a aposta** (compra imediata das Free Spins)
- Exemplo: aposta R$ 1,00 → Bonus Buy custa R$ 100,00
- Entra diretamente no bonus com 15 giros e Mult Global = 1×

---

## 6. Resumo de Lógica para Implementação

```python
# Pseudocódigo — lógica central do Free Spin
def free_spin_round(bet, n_spins=15):
    global_mult = 1  # nunca reseta durante o bônus
    total_win = 0

    for spin in range(n_spins):
        grid = generate_grid()
        clusters = find_clusters(grid, min_symbols=8)

        while clusters:
            spin_win = 0
            orbs_this_tumble = collect_orbs(grid)

            for cluster in clusters:
                spin_win += paytable[cluster.symbol][len(cluster)] * bet

            global_mult += sum(orbs_this_tumble)   # soma, não multiplica
            total_win += spin_win * global_mult

            grid = remove_clusters_and_tumble(grid, clusters)
            clusters = find_clusters(grid, min_symbols=8)

        # retrigger: 3+ scatters = +5 spins
        if count_scatters(grid) >= 3:
            n_spins += 5

        if total_win >= bet * 5000:  # teto máximo
            break

    return total_win
```

---

## 7. Variantes do Jogo

| Versão                  | Orb máx. | Ganho máx. | Diferença principal          |
|-------------------------|:---------:|:----------:|------------------------------|
| Gates of Olympus (orig) |   500×    |   5.000×   | Versão base — a mais popular |
| Gates of Olympus 1000   |  1.000×   |  15.000×   | Orb maior, max win 3× raro   |
| Gates of Olympus Xmas   |  1.000×   |  15.000×   | Skin natalina do 1000        |
| Gates of Olympus Super Scatter | 500× | 50.000× | Super Scatter especial       |

---

## 8. Referências

- Pragmatic Play — paytable oficial in-game (botão `i`)
- LiveCasinoComparer — paytable detalhado por símbolo
- GalaxyOfSlots — análise matemática do RNG e trigger frequency
- OLBG Slots — paytable por quantidade de símbolos
- EGR Operator Awards 2021 — Game of the Year

> **Aviso:** Gates of Olympus é um jogo de azar com resultados 100% aleatórios (RNG certificado).  
> Proibido para menores de 18 anos. Jogue com responsabilidade.
