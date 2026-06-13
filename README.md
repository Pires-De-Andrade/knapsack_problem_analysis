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
| 1 | Força Bruta          | O(2ⁿ)             | O(n)                 | 🔲     |
| 2 | Backtracking         | O(2ⁿ) pior caso   | O(n)                 | 🔲     |
| 3 | Divisão e Conquista  | O(2ⁿ)             | O(n)                 | 🔲     |
| 4 | Programação Dinâmica | O(n × W)           | O(n × W) / O(W)     | ✅     |
| 5 | Guloso               | O(n log n)         | O(n)                | 🔲     |
| 6 | Heurística FPTAS     | O(n² / ε)         | O(n / ε)             | 🔲     |

## Instalação

```bash
# 1. Criar ambiente virtual (recomendado)
python -m venv venv
venv\Scripts\activate         # Windows
source venv/bin/activate      # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt
```

## Uso Rápido

```bash
# Executar Programação Dinâmica com instância gerada automaticamente
cd src
python main.py --algoritmo prog_dinamica --gerar 15 --seed 42 --exibir-instancia

# Executar com instância salva em JSON
python main.py --algoritmo prog_dinamica --arquivo ../instancias/exemplo.json

# Listar algoritmos disponíveis
python main.py --listar-algoritmos
```

## Testes

```bash
# Executar todos os testes unitários
python -m pytest testes/ -v

# Executar com cobertura (requer pytest-cov)
python -m pytest testes/ -v --cov=src
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
