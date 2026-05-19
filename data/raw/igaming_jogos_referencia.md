# Referência de Jogos iGaming — Gates of Olympus & Fortune Tiger

> Documento de referência técnica e de produto para uso interno.  
> Fontes: pesquisa pública, documentação de fornecedoras, skill interno Gates of Olympus.

---

## 1. Gates of Olympus

| Atributo | Valor |
|---|---|
| **Nome oficial** | Gates of Olympus™ |
| **Apelido BR** | Veio do Raio / Velho do Raio |
| **Desenvolvedora** | Pragmatic Play |
| **Lançamento** | Fevereiro de 2021 |
| **Prêmio** | Game of the Year — EGR Operator Awards 2021 |

### 1.1 Especificações do Jogo

| Atributo | Valor |
|---|---|
| Grid | 6 colunas × 5 linhas (30 posições) |
| Sistema de pagamento | Scatter Pays / Pay Anywhere |
| Mínimo para ganhar | 8 símbolos idênticos |
| RTP padrão | 96,50% |
| Volatilidade | Alta (5/5) |
| Ganho máximo | 5.000× a aposta |
| Wild | Não existe |
| Paylines fixas | Não existem |
| Mecânica de cascata | Sim (Tumble) |
| Multiplicadores base | 2× a 500× (orbs) |
| Frequência Free Spin | ~1 a cada 448 giros |

### 1.2 Paytable Resumida

**Gemas (baixo pagamento)**

| Símbolo | 8–9 | 10–11 | 12–30 |
|---|:---:|:---:|:---:|
| Gema Azul | 0,25× | 0,75× | 2× |
| Gema Verde | 0,40× | 0,90× | 4× |
| Gema Amarela | 0,50× | 1,00× | 5× |
| Gema Roxa | 0,80× | 1,20× | 8× |
| Gema Vermelha | 1,00× | 1,50× | 10× |

**Relíquias (alto pagamento)**

| Símbolo | 8–9 | 10–11 | 12–30 |
|---|:---:|:---:|:---:|
| Taça / Cálice | 1,50× | 2× | 12× |
| Anel | 2,00× | 5× | 15× |
| Ampulheta | 2,50× | 10× | 25× |
| Coroa Dourada | 10,00× | 25× | 50× |

**Scatter (Zeus)**

| Scatters | Pagamento | Ação |
|:---:|:---:|---|
| 4 | 3× | Ativa Free Spins (15 giros) |
| 5 | 5× | Ativa Free Spins (15 giros) |
| 6 | 100× | Ativa Free Spins (15 giros) |

> Retrigger: 3 Scatters durante o Free Spin concedem +5 giros (sem limite de retriggers).

**Orbs Multiplicadores**

Valores possíveis: `2×, 3×, 4×, 5×, 6×, 8×, 10×, 12×, 15×, 20×, 25×, 50×, 100×, 250×, 500×`

- Múltiplos Orbs são **somados** (não multiplicados entre si).
- No jogo base: resetam após cada giro.
- No Free Spin: acumulam em um Multiplicador Global persistente até o fim do bônus.

### 1.3 Features Opcionais

| Feature | Detalhe |
|---|---|
| **Ante Bet** | +25% por giro; dobra a frequência de Free Spin (~1/224 giros) |
| **Bonus Buy** | 100× a aposta; entra direto nas Free Spins com 15 giros |

### 1.4 Variantes

| Versão | Orb máx. | Ganho máx. | Diferença |
|---|:---:|:---:|---|
| Gates of Olympus (original) | 500× | 5.000× | Versão base |
| Gates of Olympus 1000 | 1.000× | 15.000× | Orb e max win maiores |
| Gates of Olympus Xmas 1000 | 1.000× | 15.000× | Skin natalina do 1000 |
| Gates of Olympus Super Scatter | 500× | 50.000× | Super Scatter jackpot |

### 1.5 Compatibilidade Mobile

| Atributo | Valor |
|---|---|
| Tecnologia | HTML5 (responsivo) |
| Orientação | Portrait e Landscape |
| Layout portrait | Zeus acima do grid |
| Layout landscape | Zeus ao lado do grid |
| Canvas estimado | ~720×1280px (portrait) / ~1280×720px (landscape) |
| Scaling | CSS/canvas adaptativo à viewport |
| Assets | Sprites ~2× (retina-ready) |
| Android mínimo | ~5.0 (não publicado oficialmente) |
| iOS mínimo | iOS 12+ (estimado) |
| App dedicado | Não (Pragmatic Play não tem app próprio) |
| Requisitos formais | Nenhum publicado — sem mínimo de hardware declarado |

---

## 2. Fortune Tiger

| Atributo | Valor |
|---|---|
| **Nome oficial** | Fortune Tiger |
| **Apelido BR** | Tigrinho / Jogo do Tigrinho / Jogo do Tigre |
| **Desenvolvedora** | PG Soft (Pocket Games Soft) |
| **Lançamento** | 2022 (janeiro/março) |

### 2.1 Especificações do Jogo

| Atributo | Valor |
|---|---|
| Grid | 3 × 3 (9 posições) |
| Paylines | 5 fixas |
| RTP | 96,81% |
| Volatilidade | Média |
| Ganho máximo | 2.500× a aposta |
| Wild | Sim (Tigre Dourado — substitui todos) |
| Scatter / Free Spins | Não possui |
| Aposta mínima | R$ 0,20 / €0,15 |
| Aposta máxima | R$ 500 / €45–250 (varia por casino) |

### 2.2 Paytable Resumida

| Símbolo | Pagamento (3 iguais) |
|---|:---:|
| Wild (Tigre Dourado) | 50× |
| Envelope Vermelho | até 250× (linha cheia de Wilds) |
| Lingote de Ouro | 20× |
| Amuleto / Lucky Charm | 25× |
| Bolsa de Moedas | 10× |
| Envelope Vermelho (baixo) | 8× |
| Rojões / Firecrackers | 5× |
| Laranja / Mandarina | 3× |

> Nota: nomenclatura dos símbolos pode variar por fonte; o Wild (Tigre) é sempre o mais valioso.

### 2.3 Features

**Multiplicador de Tela Cheia (×10)**
- Ativado quando todos os 9 espaços são preenchidos com símbolos vencedores (incluindo Wilds).
- Multiplica o prêmio total por 10×.
- Máximo via esta feature: até 500× a aposta em um único giro.

**Fortune Tiger Feature (Streak Respins)**
- Ativada aleatoriamente em qualquer giro.
- Um símbolo regular é sorteado; apenas esse símbolo, Wilds ou espaços em branco podem aparecer.
- Novos símbolos do tipo sorteado ou Wilds ficam fixos (sticky) e concedem um respin adicional.
- Continua até não aparecerem novos símbolos ou a tela encher.
- Se a tela encher completamente: ativa o multiplicador ×10.

### 2.4 Compatibilidade Mobile

| Atributo | Valor |
|---|---|
| Tecnologia | HTML5 (Mobile First) |
| Orientação primária | **Portrait (retrato)** |
| Orientação secundária | Landscape suportado |
| Canvas estimado | ~720×1280px (portrait) |
| Scaling | CSS/canvas adaptativo à viewport |
| Assets | Sprites ~2× (retina-ready) |
| Peso no primeiro load | ~18,5 MB |
| Android mínimo | 5.0 (mencionado por terceiros) |
| iOS mínimo | iOS 12+ (estimado) |
| App dedicado | Não (roda direto no browser) |
| Filosofia | "Pocket Games" — projetado para uma mão, botões grandes |

---

## 3. Comparativo Rápido

| | Gates of Olympus | Fortune Tiger |
|---|---|---|
| **Desenvolvedora** | Pragmatic Play | PG Soft |
| **Lançamento** | Fev/2021 | 2022 |
| **Grid** | 6×5 (30 pos.) | 3×3 (9 pos.) |
| **Paylines** | Scatter Pay (qualquer lugar) | 5 fixas |
| **RTP** | 96,50% | 96,81% |
| **Volatilidade** | Alta | Média |
| **Max win** | 5.000× | 2.500× |
| **Wild** | Não | Sim (Tigre) |
| **Free Spins** | Sim (15 giros + retrigger) | Não |
| **Bonus Buy** | Sim (100×) | Não |
| **Ante Bet** | Sim (+25%) | Não |
| **Orientação mobile** | Portrait e Landscape | Portrait (primário) |
| **Tecnologia** | HTML5 | HTML5 |
| **Android mínimo** | ~5.0 (não oficial) | 5.0 (mencionado) |

---

## 4. Notas Técnicas para Integração

- Nenhuma das fornecedoras publica resolução interna do canvas nem requisitos mínimos de hardware de forma oficial. Os dados de resolução são estimados com base na prática de mercado para slots HTML5 mobile-first.
- A resolução real do canvas pode ser inspecionada via DevTools no elemento `<canvas>` com o jogo ativo. O JS abaixo captura os valores em runtime:

```javascript
// Executar no console do DevTools com o jogo carregado
const canvas = document.querySelector('canvas');
if (canvas) {
  console.log(`Canvas interno: ${canvas.width} × ${canvas.height}`);
  console.log(`Canvas CSS: ${canvas.offsetWidth} × ${canvas.offsetHeight}`);
  console.log(`devicePixelRatio: ${window.devicePixelRatio}`);
}
```

- Ambos os jogos são servidos pelos servidores da fornecedora (PG Soft / Pragmatic Play). O operador/casino é apenas a interface de integração via iFrame ou SDK.
- O RNG é certificado por BMM e Gaming Associates (GA) para Fortune Tiger; Pragmatic Play usa certificações equivalentes.

---

*Última atualização: Abril 2026*  
*Fontes: Pragmatic Play (paytable oficial in-game), PG Soft (documentação pública), EGR Operator Awards, pesquisa de mercado.*
