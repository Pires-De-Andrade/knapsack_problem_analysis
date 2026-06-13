"""
Backtracking para o Problema da Mochila Binaria (0/1)
=======================================================

Implementa a solucao por arvore de decisao recursiva com podas, onde cada
no da arvore representa a decisao de incluir ou nao incluir o item i.

Este algoritmo e conceitualmente uma evolucao da Forca Bruta: enquanto a
Forca Bruta avalia TODOS os 2^n subconjuntos sem discriminacao, o
Backtracking usa podas inteligentes para eliminar ramos inteiros da arvore
de busca que comprovadamente nao podem levar a uma solucao melhor que a
ja encontrada. A corretude e mantida (encontra o otimo global), mas o
numero de nos visitados e drasticamente reduzido na pratica.

Duas podas sao implementadas:

    1. **Poda de viabilidade (feasibility pruning)**:
       Nao desce na ramificacao "incluir item i" se o peso acumulado
       mais o peso do item i excederia a capacidade W. Isso evita
       explorar subconjuntos inviaveis.

    2. **Poda por limite superior (bound pruning / branch-and-bound)**:
       Calcula um limite superior otimista para o valor restante
       alcancavel a partir do no atual. Se esse limite nao supera a
       melhor solucao ja encontrada, nao ha razao para continuar
       explorando esse ramo. O limite e calculado usando a relaxacao
       fracionaria (razao valor/peso), que fornece um upper bound
       justo para o problema 0/1.

Complexidade:
    - Tempo:  O(2^n) no pior caso (sem podas eficazes), mas na pratica
              visita muito menos nos. A eficacia das podas depende da
              instancia: instancias com pesos grandes relativo a W
              (poda de viabilidade) ou com itens de valor baixo (poda
              por bound) tendem a ter arvores muito menores.
    - Espaco: O(n) para a pilha de recursao (profundidade maxima n).

Relacao com Forca Bruta:
    Se desativarmos ambas as podas, o Backtracking se reduz exatamente
    a Forca Bruta recursiva, visitando todos os 2^n nos folha. As podas
    sao o que diferencia os dois algoritmos.

Referencia:
    Horowitz, E.; Sahni, S. "Fundamentals of Computer Algorithms".
    Cormen, T.H. et al. "Introduction to Algorithms", 3rd Edition.

Autor: Projeto APA — Problema da Mochila Binaria
"""

import time
import warnings
from typing import Dict, List, Any, Tuple

from instrumentacao import Contador, ResultadoAlgoritmo


# ---------------------------------------------------------------------------
# Constante de limite pratico
# ---------------------------------------------------------------------------

# Valor maximo de n recomendado para o Backtracking.
# Maior que o da Forca Bruta (22) porque as podas reduzem significativamente
# o espaco efetivamente explorado. Na pratica, instancias com n=25-30
# costumam ser resolvidas em segundos quando as podas sao eficazes.
# Para n=35+, mesmo com podas, o pior caso pode ser lento.
N_MAXIMO_RECOMENDADO: int = 30


def _calcular_limite_superior(
    pesos: List[int],
    valores: List[int],
    capacidade_restante: int,
    indice_inicio: int,
    valor_acumulado: int,
    itens_ordenados: List[Tuple[float, int]],
    contador: Contador,
) -> float:
    """
    Calcula o limite superior (upper bound) otimista para o valor
    alcancavel a partir do estado atual, usando relaxacao fracionaria.

    O bound e calculado assumindo que podemos incluir fracoes dos itens
    restantes (relaxacao LP), ordenados por razao valor/peso decrescente.
    Como a versao fracionaria do problema da mochila sempre tem solucao
    >= a versao 0/1, este valor serve como upper bound valido.

    O calculo percorre os itens restantes em ordem decrescente de razao
    valor/peso (pre-ordenados), adicionando itens inteiros enquanto
    cabem e fracionando o ultimo item que nao cabe inteiro.

    Complexidade de tempo:  O(n) no pior caso (percorre itens restantes).
    Complexidade de espaco: O(1) — apenas variaveis escalares.

    Args:
        pesos: Lista de pesos dos itens.
        valores: Lista de valores dos itens.
        capacidade_restante: Capacidade ainda disponivel na mochila.
        indice_inicio: Indice do proximo item a considerar na arvore.
        valor_acumulado: Valor ja acumulado na solucao parcial.
        itens_ordenados: Lista de tuplas (razao_v/p, indice_original),
                         pre-ordenada por razao decrescente.
        contador: Objeto Contador para instrumentacao.

    Returns:
        float: Limite superior otimista do valor alcancavel.
    """
    bound = float(valor_acumulado)
    cap_restante = capacidade_restante

    # Percorre os itens restantes na ordem de melhor razao valor/peso
    # (apenas itens com indice >= indice_inicio na arvore de decisao)
    for razao, idx_original in itens_ordenados:
        # Pula itens que ja foram decididos (antes de indice_inicio)
        contador.comparacoes += 1
        if idx_original < indice_inicio:
            continue

        peso_item = pesos[idx_original]
        valor_item = valores[idx_original]
        contador.acessos += 2  # Acessos a pesos[] e valores[]

        contador.comparacoes += 1
        if peso_item <= cap_restante:
            # Item cabe inteiro: adiciona ao bound
            bound += valor_item
            cap_restante -= peso_item
            contador.somas += 2  # Soma ao bound e subtracao da capacidade
        else:
            # Item nao cabe inteiro: adiciona fracao (relaxacao LP)
            # Fracao = capacidade_restante / peso_item
            bound += valor_item * (cap_restante / peso_item)
            contador.somas += 1  # Soma da fracao ao bound
            break  # Mochila fracionaria cheia, nao ha mais espaco

    return bound


def backtracking(
    pesos: List[int],
    valores: List[int],
    capacidade: int,
    contador: Contador = None,
) -> Tuple[int, List[int], int, Dict[str, int]]:
    """
    Resolve o problema da mochila 0/1 por Backtracking com duas podas:
    poda de viabilidade e poda por limite superior (branch-and-bound).

    A arvore de decisao tem profundidade n, onde cada nivel i representa
    a decisao binaria sobre o item i: incluir (ramo esquerdo) ou nao
    incluir (ramo direito). A arvore completa teria 2^(n+1) - 1 nos,
    mas as podas eliminam ramos inteiros.

    Estrutura da recursao:
        _backtrack(i, peso_atual, valor_atual, solucao_parcial)
          |
          |-- [PODA 1 - Viabilidade]: se peso_atual + pesos[i] > W,
          |   nao desce no ramo "incluir item i".
          |
          |-- [PODA 2 - Bound]: se limite_superior(estado_atual) <= melhor_valor,
          |   nao desce em NENHUM ramo (corta toda a subarvore).
          |
          |-- Ramo INCLUIR item i (se passou nas podas):
          |   _backtrack(i+1, peso+pesos[i], valor+valores[i], ...)
          |
          |-- Ramo NAO INCLUIR item i:
              _backtrack(i+1, peso, valor, ...)

    Complexidade de tempo:  O(2^n) no pior caso (nenhuma poda eficaz).
                            Na pratica, muito menos nos sao visitados.
                            A poda por bound e particularmente eficaz
                            quando os itens tem razoes valor/peso variadas.
    Complexidade de espaco: O(n) — pilha de recursao de profundidade n.

    Args:
        pesos: Lista de pesos dos n itens (indexados de 0 a n-1).
        valores: Lista de valores dos n itens (indexados de 0 a n-1).
        capacidade: Capacidade W da mochila (inteiro nao-negativo).
        contador: Objeto Contador para instrumentacao. Se None, um novo
                  contador e criado internamente.

    Returns:
        Tuple[int, List[int], int, Dict[str, int]]: Tupla contendo:
            - valor_otimo (int): Valor maximo alcancavel.
            - itens_selecionados (List[int]): Indices dos itens na solucao
              otima (0-indexed).
            - peso_total (int): Peso total da solucao otima.
            - estatisticas_poda (Dict[str, int]): Dicionario com contagens
              de nos visitados e podas aplicadas:
                - 'nodos_visitados': Total de nos da arvore explorados.
                - 'podas_viabilidade': Nos cortados por exceder capacidade.
                - 'podas_bound': Nos cortados por bound insuficiente.
    """
    n = len(pesos)

    # Inicializa o contador se nao fornecido externamente
    if contador is None:
        contador = Contador()

    # Emite warning se n excede o limite recomendado
    if n > N_MAXIMO_RECOMENDADO:
        warnings.warn(
            f"Backtracking chamado com n={n}, que excede o limite recomendado "
            f"de {N_MAXIMO_RECOMENDADO}. Embora as podas melhorem o desempenho "
            f"pratico, o pior caso continua sendo O(2^{n}).",
            RuntimeWarning,
            stacklevel=2,
        )

    # ---------------------------------------------------------------
    # Pre-processamento: ordenar itens por razao valor/peso para o bound
    # ---------------------------------------------------------------
    # A ordem de razao decrescente maximiza a eficacia da poda por bound,
    # pois itens com melhor razao sao testados primeiro, encontrando
    # solucoes boas mais cedo.
    itens_ordenados: List[Tuple[float, int]] = sorted(
        [(valores[i] / pesos[i] if pesos[i] > 0 else float("inf"), i)
         for i in range(n)],
        reverse=True,
    )

    # Estado global da melhor solucao encontrada (mutavel pela recursao)
    melhor = {
        "valor": 0,
        "itens": [],
        "peso": 0,
    }

    # Estatisticas de poda (material para analise de resultados)
    estatisticas_poda = {
        "nodos_visitados": 0,
        "podas_viabilidade": 0,
        "podas_bound": 0,
    }

    # ---------------------------------------------------------------
    # Funcao recursiva interna (backtrack)
    # ---------------------------------------------------------------
    def _backtrack(
        i: int,
        peso_atual: int,
        valor_atual: int,
        solucao_parcial: List[int],
    ) -> None:
        """
        Explora recursivamente a arvore de decisao para o item i.

        Args:
            i: Indice do item sendo decidido (0 a n-1).
            peso_atual: Peso acumulado na solucao parcial.
            valor_atual: Valor acumulado na solucao parcial.
            solucao_parcial: Lista de indices dos itens incluidos ate aqui.
        """
        # Contabiliza este no como visitado
        estatisticas_poda["nodos_visitados"] += 1
        contador.acessos += 1  # Acesso ao no da arvore

        # --- Caso base: todos os itens foram decididos ---
        contador.comparacoes += 1
        if i == n:
            # Verifica se esta solucao completa e melhor que a atual
            contador.comparacoes += 1
            if valor_atual > melhor["valor"]:
                melhor["valor"] = valor_atual
                melhor["itens"] = solucao_parcial[:]  # Copia da lista
                melhor["peso"] = peso_atual
            return

        # ===================================================
        # PODA 2 — Poda por limite superior (bound pruning)
        # ===================================================
        # Calcula o upper bound otimista para a melhor solucao possivel
        # a partir deste no. Se o bound nao supera a melhor solucao
        # ja conhecida, toda esta subarvore pode ser descartada.
        bound = _calcular_limite_superior(
            pesos, valores,
            capacidade - peso_atual,  # Capacidade restante
            i,                         # Proximo item a considerar
            valor_atual,               # Valor ja acumulado
            itens_ordenados,
            contador,
        )
        contador.somas += 1  # Subtracao capacidade - peso_atual

        contador.comparacoes += 1
        if bound <= melhor["valor"]:
            # O melhor caso possivel deste ramo nao supera o que ja temos.
            # Descarta toda a subarvore — nao ha como melhorar.
            estatisticas_poda["podas_bound"] += 1
            return

        # ===================================================
        # RAMO 1 — Incluir o item i (se viavel)
        # ===================================================
        peso_com_item = peso_atual + pesos[i]
        contador.acessos += 1  # Acesso a pesos[i]
        contador.somas += 1    # Soma peso_atual + pesos[i]

        # PODA 1 — Poda de viabilidade (feasibility pruning)
        # So desce neste ramo se o item i cabe na mochila.
        contador.comparacoes += 1
        if peso_com_item <= capacidade:
            # Item i cabe: inclui na solucao parcial e recursa
            valor_com_item = valor_atual + valores[i]
            contador.acessos += 1  # Acesso a valores[i]
            contador.somas += 1    # Soma valor_atual + valores[i]

            solucao_parcial.append(i)
            _backtrack(i + 1, peso_com_item, valor_com_item, solucao_parcial)
            solucao_parcial.pop()  # Desfaz a inclusao (backtrack)
        else:
            # Item i nao cabe: poda de viabilidade aplicada
            estatisticas_poda["podas_viabilidade"] += 1

        # ===================================================
        # RAMO 2 — Nao incluir o item i
        # ===================================================
        # Sempre explora este ramo (a menos que a poda por bound
        # ja tenha cortado no inicio da funcao).
        _backtrack(i + 1, peso_atual, valor_atual, solucao_parcial)

    # ---------------------------------------------------------------
    # Inicia a recursao a partir do item 0
    # ---------------------------------------------------------------
    _backtrack(0, 0, 0, [])

    return melhor["valor"], melhor["itens"], melhor["peso"], estatisticas_poda


def executar_backtracking(
    instancia: Dict[str, Any],
    repeticoes_tempo: int = 1,
) -> ResultadoAlgoritmo:
    """
    Funcao de alto nivel que executa o Backtracking sobre uma instancia
    do problema da mochila e retorna o resultado padronizado.

    Alem dos campos padrao do ResultadoAlgoritmo, inclui estatisticas
    de poda no campo `extras` do resultado, fornecendo dados para a
    analise de eficacia das podas no relatorio.

    Args:
        instancia: Dicionario com os dados da instancia (campos 'pesos',
                   'valores', 'capacidade').
        repeticoes_tempo: Numero de repeticoes para medicao de tempo.

    Returns:
        ResultadoAlgoritmo: Resultado padronizado com valor, itens,
                            contagem de instrucoes e tempo. O campo
                            `estatisticas_poda` e adicionado como
                            atributo extra ao objeto retornado.
    """
    pesos = instancia["pesos"]
    valores = instancia["valores"]
    capacidade = instancia["capacidade"]

    nome = "Backtracking (com podas)"

    # Cria o contador de instrucoes
    contador = Contador()

    # Mede o tempo de execucao
    inicio = time.perf_counter()
    valor_otimo, itens_selecionados, peso_total, estatisticas_poda = backtracking(
        pesos, valores, capacidade, contador
    )
    fim = time.perf_counter()
    tempo_execucao = fim - inicio

    # Se pedido mais repeticoes, refaz apenas para tempo (sem recontar instrucoes)
    if repeticoes_tempo > 1:
        tempos = [tempo_execucao]
        for _ in range(repeticoes_tempo - 1):
            inicio = time.perf_counter()
            backtracking(pesos, valores, capacidade)
            fim = time.perf_counter()
            tempos.append(fim - inicio)

        import statistics
        tempo_execucao = statistics.mean(tempos)

    # Monta o resultado padronizado
    resultado = ResultadoAlgoritmo(
        valor=valor_otimo,
        itens_selecionados=itens_selecionados,
        contador=contador,
        tempo_execucao=tempo_execucao,
        nome_algoritmo=nome,
        peso_total=peso_total,
    )

    # Adiciona estatisticas de poda como atributo extra
    # (material para graficos de eficacia da poda na documentacao)
    resultado.estatisticas_poda = estatisticas_poda

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
    print("TESTE: Backtracking (arvore de decisao com podas)")
    print("=" * 60)
    resultado = executar_backtracking(instancia_teste)
    print(resultado)
    print(f"Estatisticas de poda:")
    for chave, valor in resultado.estatisticas_poda.items():
        print(f"  {chave}: {valor}")

    # Teste com instancia aleatoria
    print("\n" + "=" * 60)
    print("TESTE: Backtracking com instancia aleatoria (n=15)")
    print("=" * 60)
    inst = gerar_instancia(n=15, seed=42)
    imprimir_instancia(inst)
    resultado2 = executar_backtracking(inst)
    print(resultado2)
    print(f"Estatisticas de poda:")
    for chave, valor in resultado2.estatisticas_poda.items():
        print(f"  {chave}: {valor}")

    # Comparacao com Forca Bruta
    print("\n" + "=" * 60)
    print("COMPARACAO: Forca Bruta vs Backtracking (n=15, seed=42)")
    print("=" * 60)
    from forca_bruta import executar_forca_bruta
    resultado_fb = executar_forca_bruta(inst)
    print(f"Forca Bruta:  valor={resultado_fb.valor}, "
          f"instrucoes={resultado_fb.num_instrucoes:,}")
    print(f"Backtracking: valor={resultado2.valor}, "
          f"instrucoes={resultado2.num_instrucoes:,}")
    print(f"Reducao:      {(1 - resultado2.num_instrucoes/resultado_fb.num_instrucoes)*100:.1f}% "
          f"menos instrucoes")
    assert resultado_fb.valor == resultado2.valor, "ERRO: Valores divergem!"
    print("[OK] Ambos encontraram o mesmo valor otimo.")
