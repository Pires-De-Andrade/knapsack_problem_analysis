"""
Programação Dinâmica para o Problema da Mochila Binária (0/1)
===============================================================

Implementa o algoritmo clássico de Programação Dinâmica bottom-up para
o problema da mochila 0/1, com duas variantes:

1. **Tabela completa O(n × W)**: Constrói a tabela bidimensional dp[i][w]
   e reconstrói a solução (quais itens foram selecionados) por backtracking
   na tabela. Esta é a versão canônica, ideal para fins didáticos.

2. **Espaço otimizado O(W)**: Utiliza apenas duas linhas (ou uma linha
   percorrida de trás para frente) para reduzir o consumo de memória,
   sacrificando a reconstrução trivial dos itens selecionados.

Complexidade (versão tabela completa):
    - Tempo:  O(n × W), onde n é o número de itens e W a capacidade.
    - Espaço: O(n × W) para a tabela dp.

Complexidade (versão espaço otimizado):
    - Tempo:  O(n × W).
    - Espaço: O(W) para o vetor unidimensional.

Referência:
    Cormen, T.H. et al. "Introduction to Algorithms", 3rd Edition,
    Chapter 16 (Dynamic Programming).

Autor: Projeto APA — Problema da Mochila Binária
"""

import time
from typing import Dict, List, Any, Tuple

from instrumentacao import Contador, ResultadoAlgoritmo


def programacao_dinamica(
    pesos: List[int],
    valores: List[int],
    capacidade: int,
    contador: Contador = None,
) -> Tuple[int, List[int], int]:
    """
    Resolve o problema da mochila 0/1 usando Programação Dinâmica (bottom-up)
    com tabela completa O(n × W) e reconstrução dos itens selecionados.

    O algoritmo preenche uma tabela dp[i][w] onde:
      - i varia de 0 a n (linhas: itens considerados)
      - w varia de 0 a W (colunas: capacidade restante)
      - dp[i][w] = valor máximo alcançável usando os itens {0, ..., i-1}
                   com capacidade máxima w.

    A recorrência fundamental é:
      dp[i][w] = max(dp[i-1][w],                         # não incluir item i
                     dp[i-1][w - pesos[i-1]] + valores[i-1])  # incluir item i
      (a segunda opção só é válida se pesos[i-1] <= w)

    Após o preenchimento, a reconstrução dos itens selecionados percorre
    a tabela de dp[n][W] até dp[0][0], verificando se cada item foi incluído.

    Complexidade de tempo:  O(n × W) — preenchimento da tabela.
    Complexidade de espaço: O(n × W) — armazenamento da tabela dp.

    Args:
        pesos: Lista de pesos dos n itens (indexados de 0 a n-1).
        valores: Lista de valores dos n itens (indexados de 0 a n-1).
        capacidade: Capacidade W da mochila (inteiro não-negativo).
        contador: Objeto Contador para instrumentação. Se None, um novo
                  contador é criado internamente.

    Returns:
        Tuple[int, List[int], int]: Tupla contendo:
            - valor_otimo (int): Valor máximo alcançável.
            - itens_selecionados (List[int]): Índices dos itens na solução
              ótima (0-indexed).
            - peso_total (int): Peso total da solução ótima.
    """
    n = len(pesos)

    # Inicializa o contador se não fornecido externamente
    if contador is None:
        contador = Contador()

    # ---------------------------------------------------------------
    # FASE 1: Construção da tabela dp
    # ---------------------------------------------------------------
    # Cria a tabela (n+1) × (capacidade+1) inicializada com zeros.
    # dp[i][w] = melhor valor usando os primeiros i itens com capacidade w.
    dp: List[List[int]] = [
        [0] * (capacidade + 1) for _ in range(n + 1)
    ]

    # Preenchimento bottom-up: para cada item i (de 1 a n)
    for i in range(1, n + 1):
        # Peso e valor do item atual (i-1 no array original, pois dp é 1-indexed)
        peso_item = pesos[i - 1]
        valor_item = valores[i - 1]
        contador.acessos += 2  # Acessos a pesos[i-1] e valores[i-1]

        for w in range(capacidade + 1):
            # Caso base: não incluir o item i — herda o valor da linha anterior
            dp[i][w] = dp[i - 1][w]
            contador.acessos += 2  # Leitura de dp[i-1][w] e escrita em dp[i][w]

            # Verifica se o item i cabe na capacidade w
            contador.comparacoes += 1
            if peso_item <= w:
                # Calcula o valor se incluirmos o item i
                valor_com_item = dp[i - 1][w - peso_item] + valor_item
                contador.acessos += 1  # Leitura de dp[i-1][w - peso_item]
                contador.somas += 1    # Soma: dp[i-1][w-peso] + valor_item

                # Mantém o melhor entre incluir e não incluir
                contador.comparacoes += 1
                if valor_com_item > dp[i][w]:
                    dp[i][w] = valor_com_item
                    contador.acessos += 1  # Escrita em dp[i][w]

    # O valor ótimo está em dp[n][capacidade]
    valor_otimo = dp[n][capacidade]
    contador.acessos += 1  # Leitura do valor ótimo

    # ---------------------------------------------------------------
    # FASE 2: Reconstrução dos itens selecionados (backtracking na tabela)
    # ---------------------------------------------------------------
    # Percorre a tabela de trás para frente, verificando para cada item
    # se ele foi incluído na solução ótima.
    itens_selecionados: List[int] = []
    w = capacidade

    for i in range(n, 0, -1):
        contador.comparacoes += 1  # Comparação dp[i][w] != dp[i-1][w]
        contador.acessos += 2      # Leituras de dp[i][w] e dp[i-1][w]

        # Se dp[i][w] != dp[i-1][w], o item i foi incluído na solução
        if dp[i][w] != dp[i - 1][w]:
            itens_selecionados.append(i - 1)  # Converte para 0-indexed
            w -= pesos[i - 1]                 # Subtrai o peso do item
            contador.somas += 1               # Subtração da capacidade
            contador.acessos += 1             # Acesso a pesos[i-1]

    # Calcula o peso total dos itens selecionados
    peso_total = sum(pesos[i] for i in itens_selecionados)
    contador.somas += len(itens_selecionados)   # Somas para calcular peso total
    contador.acessos += len(itens_selecionados)  # Acessos a pesos[i]

    return valor_otimo, itens_selecionados, peso_total


def programacao_dinamica_espaco_otimizado(
    pesos: List[int],
    valores: List[int],
    capacidade: int,
    contador: Contador = None,
) -> Tuple[int, List[int], int]:
    """
    Resolve o problema da mochila 0/1 usando Programação Dinâmica com
    espaço otimizado O(W), utilizando um único vetor unidimensional.

    O truque é percorrer as capacidades de trás para frente (de W até 0)
    em cada iteração, garantindo que cada item só seja considerado uma vez
    (propriedade 0/1). Isso funciona porque, ao processar w em ordem
    decrescente, o valor dp[w - peso_item] ainda contém o valor da
    iteração anterior (sem o item atual).

    Para reconstruir os itens selecionados, esta versão mantém uma matriz
    de decisão keep[i][w] que registra se o item i foi incluído para a
    capacidade w. Isso consome O(n × W) de memória adicional, mas é
    necessário para a reconstrução.

    NOTA: Se a reconstrução dos itens não for necessária (apenas o valor
    ótimo), a matriz keep pode ser omitida, resultando em O(W) de espaço
    total. Esta versão mantém keep para compatibilidade com a interface
    padronizada.

    Complexidade de tempo:  O(n × W).
    Complexidade de espaço: O(W) para o vetor dp + O(n × W) para keep.

    Args:
        pesos: Lista de pesos dos n itens.
        valores: Lista de valores dos n itens.
        capacidade: Capacidade W da mochila.
        contador: Objeto Contador para instrumentação.

    Returns:
        Tuple[int, List[int], int]: (valor_otimo, itens_selecionados, peso_total).
    """
    n = len(pesos)

    if contador is None:
        contador = Contador()

    # Vetor unidimensional: dp[w] = melhor valor com capacidade w
    dp: List[int] = [0] * (capacidade + 1)

    # Matriz de decisão para reconstrução dos itens
    keep: List[List[bool]] = [
        [False] * (capacidade + 1) for _ in range(n)
    ]

    # Preenchimento: para cada item i
    for i in range(n):
        peso_item = pesos[i]
        valor_item = valores[i]
        contador.acessos += 2  # Acessos a pesos[i] e valores[i]

        # Percorre capacidades de trás para frente (W até peso_item)
        # Isso garante que cada item seja considerado no máximo uma vez
        for w in range(capacidade, peso_item - 1, -1):
            valor_com_item = dp[w - peso_item] + valor_item
            contador.acessos += 1  # Leitura de dp[w - peso_item]
            contador.somas += 1    # Soma para calcular valor_com_item

            contador.comparacoes += 1
            if valor_com_item > dp[w]:
                dp[w] = valor_com_item
                keep[i][w] = True
                contador.acessos += 2  # Escrita em dp[w] e keep[i][w]

    valor_otimo = dp[capacidade]
    contador.acessos += 1

    # ---------------------------------------------------------------
    # Reconstrução dos itens a partir da matriz keep
    # ---------------------------------------------------------------
    itens_selecionados: List[int] = []
    w = capacidade

    for i in range(n - 1, -1, -1):
        contador.acessos += 1       # Leitura de keep[i][w]
        contador.comparacoes += 1   # Verificação if keep[i][w]

        if keep[i][w]:
            itens_selecionados.append(i)
            w -= pesos[i]
            contador.somas += 1    # Subtração da capacidade
            contador.acessos += 1  # Acesso a pesos[i]

    # Calcula o peso total
    peso_total = sum(pesos[i] for i in itens_selecionados)
    contador.somas += len(itens_selecionados)
    contador.acessos += len(itens_selecionados)

    return valor_otimo, itens_selecionados, peso_total


def executar_programacao_dinamica(
    instancia: Dict[str, Any],
    versao: str = "tabela",
    repeticoes_tempo: int = 1,
) -> ResultadoAlgoritmo:
    """
    Função de alto nível que executa a Programação Dinâmica sobre uma instância
    do problema da mochila e retorna o resultado padronizado.

    Integra a lógica do algoritmo com a instrumentação de tempo e contagem
    de instruções, retornando um `ResultadoAlgoritmo` completo.

    Args:
        instancia: Dicionário com os dados da instância (campos 'pesos',
                   'valores', 'capacidade').
        versao: Variante a executar:
                - "tabela": Tabela completa O(n × W) (padrão).
                - "otimizada": Espaço otimizado O(W).
        repeticoes_tempo: Número de repetições para medição de tempo.

    Returns:
        ResultadoAlgoritmo: Resultado padronizado com valor, itens,
                            contagem de instruções e tempo.

    Raises:
        ValueError: Se a versão especificada for inválida.
    """
    pesos = instancia["pesos"]
    valores = instancia["valores"]
    capacidade = instancia["capacidade"]

    # Seleciona a variante do algoritmo
    if versao == "tabela":
        funcao_algoritmo = programacao_dinamica
        nome = "Programação Dinâmica (tabela O(n×W))"
    elif versao == "otimizada":
        funcao_algoritmo = programacao_dinamica_espaco_otimizado
        nome = "Programação Dinâmica (espaço O(W))"
    else:
        raise ValueError(f"Versão desconhecida: '{versao}'. Use 'tabela' ou 'otimizada'.")

    # Cria o contador de instruções
    contador = Contador()

    # Mede o tempo de execução
    inicio = time.perf_counter()
    valor_otimo, itens_selecionados, peso_total = funcao_algoritmo(
        pesos, valores, capacidade, contador
    )
    fim = time.perf_counter()
    tempo_execucao = fim - inicio

    # Se pedido mais repetições, refaz apenas para tempo (sem recontar instruções)
    if repeticoes_tempo > 1:
        tempos = [tempo_execucao]
        for _ in range(repeticoes_tempo - 1):
            inicio = time.perf_counter()
            funcao_algoritmo(pesos, valores, capacidade)
            fim = time.perf_counter()
            tempos.append(fim - inicio)

        import statistics
        tempo_execucao = statistics.mean(tempos)

    # Monta e retorna o resultado padronizado
    resultado = ResultadoAlgoritmo(
        valor=valor_otimo,
        itens_selecionados=itens_selecionados,
        contador=contador,
        tempo_execucao=tempo_execucao,
        nome_algoritmo=nome,
        peso_total=peso_total,
    )

    return resultado


# ---------------------------------------------------------------------------
# Execução direta para testes rápidos
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Exemplo didático: mochila com 4 itens
    # Item 0: peso=2, valor=3
    # Item 1: peso=3, valor=4
    # Item 2: peso=4, valor=5
    # Item 3: peso=5, valor=6
    # Capacidade: 8
    # Solução ótima: itens {1, 3} ou {0, 2, 3} com valor ótimo = 11

    instancia_teste = {
        "n": 4,
        "capacidade": 8,
        "pesos": [2, 3, 4, 5],
        "valores": [3, 4, 5, 6],
    }

    print("=" * 60)
    print("TESTE: Programação Dinâmica — Tabela Completa O(n×W)")
    print("=" * 60)
    resultado_tabela = executar_programacao_dinamica(instancia_teste, versao="tabela")
    print(resultado_tabela)

    print("=" * 60)
    print("TESTE: Programação Dinâmica — Espaço Otimizado O(W)")
    print("=" * 60)
    resultado_otim = executar_programacao_dinamica(instancia_teste, versao="otimizada")
    print(resultado_otim)

    # Verificação: ambas as versões devem encontrar o mesmo valor ótimo
    assert resultado_tabela.valor == resultado_otim.valor, (
        f"ERRO: Valores diferentes! Tabela={resultado_tabela.valor}, "
        f"Otimizada={resultado_otim.valor}"
    )
    print("[OK] Ambas as versoes encontraram o mesmo valor otimo.")
