"""
Forca Bruta para o Problema da Mochila Binaria (0/1)
======================================================

Implementa a solucao por enumeracao exaustiva de todos os 2^n subconjuntos
possiveis de itens, avaliando peso e valor de cada subconjunto e mantendo
o melhor resultado viavel (que nao excede a capacidade W).

Decisao de design — representacao binaria iterativa:
    Optou-se pela abordagem iterativa com representacao binaria (inteiros
    de 0 a 2^n - 1) em vez de recursao "incluir/nao incluir". Justificativa:

    1. **Clareza didatica**: a representacao binaria torna explicito que
       cada subconjunto corresponde a uma mascara de bits, onde o bit j
       indica se o item j esta incluido (1) ou nao (0). Isso facilita
       a explicacao na documentacao de que ha exatamente 2^n subconjuntos.

    2. **Simplicidade**: a implementacao iterativa evita overhead de
       chamadas recursivas e facilita a contagem precisa de instrucoes.

    3. **Contraste com Backtracking**: ao nao realizar nenhuma poda, fica
       evidente que TODOS os 2^n subconjuntos sao avaliados, o que
       evidencia a diferenca para o Backtracking (que aplica podas para
       evitar explorar subconjuntos improdutivos).

Complexidade:
    - Tempo:  O(2^n * n) — para cada um dos 2^n subconjuntos, percorre-se
              ate n itens para calcular peso e valor totais.
    - Espaco: O(n) — armazena apenas a melhor solucao encontrada e a
              solucao corrente.

LIMITACAO PRATICA:
    Devido a complexidade exponencial, este algoritmo so e viavel para
    instancias pequenas. Para n=20, ha ~1 milhao de subconjuntos; para
    n=25, ~33 milhoes. O limite recomendado e N_MAXIMO_RECOMENDADO = 22.

Referencia:
    Cormen, T.H. et al. "Introduction to Algorithms", 3rd Edition.
    A enumeracao exaustiva e a abordagem mais simples e serve como
    baseline para comparacao com algoritmos mais sofisticados.

Autor: Projeto APA — Problema da Mochila Binaria
"""

import time
import warnings
from typing import Dict, List, Any, Tuple

from instrumentacao import Contador, ResultadoAlgoritmo


# ---------------------------------------------------------------------------
# Constante de limite pratico para algoritmos exponenciais
# ---------------------------------------------------------------------------

# Valor maximo de n recomendado para a Forca Bruta.
# Para n=22, ha 2^22 = 4.194.304 subconjuntos, o que leva poucos segundos.
# Para n=25, ha 2^25 = 33.554.432 subconjuntos, ja podendo levar minutos.
N_MAXIMO_RECOMENDADO: int = 22


def forca_bruta(
    pesos: List[int],
    valores: List[int],
    capacidade: int,
    contador: Contador = None,
) -> Tuple[int, List[int], int]:
    """
    Resolve o problema da mochila 0/1 por Forca Bruta, enumerando todos
    os 2^n subconjuntos possiveis de itens.

    Para cada subconjunto (representado como mascara de bits de 0 a 2^n - 1):
      1. Calcula o peso total dos itens incluidos.
      2. Se o peso total nao excede a capacidade W, calcula o valor total.
      3. Se o valor total supera o melhor encontrado, atualiza a melhor solucao.

    A representacao binaria funciona assim:
      - O inteiro `mascara` tem n bits.
      - O bit j (contando do menos significativo) indica se o item j esta
        incluido (bit=1) ou nao (bit=0).
      - Exemplo para n=3: mascara=5 (binario 101) -> itens {0, 2} incluidos.

    Nenhuma poda e aplicada: TODOS os 2^n subconjuntos sao avaliados,
    mesmo aqueles que claramente excedem a capacidade. Isso diferencia
    este algoritmo do Backtracking, que aplica podas para reduzir o
    espaco de busca.

    Complexidade de tempo:  O(2^n * n) — 2^n subconjuntos, cada um com
                            ate n itens para somar.
    Complexidade de espaco: O(n) — apenas a melhor solucao e armazenada.

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
            f"Forca Bruta chamada com n={n}, que excede o limite recomendado "
            f"de {N_MAXIMO_RECOMENDADO}. A execucao pode levar tempo "
            f"impraticavel (2^{n} = {2**n:,} subconjuntos).",
            RuntimeWarning,
            stacklevel=2,
        )

    # Variaveis para rastrear a melhor solucao encontrada
    melhor_valor: int = 0
    melhor_itens: List[int] = []
    melhor_peso: int = 0

    # Total de subconjuntos a avaliar: 2^n
    total_subconjuntos = 1 << n  # Equivalente a 2**n, mais eficiente

    # ---------------------------------------------------------------
    # Enumeracao exaustiva de todos os 2^n subconjuntos
    # ---------------------------------------------------------------
    for mascara in range(total_subconjuntos):
        peso_subconjunto: int = 0
        valor_subconjunto: int = 0
        itens_subconjunto: List[int] = []

        # Para cada item j, verifica se o bit j esta ativo na mascara
        for j in range(n):
            # Testa o bit j: (mascara >> j) & 1
            contador.comparacoes += 1  # Teste do bit j
            if (mascara >> j) & 1:
                # Item j esta incluido neste subconjunto
                peso_subconjunto += pesos[j]
                valor_subconjunto += valores[j]
                itens_subconjunto.append(j)
                contador.acessos += 2  # Acessos a pesos[j] e valores[j]
                contador.somas += 2    # Somas de peso e valor acumulados

        # Verifica se o subconjunto e viavel (peso nao excede capacidade)
        contador.comparacoes += 1  # Comparacao peso <= capacidade
        if peso_subconjunto <= capacidade:
            # Subconjunto viavel: verifica se e melhor que o atual
            contador.comparacoes += 1  # Comparacao valor > melhor_valor
            if valor_subconjunto > melhor_valor:
                melhor_valor = valor_subconjunto
                melhor_itens = itens_subconjunto
                melhor_peso = peso_subconjunto

    return melhor_valor, melhor_itens, melhor_peso


def executar_forca_bruta(
    instancia: Dict[str, Any],
    repeticoes_tempo: int = 1,
) -> ResultadoAlgoritmo:
    """
    Funcao de alto nivel que executa a Forca Bruta sobre uma instancia
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

    nome = "Forca Bruta (2^n subconjuntos)"

    # Cria o contador de instrucoes
    contador = Contador()

    # Mede o tempo de execucao
    inicio = time.perf_counter()
    valor_otimo, itens_selecionados, peso_total = forca_bruta(
        pesos, valores, capacidade, contador
    )
    fim = time.perf_counter()
    tempo_execucao = fim - inicio

    # Se pedido mais repeticoes, refaz apenas para tempo (sem recontar instrucoes)
    if repeticoes_tempo > 1:
        tempos = [tempo_execucao]
        for _ in range(repeticoes_tempo - 1):
            inicio = time.perf_counter()
            forca_bruta(pesos, valores, capacidade)
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
    print("TESTE: Forca Bruta (enumeracao de 2^n subconjuntos)")
    print("=" * 60)
    resultado = executar_forca_bruta(instancia_teste)
    print(resultado)
    print(f"Subconjuntos avaliados: 2^{instancia_teste['n']} = {2**instancia_teste['n']}")

    # Teste com instancia gerada aleatoriamente
    print("\n" + "=" * 60)
    print("TESTE: Forca Bruta com instancia aleatoria (n=15)")
    print("=" * 60)
    inst_aleatoria = gerar_instancia(n=15, seed=42)
    imprimir_instancia(inst_aleatoria)
    resultado2 = executar_forca_bruta(inst_aleatoria)
    print(resultado2)
