"""
Algoritmo Guloso para o Problema da Mochila Binaria (0/1)
===========================================================

Implementa a heuristica gulosa baseada na ordenacao dos itens pela
razao valor/peso em ordem decrescente.

Logica:
    1. Calcula a razao v_i / p_i para cada item.
    2. Ordena os itens de forma decrescente por essa razao.
    3. Percorre a lista ordenada e inclui o item na mochila se o seu
       peso for menor ou igual a capacidade restante.

POR QUE O GULOSO NAO E OTIMO PARA A MOCHILA 0/1?
------------------------------------------------
Diferente da Mochila Fracionaria (onde podemos quebrar itens), na
Mochila 0/1 um item de altissima razao valor/peso pode ocupar quase
toda a capacidade, impedindo a entrada de multiplos outros itens que,
somados, teriam um valor maior.

Exemplo concreto de falha do Guloso:
    Capacidade W = 10
    Item 0: valor = 8, peso = 6  (Razao = 1.33)
    Item 1: valor = 5, peso = 5  (Razao = 1.00)
    Item 2: valor = 5, peso = 5  (Razao = 1.00)

    Execucao do Guloso:
        1. Ordena pela razao: [Item 0, Item 1, Item 2]
        2. Analisa Item 0 (peso 6 <= 10): INCLUI. Restam W = 4.
        3. Analisa Item 1 (peso 5 > 4): NAO CABE.
        4. Analisa Item 2 (peso 5 > 4): NAO CABE.
        Valor Total Guloso = 8.

    Solucao Otima Real:
        Incluir Item 1 e Item 2.
        Peso total = 10 <= 10.
        Valor Total = 10.

    Conclusao: O Guloso obteve 8, enquanto o otimo e 10.

A grande vantagem do Guloso e a sua escalabilidade extrema. Diferente
dos algoritmos exatos que sofrem com complexidade exponencial (Forca
Bruta, D&C, Backtracking) ou dependem pseudopolinomialmente da capacidade
(Programacao Dinamica), o Guloso roda em fracoes de segundo ate para
milhoes de itens. Por isso, nao e necessario um N_MAXIMO_RECOMENDADO.

Complexidade:
    - Tempo:  O(n log n) — dominado pela ordenacao inicial dos itens.
              A passagem pela lista custa apenas O(n).
    - Espaco: O(n) — para armazenar a lista ordenada de tuplas com
              as razoes.

Referencia:
    Cormen, T.H. et al. "Introduction to Algorithms", 3rd Edition,
    Secao 16.2 (Elements of the greedy strategy).

Autor: Projeto APA — Problema da Mochila Binaria
"""

import time
import math
from typing import Dict, List, Any, Tuple

from instrumentacao import Contador, ResultadoAlgoritmo


def guloso(
    pesos: List[int],
    valores: List[int],
    capacidade: int,
    contador: Contador = None,
) -> Tuple[int, List[int], int]:
    """
    Resolve a mochila 0/1 de forma heuristica usando a estrategia
    gulosa por razao valor/peso. Nao garante solucao otima.

    Args:
        pesos: Lista de pesos dos n itens.
        valores: Lista de valores dos n itens.
        capacidade: Capacidade W da mochila.
        contador: Objeto Contador para instrumentacao.

    Returns:
        Tuple[int, List[int], int]: Tupla contendo:
            - valor_total (int): Valor alcancado (subotimo na maioria das vezes).
            - itens_selecionados (List[int]): Indices dos itens escolhidos.
            - peso_total (int): Peso total da solucao gulosa.
    """
    n = len(pesos)

    if contador is None:
        contador = Contador()

    if n == 0:
        return 0, [], 0

    # 1. Calcula a razao e guarda o indice original
    # Custo: O(n)
    razoes = []
    for i in range(n):
        contador.acessos += 2
        # Evita divisao por zero. Se peso for 0 e valor > 0, razao e infinita
        if pesos[i] == 0:
            razao = float('inf') if valores[i] > 0 else 0.0
        else:
            razao = valores[i] / pesos[i]
        
        razoes.append((razao, i))
        contador.somas += 1 # Conta a divisao como operacao

    # 2. Ordena os itens por razao em ordem decrescente
    # Custo de ordenacao O(n log n). Vamos instrumentar uma estimativa do custo
    # no contador para refletir a complexidade teorica.
    comparacoes_sort = int(n * math.log2(n) if n > 0 else 0)
    contador.comparacoes += comparacoes_sort
    razoes.sort(reverse=True, key=lambda x: x[0])

    valor_total = 0
    peso_total = 0
    itens_selecionados = []
    cap_restante = capacidade

    # 3. Percorre a lista gulosa
    for _, idx_original in razoes:
        peso_item = pesos[idx_original]
        valor_item = valores[idx_original]
        contador.acessos += 2

        contador.comparacoes += 1
        if peso_item <= cap_restante:
            # Inclui o item
            itens_selecionados.append(idx_original)
            valor_total += valor_item
            peso_total += peso_item
            cap_restante -= peso_item
            contador.somas += 3

    return valor_total, itens_selecionados, peso_total


def executar_guloso(
    instancia: Dict[str, Any],
    repeticoes_tempo: int = 1,
) -> ResultadoAlgoritmo:
    """
    Funcao de alto nivel que executa o Algoritmo Guloso.
    """
    pesos = instancia["pesos"]
    valores = instancia["valores"]
    capacidade = instancia["capacidade"]

    nome = "Algoritmo Guloso (Razao v/p)"
    contador = Contador()

    inicio = time.perf_counter()
    valor_otimo, itens_selecionados, peso_total = guloso(
        pesos, valores, capacidade, contador
    )
    fim = time.perf_counter()
    tempo_execucao = fim - inicio

    if repeticoes_tempo > 1:
        tempos = [tempo_execucao]
        for _ in range(repeticoes_tempo - 1):
            inicio = time.perf_counter()
            guloso(pesos, valores, capacidade)
            fim = time.perf_counter()
            tempos.append(fim - inicio)

        import statistics
        tempo_execucao = statistics.mean(tempos)

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
    # Teste com a instancia falha do docstring
    instancia_falha = {
        "n": 3,
        "capacidade": 10,
        "pesos": [6, 5, 5],
        "valores": [8, 5, 5],
    }

    print("=" * 60)
    print("TESTE: Instancia Falha do Guloso (W=10)")
    print("=" * 60)
    resultado = executar_guloso(instancia_falha)
    print(resultado)
    print("Conclusao: Guloso encontrou valor 8. Otimo real e 10 (itens 1 e 2).")
