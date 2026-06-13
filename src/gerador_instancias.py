"""
Gerador de Instâncias para o Problema da Mochila Binária
==========================================================

Fornece funções para gerar instâncias aleatórias do problema da mochila 0/1,
bem como para salvar e carregar instâncias em formato JSON, garantindo
reprodutibilidade dos experimentos por meio de seeds configuráveis.

Uma instância é representada pelo dicionário:
    {
        "n": int,                     # Número de itens
        "capacidade": int,            # Capacidade W da mochila
        "pesos": List[int],           # Peso de cada item
        "valores": List[int],         # Valor de cada item
        "seed": int | None,           # Seed usada na geração
        "fracao_capacidade": float,   # Fração da soma de pesos usada como W
    }

Autor: Projeto APA — Problema da Mochila Binária
"""

import json
import os
import random
from typing import Dict, List, Optional, Any


def gerar_instancia(
    n: int,
    peso_min: int = 1,
    peso_max: int = 100,
    valor_min: int = 1,
    valor_max: int = 100,
    fracao_capacidade: float = 0.5,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Gera uma instância aleatória do problema da mochila binária (0/1).

    Os pesos e valores são gerados uniformemente no intervalo [min, max].
    A capacidade W da mochila é calculada como uma fração da soma total
    dos pesos, o que produz instâncias com dificuldade controlável:
      - fracao_capacidade ≈ 0.5 → instâncias moderadas (nem muito fáceis,
        nem triviais)
      - fracao_capacidade < 0.3 → mochila apertada (poucos itens cabem)
      - fracao_capacidade > 0.7 → mochila folgada (maioria dos itens cabe)

    Complexidade de tempo: O(n) para gerar n itens.
    Complexidade de espaço: O(n) para armazenar pesos e valores.

    Args:
        n: Número de itens a gerar.
        peso_min: Peso mínimo de um item (padrão: 1).
        peso_max: Peso máximo de um item (padrão: 100).
        valor_min: Valor mínimo de um item (padrão: 1).
        valor_max: Valor máximo de um item (padrão: 100).
        fracao_capacidade: Fração da soma total dos pesos usada como
                           capacidade W da mochila (padrão: 0.5).
        seed: Semente para o gerador aleatório, garantindo reprodutibilidade.
              Se None, uma seed aleatória é usada.

    Returns:
        Dict[str, Any]: Dicionário representando a instância gerada, com
                        as chaves 'n', 'capacidade', 'pesos', 'valores',
                        'seed' e 'fracao_capacidade'.

    Raises:
        ValueError: Se os parâmetros forem inválidos (n < 1, pesos/valores
                    negativos, fração fora de (0, 1]).

    Exemplo:
        >>> instancia = gerar_instancia(n=10, seed=42)
        >>> print(instancia['n'], instancia['capacidade'])
        10 255
    """
    # --- Validação dos parâmetros de entrada ---
    if n < 1:
        raise ValueError(f"Número de itens deve ser >= 1, recebido: {n}")
    if peso_min < 0 or peso_max < 0:
        raise ValueError(f"Pesos devem ser não-negativos: [{peso_min}, {peso_max}]")
    if peso_min > peso_max:
        raise ValueError(f"peso_min ({peso_min}) > peso_max ({peso_max})")
    if valor_min < 0 or valor_max < 0:
        raise ValueError(f"Valores devem ser não-negativos: [{valor_min}, {valor_max}]")
    if valor_min > valor_max:
        raise ValueError(f"valor_min ({valor_min}) > valor_max ({valor_max})")
    if not (0 < fracao_capacidade <= 1.0):
        raise ValueError(
            f"fracao_capacidade deve estar em (0, 1], recebido: {fracao_capacidade}"
        )

    # Configura a seed para reprodutibilidade
    if seed is not None:
        random.seed(seed)

    # Gera pesos e valores aleatórios uniformemente distribuídos
    pesos: List[int] = [random.randint(peso_min, peso_max) for _ in range(n)]
    valores: List[int] = [random.randint(valor_min, valor_max) for _ in range(n)]

    # Calcula a capacidade como fração da soma total dos pesos
    soma_pesos = sum(pesos)
    capacidade = max(1, int(soma_pesos * fracao_capacidade))

    instancia: Dict[str, Any] = {
        "n": n,
        "capacidade": capacidade,
        "pesos": pesos,
        "valores": valores,
        "seed": seed,
        "fracao_capacidade": fracao_capacidade,
    }

    return instancia


def gerar_conjunto_instancias(
    tamanhos: List[int],
    num_instancias_por_tamanho: int = 5,
    seed_base: int = 0,
    **kwargs,
) -> List[Dict[str, Any]]:
    """
    Gera múltiplas instâncias para cada tamanho especificado, útil para
    experimentos com tamanhos crescentes de n.

    Para cada tamanho n e cada repetição r, a seed utilizada é:
        seed = seed_base + n * 1000 + r
    Isso garante reprodutibilidade completa e independência entre instâncias.

    Complexidade de tempo: O(len(tamanhos) * num_instancias_por_tamanho * n_max).
    Complexidade de espaço: O(total_instancias * n_max).

    Args:
        tamanhos: Lista com os tamanhos de n desejados (ex: [5, 10, 15, 20]).
        num_instancias_por_tamanho: Quantas instâncias gerar para cada n (padrão: 5).
        seed_base: Seed base para geração determinística (padrão: 0).
        **kwargs: Argumentos adicionais repassados para `gerar_instancia`.

    Returns:
        List[Dict[str, Any]]: Lista de instâncias geradas, cada uma contendo
                              um campo adicional 'id_instancia' com o
                              identificador único.

    Exemplo:
        >>> instancias = gerar_conjunto_instancias([5, 10], num_instancias_por_tamanho=3)
        >>> len(instancias)
        6
    """
    instancias: List[Dict[str, Any]] = []

    for n in tamanhos:
        for r in range(num_instancias_por_tamanho):
            # Seed determinística baseada no tamanho e na repetição
            seed = seed_base + n * 1000 + r

            instancia = gerar_instancia(n=n, seed=seed, **kwargs)
            instancia["id_instancia"] = f"n{n}_r{r}"

            instancias.append(instancia)

    return instancias


def salvar_instancia(instancia: Dict[str, Any], caminho_arquivo: str) -> None:
    """
    Salva uma instância do problema da mochila em formato JSON.

    Cria os diretórios necessários automaticamente caso não existam.
    O JSON é formatado com indentação para facilitar inspeção manual.

    Complexidade de tempo: O(n) para serializar n itens.
    Complexidade de espaço: O(n) para a string JSON em memória.

    Args:
        instancia: Dicionário da instância a ser salva.
        caminho_arquivo: Caminho completo do arquivo JSON de destino.

    Raises:
        IOError: Se não for possível escrever no caminho especificado.

    Exemplo:
        >>> instancia = gerar_instancia(n=10, seed=42)
        >>> salvar_instancia(instancia, "instancias/inst_n10_s42.json")
    """
    # Cria diretórios intermediários, se necessário
    diretorio = os.path.dirname(caminho_arquivo)
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)

    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(instancia, arquivo, indent=2, ensure_ascii=False)


def carregar_instancia(caminho_arquivo: str) -> Dict[str, Any]:
    """
    Carrega uma instância do problema da mochila a partir de um arquivo JSON.

    Realiza validação básica dos campos obrigatórios após o carregamento.

    Complexidade de tempo: O(n) para desserializar n itens.
    Complexidade de espaço: O(n) para armazenar a instância em memória.

    Args:
        caminho_arquivo: Caminho completo do arquivo JSON a ser lido.

    Returns:
        Dict[str, Any]: Dicionário com os dados da instância carregada.

    Raises:
        FileNotFoundError: Se o arquivo não existir.
        ValueError: Se o arquivo não contiver os campos obrigatórios.

    Exemplo:
        >>> instancia = carregar_instancia("instancias/inst_n10_s42.json")
        >>> print(instancia['n'], instancia['capacidade'])
    """
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        instancia = json.load(arquivo)

    # Validação dos campos obrigatórios
    campos_obrigatorios = ["n", "capacidade", "pesos", "valores"]
    campos_faltantes = [c for c in campos_obrigatorios if c not in instancia]

    if campos_faltantes:
        raise ValueError(
            f"Arquivo '{caminho_arquivo}' não contém os campos obrigatórios: "
            f"{campos_faltantes}"
        )

    # Validação de consistência
    if len(instancia["pesos"]) != instancia["n"]:
        raise ValueError(
            f"Tamanho da lista de pesos ({len(instancia['pesos'])}) "
            f"difere de n ({instancia['n']})"
        )
    if len(instancia["valores"]) != instancia["n"]:
        raise ValueError(
            f"Tamanho da lista de valores ({len(instancia['valores'])}) "
            f"difere de n ({instancia['n']})"
        )

    return instancia


def salvar_conjunto_instancias(
    instancias: List[Dict[str, Any]], diretorio: str
) -> List[str]:
    """
    Salva uma lista de instâncias em arquivos JSON individuais dentro
    de um diretório.

    Cada instância é salva com o nome baseado no campo 'id_instancia'
    (se presente) ou em um nome sequencial.

    Complexidade de tempo: O(total_itens) para serializar todas as instâncias.
    Complexidade de espaço: O(n_max) por arquivo JSON gerado.

    Args:
        instancias: Lista de dicionários representando instâncias.
        diretorio: Caminho do diretório onde salvar os arquivos.

    Returns:
        List[str]: Lista de caminhos dos arquivos salvos.
    """
    os.makedirs(diretorio, exist_ok=True)
    caminhos: List[str] = []

    for i, instancia in enumerate(instancias):
        # Usa id_instancia se disponível, senão gera nome sequencial
        nome = instancia.get("id_instancia", f"instancia_{i:04d}")
        caminho = os.path.join(diretorio, f"{nome}.json")
        salvar_instancia(instancia, caminho)
        caminhos.append(caminho)

    return caminhos


def carregar_conjunto_instancias(diretorio: str) -> List[Dict[str, Any]]:
    """
    Carrega todas as instâncias JSON de um diretório.

    Os arquivos são carregados em ordem alfabética para garantir
    consistência entre execuções.

    Args:
        diretorio: Caminho do diretório contendo arquivos JSON.

    Returns:
        List[Dict[str, Any]]: Lista de instâncias carregadas.

    Raises:
        FileNotFoundError: Se o diretório não existir.
    """
    if not os.path.isdir(diretorio):
        raise FileNotFoundError(f"Diretório não encontrado: {diretorio}")

    instancias: List[Dict[str, Any]] = []

    # Ordena para garantir ordem determinística
    arquivos = sorted(
        f for f in os.listdir(diretorio) if f.endswith(".json")
    )

    for nome_arquivo in arquivos:
        caminho = os.path.join(diretorio, nome_arquivo)
        instancia = carregar_instancia(caminho)
        instancias.append(instancia)

    return instancias


def imprimir_instancia(instancia: Dict[str, Any]) -> None:
    """
    Imprime uma instância de forma legível no terminal, útil para
    depuração e verificação visual.

    Args:
        instancia: Dicionário representando a instância.
    """
    print(f"{'='*50}")
    print(f"Instância: {instancia.get('id_instancia', 'sem id')}")
    print(f"  n (itens):        {instancia['n']}")
    print(f"  Capacidade (W):   {instancia['capacidade']}")
    print(f"  Seed:             {instancia.get('seed', 'N/A')}")
    print(f"  Fração capac.:    {instancia.get('fracao_capacidade', 'N/A')}")
    print(f"  {'Índice':<8} {'Peso':<8} {'Valor':<8} {'Razão v/p':<10}")
    print(f"  {'-'*34}")

    for i in range(instancia["n"]):
        peso = instancia["pesos"][i]
        valor = instancia["valores"][i]
        razao = valor / peso if peso > 0 else float("inf")
        print(f"  {i:<8} {peso:<8} {valor:<8} {razao:<10.2f}")

    soma_pesos = sum(instancia["pesos"])
    soma_valores = sum(instancia["valores"])
    print(f"  {'-'*34}")
    print(f"  {'TOTAL':<8} {soma_pesos:<8} {soma_valores:<8}")
    print(f"{'='*50}")
