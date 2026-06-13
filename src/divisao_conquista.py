"""
Divisao e Conquista para o Problema da Mochila Binaria (0/1)
==============================================================

Implementa a solucao por Divisao e Conquista (Divide and Conquer) usando
a recorrencia classica "incluir item i / nao incluir item i", sem nenhuma
memoizacao e sem nenhuma poda.

Relacao com os demais paradigmas — o "elo" conceitual:
------------------------------------------------------

Este algoritmo ocupa uma posicao central na progressao didatica dos
paradigmas de projeto de algoritmos para a mochila 0/1:

    Forca Bruta  →  Divisao e Conquista  →  Programacao Dinamica
    (sem estrutura     (recorrencia de         (mesma recorrencia,
     de subproblemas)   subproblemas,           mas COM memoizacao
                        SEM memoizacao)         na tabela dp[i][w])

  - **Forca Bruta**: enumera TODOS os 2^n subconjuntos de forma
    iterativa (representacao binaria). Nao ha nocao de subproblemas
    nem recorrencia; a avaliacao de cada subconjunto e independente.

  - **Divisao e Conquista** (este modulo): formula o problema como
    recorrencia sobre subproblemas: dado o item i e a capacidade
    restante w, o valor otimo e:

        T(i, w) = max(T(i+1, w),                       # nao incluir
                      T(i+1, w - peso[i]) + valor[i])   # incluir

    O problema e "dividido" em dois subproblemas menores (T(i+1, ...))
    e "combinado" tomando o maximo. Porem, sem memoizacao, muitos
    subproblemas sao recalculados, resultando em O(2^n) — a mesma
    complexidade da Forca Bruta.

  - **Backtracking**: usa a MESMA arvore de decisao, mas aplica podas
    (viabilidade e bound) para evitar explorar ramos improdutivos.
    Corta subarvores inteiras, reduzindo drasticamente o numero de
    nos visitados na pratica.

  - **Programacao Dinamica**: usa a MESMA recorrencia, mas armazena
    os resultados de subproblemas ja resolvidos na tabela dp[i][w],
    evitando recalculos. Isso reduz a complexidade para O(n * W).

Essa progressao evidencia como a mesma recorrencia, com diferentes
estrategias (sem reuso → com podas → com memoizacao), leva a
desempenhos drasticamente diferentes.

Complexidade:
    - Tempo:  O(2^n) — cada item gera duas chamadas recursivas, e nao
              ha reuso de subproblemas. A arvore de recursao tem
              profundidade n e ate 2^n folhas.
    - Espaco: O(n) — profundidade maxima da pilha de recursao.

Referencia:
    Cormen, T.H. et al. "Introduction to Algorithms", 3rd Edition,
    Secao 15.1 (Rod cutting) para a motivacao de por que D&C sem
    memoizacao e ineficiente e leva naturalmente a DP.

Autor: Projeto APA — Problema da Mochila Binaria
"""

import time
import warnings
from typing import Dict, List, Any, Tuple

from instrumentacao import Contador, ResultadoAlgoritmo


# ---------------------------------------------------------------------------
# Constante de limite pratico
# ---------------------------------------------------------------------------

# Valor maximo de n recomendado para Divisao e Conquista.
# Similar ao da Forca Bruta (22), pois ambos exploram O(2^n) subproblemas
# sem nenhuma poda. Na pratica, D&C pode ser ligeiramente mais lento que
# a Forca Bruta iterativa devido ao overhead de chamadas recursivas, mas
# a diferenca e pequena. Usamos o mesmo limite de 22 por consistencia.
N_MAXIMO_RECOMENDADO: int = 22


def mochila_dc(
    pesos: List[int],
    valores: List[int],
    capacidade: int,
    indice: int,
    contador: Contador,
) -> Tuple[int, List[int]]:
    """
    Resolve recursivamente o subproblema da mochila 0/1 usando Divisao
    e Conquista, considerando os itens de `indice` ate n-1 com a
    capacidade dada.

    A recorrencia e:
        T(i, w) = max(T(i+1, w),                       # nao incluir item i
                      T(i+1, w - peso[i]) + valor[i])   # incluir item i

    O "dividir" consiste em decompor o problema em dois subproblemas
    independentes (incluir ou nao o item atual), cada um com um item
    a menos (indice+1). O "conquistar" e resolver cada subproblema
    recursivamente. O "combinar" e escolher o maximo entre as duas
    opcoes.

    Decisao de design — reconstrucao dos itens:
        Optou-se por retornar a lista de itens selecionados junto com
        o valor otimo durante a propria recursao (em vez de uma segunda
        passada reconstrutiva). Justificativa:
        1. E mais didatico: o "combina" fica explicito — ao tomar o
           maximo, ja sabemos quais itens compoem a melhor solucao.
        2. Evita uma segunda passada recursiva O(2^n), que dobraria
           o tempo de execucao.
        3. O custo adicional e apenas O(n) por nivel de recursao para
           copiar a lista de itens (dominado pelo O(2^n) total).

    Complexidade de tempo:  O(2^n) — a arvore de recursao bifurca em
                            cada nivel, gerando ate 2^n chamadas.
    Complexidade de espaco: O(n) para a pilha de recursao (profundidade
                            maxima n), mais O(n) para as listas de itens
                            em cada nivel.

    Args:
        pesos: Lista de pesos dos n itens.
        valores: Lista de valores dos n itens.
        capacidade: Capacidade restante da mochila neste subproblema.
        indice: Indice do item atual sendo decidido (0 a n-1).
        contador: Objeto Contador para instrumentacao.

    Returns:
        Tuple[int, List[int]]: Tupla contendo:
            - valor_otimo (int): Valor maximo alcancavel para este
              subproblema.
            - itens_selecionados (List[int]): Indices dos itens
              selecionados neste subproblema (0-indexed).
    """
    n = len(pesos)

    # Contabiliza cada chamada recursiva como uma instrucao
    contador.acessos += 1  # Acesso ao no da arvore de recursao

    # ---------------------------------------------------------------
    # CASO BASE: nao ha mais itens a considerar
    # ---------------------------------------------------------------
    contador.comparacoes += 1
    if indice == n:
        return 0, []

    # ---------------------------------------------------------------
    # CASO: item atual nao cabe na capacidade restante
    # ---------------------------------------------------------------
    # Se peso[indice] > capacidade, so podemos "nao incluir" o item.
    # Nao ha ramificacao — apenas uma chamada recursiva.
    contador.acessos += 1     # Acesso a pesos[indice]
    contador.comparacoes += 1  # Comparacao peso > capacidade
    if pesos[indice] > capacidade:
        # So existe o ramo "nao incluir item indice"
        return mochila_dc(pesos, valores, capacidade, indice + 1, contador)

    # ---------------------------------------------------------------
    # DIVIDIR: decompor em dois subproblemas
    # ---------------------------------------------------------------

    # Subproblema 1 — NAO incluir o item `indice`:
    # Resolve T(indice+1, capacidade) — mesma capacidade, proximo item
    valor_sem, itens_sem = mochila_dc(
        pesos, valores, capacidade, indice + 1, contador
    )

    # Subproblema 2 — INCLUIR o item `indice`:
    # Resolve T(indice+1, capacidade - peso[indice]) — capacidade reduzida
    valor_com_item, itens_com = mochila_dc(
        pesos, valores, capacidade - pesos[indice], indice + 1, contador
    )
    # Adiciona o valor do item atual ao resultado do subproblema
    valor_com = valor_com_item + valores[indice]
    contador.acessos += 2  # Acessos a pesos[indice] e valores[indice]
    contador.somas += 1    # Soma do valor do item ao subproblema

    # ---------------------------------------------------------------
    # COMBINAR: escolher o melhor entre incluir e nao incluir
    # ---------------------------------------------------------------
    contador.comparacoes += 1  # Comparacao no "combina" (max)
    if valor_com > valor_sem:
        # Incluir o item `indice` e a melhor opcao
        return valor_com, itens_com + [indice]
    else:
        # Nao incluir o item `indice` e a melhor opcao
        return valor_sem, itens_sem


def divisao_conquista(
    pesos: List[int],
    valores: List[int],
    capacidade: int,
    contador: Contador = None,
) -> Tuple[int, List[int], int]:
    """
    Wrapper principal que resolve o problema da mochila 0/1 por Divisao
    e Conquista, delegando a funcao recursiva `mochila_dc`.

    Esta funcao cuida da inicializacao do contador, validacao do tamanho
    da entrada, e calculo do peso total dos itens selecionados.

    Complexidade de tempo:  O(2^n).
    Complexidade de espaco: O(n) para a pilha de recursao.

    Args:
        pesos: Lista de pesos dos n itens (indexados de 0 a n-1).
        valores: Lista de valores dos n itens (indexados de 0 a n-1).
        capacidade: Capacidade W da mochila (inteiro nao-negativo).
        contador: Objeto Contador para instrumentacao. Se None, um novo
                  contador e criado internamente.

    Returns:
        Tuple[int, List[int], int]: Tupla contendo:
            - valor_otimo (int): Valor maximo alcancavel.
            - itens_selecionados (List[int]): Indices dos itens na solucao
              otima (0-indexed).
            - peso_total (int): Peso total da solucao otima.
    """
    n = len(pesos)

    # Inicializa o contador se nao fornecido externamente
    if contador is None:
        contador = Contador()

    # Emite warning se n excede o limite recomendado
    if n > N_MAXIMO_RECOMENDADO:
        warnings.warn(
            f"Divisao e Conquista chamada com n={n}, que excede o limite "
            f"recomendado de {N_MAXIMO_RECOMENDADO}. Sem memoizacao, a "
            f"complexidade e O(2^{n}) = {2**n:,} chamadas recursivas, "
            f"equivalente a Forca Bruta.",
            RuntimeWarning,
            stacklevel=2,
        )

    # Inicia a recursao a partir do item 0 com capacidade total
    valor_otimo, itens_selecionados = mochila_dc(
        pesos, valores, capacidade, 0, contador
    )

    # Calcula o peso total dos itens selecionados
    peso_total = sum(pesos[i] for i in itens_selecionados)
    contador.somas += len(itens_selecionados)   # Somas para peso total
    contador.acessos += len(itens_selecionados)  # Acessos a pesos[i]

    return valor_otimo, itens_selecionados, peso_total


def executar_divisao_conquista(
    instancia: Dict[str, Any],
    repeticoes_tempo: int = 1,
) -> ResultadoAlgoritmo:
    """
    Funcao de alto nivel que executa Divisao e Conquista sobre uma instancia
    do problema da mochila e retorna o resultado padronizado.

    Integra a logica do algoritmo com a instrumentacao de tempo e contagem
    de instrucoes, retornando um `ResultadoAlgoritmo` completo.

    Args:
        instancia: Dicionario com os dados da instancia (campos 'pesos',
                   'valores', 'capacidade').
        repeticoes_tempo: Numero de repeticoes para medicao de tempo.

    Returns:
        ResultadoAlgoritmo: Resultado padronizado com valor, itens,
                            contagem de instrucoes e tempo.
    """
    pesos = instancia["pesos"]
    valores = instancia["valores"]
    capacidade = instancia["capacidade"]

    nome = "Divisao e Conquista (sem memoizacao)"

    # Cria o contador de instrucoes
    contador = Contador()

    # Mede o tempo de execucao
    inicio = time.perf_counter()
    valor_otimo, itens_selecionados, peso_total = divisao_conquista(
        pesos, valores, capacidade, contador
    )
    fim = time.perf_counter()
    tempo_execucao = fim - inicio

    # Se pedido mais repeticoes, refaz apenas para tempo (sem recontar instrucoes)
    if repeticoes_tempo > 1:
        tempos = [tempo_execucao]
        for _ in range(repeticoes_tempo - 1):
            inicio = time.perf_counter()
            divisao_conquista(pesos, valores, capacidade)
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
# Execucao direta para testes rapidos
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from gerador_instancias import gerar_instancia, imprimir_instancia

    # Exemplo didatico com instancia pequena
    instancia_teste = {
        "n": 4,
        "capacidade": 8,
        "pesos": [2, 3, 4, 5],
        "valores": [3, 4, 5, 6],
    }

    print("=" * 60)
    print("TESTE: Divisao e Conquista (recorrencia sem memoizacao)")
    print("=" * 60)
    resultado = executar_divisao_conquista(instancia_teste)
    print(resultado)

    # Comparacao com os demais algoritmos na mesma instancia
    print("\n" + "=" * 60)
    print("COMPARACAO: 4 algoritmos exatos (n=15, seed=42)")
    print("=" * 60)
    inst = gerar_instancia(n=15, seed=42)

    from forca_bruta import executar_forca_bruta
    from backtracking import executar_backtracking
    from prog_dinamica import executar_programacao_dinamica

    resultados = [
        executar_programacao_dinamica(inst),
        executar_forca_bruta(inst),
        resultado_bt := executar_backtracking(inst),
        executar_divisao_conquista(inst),
    ]

    print(f"{'Algoritmo':<40} {'Valor':>8} {'Instrucoes':>14} {'Tempo (s)':>12}")
    print("-" * 76)
    for r in resultados:
        print(f"{r.nome_algoritmo:<40} {r.valor:>8} {r.num_instrucoes:>14,} {r.tempo_execucao:>12.6f}")

    # Verificacao: todos devem encontrar o mesmo valor
    valores_unicos = set(r.valor for r in resultados)
    assert len(valores_unicos) == 1, f"Valores divergentes: {valores_unicos}"
    print(f"\n[OK] Todos os 4 algoritmos encontraram valor otimo = {resultados[0].valor}")
