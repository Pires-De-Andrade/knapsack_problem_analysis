"""
Heuristica FPTAS para o Problema da Mochila Binaria (0/1)
===========================================================

Implementa um FPTAS (Fully Polynomial-Time Approximation Scheme) usando
escalonamento de valores, de acordo com o algoritmo classico de Vazirani.

Garantia Teorica:
-----------------
Dado um parametro de erro epsilon (ε) onde 0 < ε < 1, o FPTAS garante
que o valor da solucao retornada (V_fptas) sera no minimo:
    V_fptas >= (1 - ε) * V_otimo
Isso em tempo polinomial tanto em n quanto em 1/ε.

Funcionamento:
--------------
1. Seja max_v o maior valor entre os itens.
2. Definimos um fator de escala K = (ε * max_v) / n.
3. Para cada item i, criamos um valor escalonado: v'_i = floor(v_i / K).
4. Resolvemos o problema usando Programacao Dinamica, mas sobre os
   VALORES ESCALONADOS em vez dos pesos.
5. Retornamos os itens encontrados e o seu valor real original.

Por que nao reusamos prog_dinamica.py?
--------------------------------------
O modulo `prog_dinamica.py` implementa uma DP orientada a CAPACIDADE,
cuja tabela e dp[i][w] = "valor maximo alcancavel com peso ate w".
O FPTAS requer uma DP orientada a VALOR, cuja tabela e:
dp[i][v] = "PESO MINIMO para alcancar exatemente o valor v".
As dimensoes da tabela, o significado das celulas, o caso base
(dp[0] = 0, resto infinito) e a funcao de transicao (min em vez de max)
sao diferentes, exigindo uma implementacao dedicada.

Complexidade:
    - Tempo:  O(n^3 / ε) — o valor escalonado maximo e n/ε, a tabela
              de DP tem tamanho O(n^2 / ε).
    - Espaco: O(n^2 / ε) — para rastrear os itens selecionados na
              tabela de DP (otimizada para 1D para os pesos).

Referencia:
    Vazirani, V.V. "Approximation Algorithms", Springer.
    Secao 8.1 (Knapsack).

Autor: Projeto APA — Problema da Mochila Binaria
"""

import time
import math
from typing import Dict, List, Any, Tuple

from instrumentacao import Contador, ResultadoAlgoritmo


def fptas(
    pesos: List[int],
    valores: List[int],
    capacidade: int,
    epsilon: float = 0.1,
    contador: Contador = None,
) -> Tuple[int, List[int], int, float, int]:
    """
    Resolve o problema da mochila 0/1 com FPTAS garantindo solucao de
    pelo menos (1 - epsilon) vezes o otimo.

    Args:
        pesos: Lista de pesos.
        valores: Lista de valores.
        capacidade: Capacidade W da mochila.
        epsilon: Parametro de aproximacao (0 < epsilon < 1).
        contador: Objeto Contador para instrumentacao.

    Returns:
        Tuple[int, List[int], int, float, int]:
            - valor_real (int): Valor dos itens na instancia original.
            - itens_selecionados (List[int]): Indices escolhidos.
            - peso_total (int): Peso real dos itens escolhidos.
            - epsilon_usado (float): O parametro epsilon.
            - k_fator (int/float): O fator K usado no escalonamento.
    """
    n = len(pesos)
    if contador is None:
        contador = Contador()

    if n == 0 or epsilon <= 0 or epsilon >= 1:
        return 0, [], 0, epsilon, 1.0

    # 1. Encontra valor maximo
    max_v = max(valores)
    contador.comparacoes += n

    if max_v == 0:
        return 0, [], 0, epsilon, 1.0

    # 2. Calcula fator de escala K
    # K = (epsilon * max_v) / n
    K = (epsilon * max_v) / n
    if K <= 0:
        K = 1e-9  # Seguranca para evitar divisao por zero

    contador.somas += 2 # Multiplicacao e divisao

    # 3. Escalonamento dos valores
    valores_escalonados = [math.floor(v / K) for v in valores]
    contador.somas += n # Divisoes e floors
    contador.acessos += n

    # 4. Programacao Dinamica orientada a Valores
    # Soma maxima dos valores escalonados limita o tamanho da tabela
    V_max = sum(valores_escalonados)
    
    # dp_peso[v] armazenara o peso minimo para atingir EXATAMENTE
    # o valor escalonado v.
    dp_peso = [float('inf')] * (V_max + 1)
    dp_peso[0] = 0

    # rastreio[i][v] = booleano indicando se o item i foi usado
    # para compor o peso minimo do valor v. Usado para reconstruir a solucao.
    rastreio = [[False] * (V_max + 1) for _ in range(n)]

    # Preenche a tabela
    for i in range(n):
        v_i = valores_escalonados[i]
        p_i = pesos[i]
        contador.acessos += 2

        # Itera de tras para frente para simular a tabela 2D usando 1D
        for v in range(V_max, v_i - 1, -1):
            contador.comparacoes += 1
            if dp_peso[v - v_i] + p_i < dp_peso[v]:
                dp_peso[v] = dp_peso[v - v_i] + p_i
                rastreio[i][v] = True
                contador.somas += 1

    # 5. Encontra o maior valor escalonado cujo peso caiba na mochila
    melhor_v_escalonado = 0
    for v in range(V_max, -1, -1):
        contador.comparacoes += 1
        if dp_peso[v] <= capacidade:
            melhor_v_escalonado = v
            break

    # 6. Reconstrucao da solucao
    itens_selecionados = []
    v_atual = melhor_v_escalonado
    for i in range(n - 1, -1, -1):
        if rastreio[i][v_atual]:
            itens_selecionados.append(i)
            v_atual -= valores_escalonados[i]
            
    itens_selecionados.reverse()

    # 7. Valores reais
    valor_real = sum(valores[i] for i in itens_selecionados)
    peso_real = sum(pesos[i] for i in itens_selecionados)
    contador.somas += len(itens_selecionados) * 2
    contador.acessos += len(itens_selecionados) * 2

    return valor_real, itens_selecionados, peso_real, epsilon, K


def executar_heuristica_fptas(
    instancia: Dict[str, Any],
    repeticoes_tempo: int = 1,
    epsilon: float = 0.1,
) -> ResultadoAlgoritmo:
    """
    Funcao de alto nivel para rodar o FPTAS.
    """
    pesos = instancia["pesos"]
    valores = instancia["valores"]
    capacidade = instancia["capacidade"]

    nome = f"FPTAS (eps={epsilon})"
    contador = Contador()

    inicio = time.perf_counter()
    valor_real, itens, peso_total, eps_usado, K_usado = fptas(
        pesos, valores, capacidade, epsilon, contador
    )
    fim = time.perf_counter()
    tempo_execucao = fim - inicio

    if repeticoes_tempo > 1:
        tempos = [tempo_execucao]
        for _ in range(repeticoes_tempo - 1):
            inicio = time.perf_counter()
            fptas(pesos, valores, capacidade, epsilon)
            fim = time.perf_counter()
            tempos.append(fim - inicio)

        import statistics
        tempo_execucao = statistics.mean(tempos)

    resultado = ResultadoAlgoritmo(
        valor=valor_real,
        itens_selecionados=itens,
        contador=contador,
        tempo_execucao=tempo_execucao,
        nome_algoritmo=nome,
        peso_total=peso_total,
    )
    
    # Adiciona metadados da heuristica (material util p/ analise de resultados)
    resultado.epsilon = eps_usado
    resultado.fator_k = K_usado

    return resultado


if __name__ == "__main__":
    from gerador_instancias import gerar_instancia

    print("=" * 60)
    print("TESTE: FPTAS com diferentes epsilons")
    print("=" * 60)
    
    inst = gerar_instancia(n=15, seed=42)
    
    # Calcula Otimo para referencia
    from prog_dinamica import executar_programacao_dinamica
    resultado_pd = executar_programacao_dinamica(inst)
    otimo = resultado_pd.valor
    
    print(f"VALOR OTIMO (Programacao Dinamica): {otimo}")
    print("-" * 60)
    
    epsilons = [0.5, 0.2, 0.1, 0.05, 0.01]
    print(f"{'Epsilon':<10} {'Valor':<8} {'Garantia Min':<15} {'Instrucoes':<12} {'Tempo (s)'}")
    for eps in epsilons:
        res = executar_heuristica_fptas(inst, epsilon=eps)
        garantia = math.ceil(otimo * (1 - eps))
        print(f"{eps:<10.3f} {res.valor:<8} {garantia:<15} {res.num_instrucoes:<12,} {res.tempo_execucao:.5f}")
