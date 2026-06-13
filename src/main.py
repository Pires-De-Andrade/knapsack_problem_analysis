"""
CLI Principal — Problema da Mochila Binária
=============================================

Interface de linha de comando simples para executar um algoritmo
específico sobre uma instância do problema da mochila, ou gerar
uma instância aleatória para teste rápido.

Uso:
    python main.py --algoritmo prog_dinamica --arquivo instancia.json
    python main.py --algoritmo prog_dinamica --gerar 10 --seed 42

Autor: Projeto APA — Problema da Mochila Binária
"""

import argparse
import sys
import os

# Adiciona o diretório src ao path para imports locais
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gerador_instancias import gerar_instancia, carregar_instancia, imprimir_instancia
from instrumentacao import ResultadoAlgoritmo


# Mapeamento de nomes de algoritmos para funções de execução
ALGORITMOS_DISPONIVEIS = {
    "prog_dinamica": "Programação Dinâmica (tabela)",
    "prog_dinamica_otimizada": "Programação Dinâmica (espaço otimizado)",
    "forca_bruta": "Força Bruta",
    "backtracking": "Backtracking",
    "divisao_conquista": "Divisão e Conquista",
    "guloso": "Guloso",
    "heuristica": "Heurística FPTAS",
}


def carregar_algoritmo(nome: str):
    """
    Importa e retorna a função de execução do algoritmo especificado.

    Args:
        nome: Nome do algoritmo (chave em ALGORITMOS_DISPONIVEIS).

    Returns:
        Callable: Função de execução do algoritmo.

    Raises:
        NotImplementedError: Se o algoritmo ainda não foi implementado.
    """
    if nome == "prog_dinamica":
        from prog_dinamica import executar_programacao_dinamica
        return lambda inst: executar_programacao_dinamica(inst, versao="tabela")

    elif nome == "prog_dinamica_otimizada":
        from prog_dinamica import executar_programacao_dinamica
        return lambda inst: executar_programacao_dinamica(inst, versao="otimizada")

    # Algoritmos ainda não implementados — placeholders
    else:
        raise NotImplementedError(
            f"Algoritmo '{nome}' ainda não foi implementado. "
            f"Algoritmos disponíveis: {list(ALGORITMOS_DISPONIVEIS.keys())}"
        )


def main():
    """Ponto de entrada principal da CLI."""
    parser = argparse.ArgumentParser(
        description="Problema da Mochila Binária — Execução de Algoritmos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py --algoritmo prog_dinamica --gerar 15 --seed 42
  python main.py --algoritmo prog_dinamica --arquivo ../instancias/inst.json
  python main.py --listar-algoritmos
        """,
    )

    parser.add_argument(
        "--algoritmo", "-a",
        choices=list(ALGORITMOS_DISPONIVEIS.keys()),
        help="Nome do algoritmo a executar.",
    )
    parser.add_argument(
        "--arquivo", "-f",
        help="Caminho para o arquivo JSON com a instância.",
    )
    parser.add_argument(
        "--gerar", "-g",
        type=int,
        metavar="N",
        help="Gerar instância aleatória com N itens.",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Seed para geração aleatória (padrão: 42).",
    )
    parser.add_argument(
        "--capacidade-fracao",
        type=float,
        default=0.5,
        help="Fração da soma de pesos para capacidade (padrão: 0.5).",
    )
    parser.add_argument(
        "--repeticoes",
        type=int,
        default=1,
        help="Número de repetições para medição de tempo (padrão: 1).",
    )
    parser.add_argument(
        "--listar-algoritmos",
        action="store_true",
        help="Lista os algoritmos disponíveis e sai.",
    )
    parser.add_argument(
        "--exibir-instancia",
        action="store_true",
        help="Exibe detalhes da instância antes da execução.",
    )

    args = parser.parse_args()

    # Listar algoritmos disponíveis
    if args.listar_algoritmos:
        print("Algoritmos disponíveis:")
        for chave, descricao in ALGORITMOS_DISPONIVEIS.items():
            print(f"  {chave:<30} — {descricao}")
        return

    # Validação: algoritmo é obrigatório para execução
    if not args.algoritmo:
        parser.error("É necessário especificar --algoritmo ou --listar-algoritmos.")

    # Validação: uma fonte de instância é obrigatória
    if not args.arquivo and args.gerar is None:
        parser.error("Especifique --arquivo ou --gerar N para fornecer uma instância.")

    # Carregar ou gerar instância
    if args.arquivo:
        print(f"Carregando instância de: {args.arquivo}")
        instancia = carregar_instancia(args.arquivo)
    else:
        print(f"Gerando instância com n={args.gerar}, seed={args.seed}")
        instancia = gerar_instancia(
            n=args.gerar,
            seed=args.seed,
            fracao_capacidade=args.capacidade_fracao,
        )

    # Exibir instância se solicitado
    if args.exibir_instancia:
        imprimir_instancia(instancia)

    # Carregar e executar o algoritmo
    try:
        funcao_exec = carregar_algoritmo(args.algoritmo)
    except NotImplementedError as e:
        print(f"\n✗ {e}")
        sys.exit(1)

    print(f"\nExecutando: {ALGORITMOS_DISPONIVEIS[args.algoritmo]}")
    print(f"  n = {instancia['n']}, W = {instancia['capacidade']}")
    print("-" * 50)

    resultado = funcao_exec(instancia)
    print(resultado)


if __name__ == "__main__":
    main()
