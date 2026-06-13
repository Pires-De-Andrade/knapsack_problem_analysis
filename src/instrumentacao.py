"""
Módulo de Instrumentação para Análise de Algoritmos
=====================================================

Fornece mecanismos para contagem de instruções (operações relevantes) e
medição de tempo de execução dos algoritmos da mochila binária.

A contagem de instruções é feita por meio da classe `Contador`, que registra
individualmente cada tipo de operação (comparações, somas, acessos a estrutura
de dados) e fornece o total agregado. Essa separação permite análise detalhada
da complexidade prática de cada algoritmo.

A medição de tempo é realizada pelo decorator `medir_tempo`, que executa o
algoritmo múltiplas vezes e calcula a média, mediana e desvio padrão, eliminando
ruído de variação do sistema operacional.

Autor: Projeto APA — Problema da Mochila Binária
"""

import time
import statistics
from functools import wraps
from typing import Callable, Any, Dict, Tuple, List


class Contador:
    """
    Contador de instruções para análise de complexidade prática.

    Registra três categorias de operações relevantes:
      - comparacoes: operações de comparação (>, <, >=, <=, ==, !=)
      - somas: operações aritméticas (adições, subtrações, multiplicações)
      - acessos: acessos a estruturas de dados (listas, dicionários, tabelas)

    O contador é passado como argumento para as funções dos algoritmos,
    que o utilizam para registrar operações sem poluir a lógica principal.
    Isso separa claramente a lógica do algoritmo da lógica de instrumentação.

    Complexidade de tempo: O(1) para todas as operações de registro.
    Complexidade de espaço: O(1) — apenas três inteiros são armazenados.

    Exemplo de uso:
        >>> contador = Contador()
        >>> contador.comparacoes += 1
        >>> contador.somas += 3
        >>> contador.acessos += 2
        >>> print(contador.total)
        6
        >>> print(contador.detalhes())
        {'comparacoes': 1, 'somas': 3, 'acessos': 2, 'total': 6}
    """

    def __init__(self):
        """Inicializa todos os contadores com valor zero."""
        self.comparacoes: int = 0   # Comparações (>, <, >=, <=, ==, !=)
        self.somas: int = 0         # Operações aritméticas (+, -, *, //)
        self.acessos: int = 0       # Acessos a estruturas de dados (lista[i], dict[k])

    @property
    def total(self) -> int:
        """
        Retorna o total de instruções registradas (soma de todas as categorias).

        Returns:
            int: Total de instruções contabilizadas.
        """
        return self.comparacoes + self.somas + self.acessos

    def detalhes(self) -> Dict[str, int]:
        """
        Retorna um dicionário com a contagem detalhada por categoria.

        Returns:
            Dict[str, int]: Dicionário com as chaves 'comparacoes', 'somas',
                            'acessos' e 'total'.
        """
        return {
            "comparacoes": self.comparacoes,
            "somas": self.somas,
            "acessos": self.acessos,
            "total": self.total,
        }

    def resetar(self) -> None:
        """Reinicia todos os contadores para zero."""
        self.comparacoes = 0
        self.somas = 0
        self.acessos = 0

    def __repr__(self) -> str:
        """Representação textual do contador para depuração."""
        return (
            f"Contador(comparacoes={self.comparacoes}, "
            f"somas={self.somas}, "
            f"acessos={self.acessos}, "
            f"total={self.total})"
        )

    def __str__(self) -> str:
        """Representação legível do contador para impressão."""
        return (
            f"Instruções: {self.total:,} total "
            f"({self.comparacoes:,} comp. | "
            f"{self.somas:,} somas | "
            f"{self.acessos:,} acessos)"
        )


class ResultadoAlgoritmo:
    """
    Estrutura padronizada para o resultado de qualquer algoritmo da mochila.

    Todos os algoritmos retornam uma instância desta classe, garantindo
    uniformidade na interface e facilitando comparação e análise.

    Attributes:
        valor: Valor ótimo (ou aproximado) da solução encontrada.
        itens_selecionados: Lista de índices dos itens selecionados (0-indexed).
        num_instrucoes: Total de instruções contabilizadas durante a execução.
        detalhes_instrucoes: Dicionário com contagem por categoria de instrução.
        tempo_execucao: Tempo de execução em segundos.
        nome_algoritmo: Nome identificador do algoritmo utilizado.
        peso_total: Peso total dos itens selecionados.
    """

    def __init__(
        self,
        valor: int,
        itens_selecionados: List[int],
        contador: Contador,
        tempo_execucao: float,
        nome_algoritmo: str,
        peso_total: int = 0,
    ):
        """
        Inicializa o resultado do algoritmo.

        Args:
            valor: Valor ótimo ou aproximado encontrado.
            itens_selecionados: Lista de índices dos itens na solução (0-indexed).
            contador: Objeto Contador com as instruções registradas.
            tempo_execucao: Tempo de execução em segundos.
            nome_algoritmo: Nome identificador do algoritmo.
            peso_total: Peso total dos itens selecionados.
        """
        self.valor: int = valor
        self.itens_selecionados: List[int] = sorted(itens_selecionados)
        self.num_instrucoes: int = contador.total
        self.detalhes_instrucoes: Dict[str, int] = contador.detalhes()
        self.tempo_execucao: float = tempo_execucao
        self.nome_algoritmo: str = nome_algoritmo
        self.peso_total: int = peso_total

    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o resultado para dicionário, útil para exportação CSV/JSON.

        Returns:
            Dict[str, Any]: Dicionário com todos os campos do resultado.
        """
        return {
            "algoritmo": self.nome_algoritmo,
            "valor": self.valor,
            "peso_total": self.peso_total,
            "num_itens_selecionados": len(self.itens_selecionados),
            "itens_selecionados": self.itens_selecionados,
            "num_instrucoes": self.num_instrucoes,
            "comparacoes": self.detalhes_instrucoes["comparacoes"],
            "somas": self.detalhes_instrucoes["somas"],
            "acessos": self.detalhes_instrucoes["acessos"],
            "tempo_execucao": self.tempo_execucao,
        }

    def __str__(self) -> str:
        """Representação legível do resultado para impressão."""
        return (
            f"=== {self.nome_algoritmo} ===\n"
            f"  Valor encontrado:    {self.valor}\n"
            f"  Peso total:          {self.peso_total}\n"
            f"  Itens selecionados:  {self.itens_selecionados}\n"
            f"  Instruções totais:   {self.num_instrucoes:,}\n"
            f"  Tempo de execução:   {self.tempo_execucao:.6f} s\n"
        )


def medir_tempo(funcao: Callable, *args, repeticoes: int = 1, **kwargs) -> Tuple[Any, float]:
    """
    Executa uma função múltiplas vezes e retorna o resultado junto com o
    tempo médio de execução, para medição precisa de desempenho.

    Utiliza `time.perf_counter()` para máxima precisão do relógio do sistema.
    Quando `repeticoes > 1`, o resultado da primeira execução é preservado
    (para consistência), e apenas o tempo é recalculado como média.

    Complexidade de tempo: O(repeticoes * T(funcao)), onde T(funcao) é o
                           tempo de uma execução da função.
    Complexidade de espaço: O(repeticoes) para armazenar os tempos individuais.

    Args:
        funcao: Função a ser executada e medida.
        *args: Argumentos posicionais para a função.
        repeticoes: Número de repetições para cálculo da média (padrão: 1).
        **kwargs: Argumentos nomeados para a função.

    Returns:
        Tuple[Any, float]: Tupla (resultado_da_funcao, tempo_medio_em_segundos).

    Raises:
        ValueError: Se `repeticoes` for menor que 1.

    Exemplo:
        >>> resultado, tempo = medir_tempo(minha_funcao, arg1, arg2, repeticoes=10)
    """
    if repeticoes < 1:
        raise ValueError(f"Número de repetições deve ser >= 1, recebido: {repeticoes}")

    tempos: List[float] = []
    resultado = None

    for i in range(repeticoes):
        inicio = time.perf_counter()
        resultado_atual = funcao(*args, **kwargs)
        fim = time.perf_counter()

        tempos.append(fim - inicio)

        # Preserva o resultado da primeira execução
        if i == 0:
            resultado = resultado_atual

    tempo_medio = statistics.mean(tempos)

    return resultado, tempo_medio


def estatisticas_tempo(tempos: List[float]) -> Dict[str, float]:
    """
    Calcula estatísticas descritivas sobre uma lista de tempos de execução.

    Útil para análise detalhada quando se realizam múltiplas repetições
    de um mesmo experimento.

    Args:
        tempos: Lista de tempos de execução em segundos.

    Returns:
        Dict[str, float]: Dicionário com as estatísticas calculadas:
            - 'media': Média aritmética dos tempos.
            - 'mediana': Mediana dos tempos.
            - 'desvio_padrao': Desvio padrão (0.0 se apenas um tempo).
            - 'minimo': Menor tempo registrado.
            - 'maximo': Maior tempo registrado.

    Raises:
        ValueError: Se a lista de tempos estiver vazia.
    """
    if not tempos:
        raise ValueError("Lista de tempos não pode estar vazia.")

    resultado = {
        "media": statistics.mean(tempos),
        "mediana": statistics.median(tempos),
        "desvio_padrao": statistics.stdev(tempos) if len(tempos) > 1 else 0.0,
        "minimo": min(tempos),
        "maximo": max(tempos),
    }

    return resultado


# ---------------------------------------------------------------------------
# Constantes de configuração para limites de execução
# ---------------------------------------------------------------------------

# Tamanho máximo de n para algoritmos exponenciais (Força Bruta, Divisão e
# Conquista). Esses algoritmos têm complexidade O(2^n), portanto valores
# de n acima deste limite tornam a execução impraticável.
N_MAXIMO_EXPONENCIAL: int = 22

# Mensagem de aviso exibida quando um algoritmo exponencial é chamado com
# n acima do limite configurado.
AVISO_LIMITE_EXPONENCIAL: str = (
    "AVISO: Algoritmo exponencial não executado — n={n} excede o limite "
    "máximo configurado de {limite}. Algoritmos com complexidade O(2^n) "
    "se tornam impraticáveis para valores grandes de n."
)
