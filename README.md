# Mochila Binária (0/1 Knapsack Problem)

**Trabalho Acadêmico — Análise e Projeto de Algoritmos (APA)**

Implementação do problema da mochila binária (0/1 Knapsack) utilizando 6 estratégias
de projeto de algoritmos, com instrumentação para análise de complexidade prática
(contagem de instruções e medição de tempo de execução).

---

## Estrutura do Projeto

```
mochila_binaria/
├── src/                           # Código-fonte dos algoritmos
│   ├── instrumentacao.py          # Contador de instruções e medição de tempo
│   ├── gerador_instancias.py      # Gerador de instâncias aleatórias (com seed)
│   ├── prog_dinamica.py           # Programação Dinâmica (tabela + espaço otimizado)
│   ├── forca_bruta.py             # Força Bruta (todos os 2^n subconjuntos)
│   ├── backtracking.py            # Backtracking (com podas)
│   ├── divisao_conquista.py       # Divisão e Conquista (recursão sem memoização)
│   ├── guloso.py                  # Guloso (razão valor/peso)
│   ├── heuristica.py              # Heurística FPTAS (escalonamento de valores)
│   └── main.py                    # CLI para execução individual
├── instancias/                    # Instâncias de teste (JSON)
├── resultados/
│   ├── csv/                       # Resultados numéricos em CSV
│   └── graficos/                  # Gráficos comparativos (PNG)
├── analise.py                     # Script de análise comparativa
├── testes/
│   └── test_algoritmos.py         # Testes unitários
├── requirements.txt               # Dependências Python
└── README.md                      # Este arquivo
```

## Algoritmos Implementados

| # | Estratégia           | Complexidade Tempo | Complexidade Espaço | Status |
|---|----------------------|--------------------|---------------------|--------|
| 1 | Força Bruta          | O(2ⁿ)             | O(n)                 | ✅     |
| 2 | Backtracking         | O(2ⁿ) pior caso   | O(n)                 | ✅     |
| 3 | Divisão e Conquista  | O(2ⁿ)             | O(n)                 | ✅     |
| 4 | Programação Dinâmica | O(n × W)           | O(n × W) / O(W)     | ✅     |
| 5 | Guloso               | O(n log n)         | O(n)                | ✅     |
| 6 | Heurística FPTAS     | O(n² / ε)         | O(n / ε)             | ✅     |

## Instalação

```bash
# 1. Criar ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate         # Windows
source venv/bin/activate      # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt
```

## 1. Executar os Testes Automatizados

A suíte de testes (141 testes) garante que as 6 implementações estão corretas e valida as garantias teóricas (como o gap máximo do FPTAS e a subotimalidade do Guloso).

```bash
# Executar todos os testes unitários formatados de forma limpa
python -m pytest testes/test_algoritmos.py -v --tb=short
```

## 2. Executar a Análise de Resultados (CSV e Gráficos)

O script `analise.py` roda os três experimentos detalhados na sua documentação acadêmica (Escalabilidade, Qualidade/Gap e Eficácia da Poda) e salva os dados brutos e os gráficos.

```bash
# Executar a rotina completa
python src/analise.py

# Pular os experimentos (demorados) e apenas regerar os gráficos a partir dos CSVs
python src/analise.py --skip-exp
```
Os CSVs são salvos em `resultados/csv/` e os gráficos em `resultados/graficos/`.

## 3. Interface de Linha de Comando Rápida (CLI)

O arquivo `main.py` permite que você teste instâncias específicas e algoritmos avulsos rapidamente pelo terminal.

```bash
# Listar algoritmos disponíveis
python src/main.py --listar-algoritmos

# Exemplo: Rodar Programação Dinâmica
python src/main.py -a prog_dinamica -g 15 -s 42

# Exemplo: Rodar Guloso, exibindo a instância detalhada gerada
python src/main.py -a guloso -g 15 -s 42 --exibir-instancia

# Exemplo: Rodar Heurística FPTAS passando o parâmetro de erro epsilon
python src/main.py -a heuristica -g 15 -s 42 --epsilon 0.5
```

## Instrumentação

Cada algoritmo registra automaticamente:
- **Contagem de instruções**: comparações, somas/operações aritméticas, acessos a
  estruturas de dados
- **Tempo de execução**: medido com `time.perf_counter()`, com suporte a múltiplas
  repetições para cálculo de média

O módulo `instrumentacao.py` fornece:
- `Contador`: classe para contagem de operações por categoria
- `ResultadoAlgoritmo`: estrutura padronizada de retorno de todos os algoritmos
- `medir_tempo()`: função para medição precisa com repetições

## Formato das Instâncias (JSON)

```json
{
  "n": 10,
  "capacidade": 250,
  "pesos": [23, 45, 12, ...],
  "valores": [67, 34, 89, ...],
  "seed": 42,
  "fracao_capacidade": 0.5
}
```

---
**Linguagem**: Python 3.10+  
**Licença**: Uso acadêmico
