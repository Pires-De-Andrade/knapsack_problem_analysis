"""
Script de Análise de Resultados — Problema da Mochila Binária
===============================================================

Gera o material bruto (CSVs) e os gráficos (PNGs) necessários para
a documentação acadêmica do trabalho, analisando os 6 algoritmos
implementados em termos de escalabilidade, qualidade (gap) e
eficácia de poda.

Experimentos:
    1. Escalabilidade: Mede tempo e contagem de instruções vs `n`.
       - Algoritmos Exponenciais (FB, D&C, BT) rodados até n=18 (limite prático).
       - Algoritmos Escaláveis (PD, Guloso, FPTAS) rodados até n grandes.
    2. Qualidade e Gap de Otimalidade:
       - FPTAS: Varia o epsilon para mostrar o trade-off tempo vs erro.
       - Guloso: Usa instâncias adversariais projetadas para forçar o
         guloso a falhar (subotimalidade máxima).
    3. Eficácia de Poda (Backtracking):
       - Registra nodos visitados vs espaço total 2^n.

Autor: Projeto APA
"""

import os
import csv
import math
import argparse
import time
import matplotlib.pyplot as plt

# Importa os algoritmos e utils
from gerador_instancias import gerar_instancia
from instrumentacao import Contador, ResultadoAlgoritmo

from prog_dinamica import executar_programacao_dinamica
from forca_bruta import executar_forca_bruta, N_MAXIMO_RECOMENDADO as MAX_FB
from divisao_conquista import executar_divisao_conquista, N_MAXIMO_RECOMENDADO as MAX_DC
from backtracking import executar_backtracking, N_MAXIMO_RECOMENDADO as MAX_BT
from guloso import executar_guloso
from heuristica import executar_heuristica_fptas

# Limites para testes rapidos (ajustaveis via CLI, mas padrao para teste agil)
LIMITE_EXPONENCIAL = 18

# Garante a existencia das pastas
os.makedirs("resultados/csv", exist_ok=True)
os.makedirs("resultados/graficos", exist_ok=True)


def gerar_instancia_adversarial(n: int) -> dict:
    """
    Gera uma instancia construida de forma adversarial para o algoritmo Guloso.

    Estrategia:
    Criar um "Item Armadilha" (Item 0) que tem a melhor razao valor/peso,
    porem seu peso ocupa um pouco mais da metade da mochila.
    Os demais itens (1 a n-1) tem uma razao ligeiramente menor, mas somados
    ocupam quase 100% da mochila e entregam um valor total muito maior.

    O Guloso vai "morder a isca", pegar o Item 0 e ficar com uma capacidade
    restante que nao permite pegar muitos dos itens bons, resultando num
    valor final bem abaixo do otimo.
    """
    W = 100 * (n - 1)
    pesos = []
    valores = []
    
    # Item 0 (armadilha pro guloso)
    w0 = (W // 2) + 1
    v0 = int(w0 * 1.5)  # Razao ~ 1.5
    pesos.append(w0)
    valores.append(v0)
    
    # Itens 1 a n-1 (solucao otima)
    w_outros = W // (n - 1)
    v_outros = int(w_outros * 1.4)  # Razao ~ 1.4
    for _ in range(n - 1):
        pesos.append(w_outros)
        valores.append(v_outros)
        
    return {
        "n": n,
        "capacidade": W,
        "pesos": pesos,
        "valores": valores
    }


def rodar_experimento_escalabilidade(ns_exponenciais, ns_escalaveis, repeticoes=3):
    print("\n--- INICIANDO EXPERIMENTO 1: ESCALABILIDADE ---")
    caminho_csv = "resultados/csv/escalabilidade.csv"
    
    algoritmos_expo = [
        ("Forca Bruta", executar_forca_bruta, LIMITE_EXPONENCIAL),
        ("Divisao e Conquista", executar_divisao_conquista, LIMITE_EXPONENCIAL),
        ("Backtracking", executar_backtracking, LIMITE_EXPONENCIAL),
    ]
    
    algoritmos_escala = [
        ("Prog Dinamica", executar_programacao_dinamica),
        ("Guloso", executar_guloso),
        ("FPTAS (e=0.1)", lambda inst, repeticoes_tempo=1: executar_heuristica_fptas(inst, repeticoes_tempo, epsilon=0.1)),
    ]

    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "algoritmo", "n", "capacidade", "seed", "tempo_medio", 
            "instrucoes", "valor_encontrado", "valor_otimo_pd", "gap_percentual"
        ])
        
        # Unifica todos os Ns para processar PD apenas uma vez por N
        todos_ns = sorted(list(set(ns_exponenciais + ns_escalaveis)))
        
        for n in todos_ns:
            seed = 42 + n
            inst = gerar_instancia(n=n, seed=seed)
            print(f"Gerada instancia n={n}, W={inst['capacidade']}")
            
            # Obtem otimo via PD para calcular o gap
            res_pd = executar_programacao_dinamica(inst, repeticoes_tempo=repeticoes)
            otimo = res_pd.valor
            
            # Grava PD se este N faz parte da lista de escalaveis
            if n in ns_escalaveis:
                writer.writerow([
                    "Prog Dinamica", n, inst["capacidade"], seed, 
                    res_pd.tempo_execucao, res_pd.num_instrucoes, 
                    res_pd.valor, otimo, 0.0
                ])
                print(f"  Prog Dinamica: {res_pd.tempo_execucao:.4f}s")
            
            # Algoritmos Exponenciais
            if n in ns_exponenciais:
                for nome, func, limite in algoritmos_expo:
                    if n <= limite:
                        res = func(inst, repeticoes_tempo=repeticoes)
                        gap = ((otimo - res.valor) / otimo) * 100 if otimo > 0 else 0
                        writer.writerow([
                            nome, n, inst["capacidade"], seed, 
                            res.tempo_execucao, res.num_instrucoes, 
                            res.valor, otimo, gap
                        ])
                        print(f"  {nome}: {res.tempo_execucao:.4f}s")
                    else:
                        print(f"  {nome}: ignorado (n > limite)")

            # Outros Algoritmos Escalaveis
            if n in ns_escalaveis:
                for nome, func in algoritmos_escala[1:]: # Pula PD que ja foi
                    res = func(inst, repeticoes_tempo=repeticoes)
                    gap = ((otimo - res.valor) / otimo) * 100 if otimo > 0 else 0
                    writer.writerow([
                        nome, n, inst["capacidade"], seed, 
                        res.tempo_execucao, res.num_instrucoes, 
                        res.valor, otimo, gap
                    ])
                    print(f"  {nome}: {res.tempo_execucao:.4f}s (Gap: {gap:.1f}%)")


def rodar_experimento_qualidade(ns_adversariais, epsilons_fptas):
    print("\n--- INICIANDO EXPERIMENTO 2: QUALIDADE (GAP) ---")
    caminho_csv = "resultados/csv/qualidade.csv"
    
    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "experimento", "n", "algoritmo", "epsilon", "tempo",
            "valor_encontrado", "valor_otimo", "gap_percentual"
        ])
        
        # 2a. Instancias Adversariais pro Guloso
        print("  Testando Guloso em Instancias Adversariais...")
        for n in ns_adversariais:
            inst = gerar_instancia_adversarial(n)
            res_pd = executar_programacao_dinamica(inst)
            otimo = res_pd.valor
            
            res_guloso = executar_guloso(inst)
            gap = ((otimo - res_guloso.valor) / otimo) * 100 if otimo > 0 else 0
            
            writer.writerow([
                "Adversarial_Guloso", n, "Guloso", "", res_guloso.tempo_execucao,
                res_guloso.valor, otimo, gap
            ])
            print(f"    n={n}: Otimo={otimo}, Guloso={res_guloso.valor} -> Gap {gap:.1f}%")
            
        # 2b. Trade-off do FPTAS com variacao de epsilon
        print("  Testando FPTAS com diferentes Epsilons...")
        inst_fptas = gerar_instancia(n=25, seed=100)
        res_pd = executar_programacao_dinamica(inst_fptas)
        otimo = res_pd.valor
        
        for eps in epsilons_fptas:
            res_fptas = executar_heuristica_fptas(inst_fptas, epsilon=eps)
            gap = ((otimo - res_fptas.valor) / otimo) * 100 if otimo > 0 else 0
            writer.writerow([
                "Epsilon_FPTAS", inst_fptas["n"], "FPTAS", eps, res_fptas.tempo_execucao,
                res_fptas.valor, otimo, gap
            ])
            print(f"    Eps={eps}: Otimo={otimo}, FPTAS={res_fptas.valor} -> Gap {gap:.2f}% (Tempo: {res_fptas.tempo_execucao:.4f}s)")


def rodar_experimento_poda(ns_exponenciais):
    print("\n--- INICIANDO EXPERIMENTO 3: EFICACIA DA PODA ---")
    caminho_csv = "resultados/csv/poda.csv"
    
    with open(caminho_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "n", "seed", "nodos_visitados", "podas_viabilidade", 
            "podas_bound", "espaco_total"
        ])
        
        for n in ns_exponenciais:
            if n > LIMITE_EXPONENCIAL:
                continue
            seed = 99 + n
            inst = gerar_instancia(n=n, seed=seed)
            res_bt = executar_backtracking(inst)
            
            estatisticas = res_bt.estatisticas_poda
            espaco_total = (2 ** (n + 1)) - 1
            
            writer.writerow([
                n, seed, estatisticas["nodos_visitados"], 
                estatisticas["podas_viabilidade"], estatisticas["podas_bound"],
                espaco_total
            ])
            perc = (estatisticas["nodos_visitados"] / espaco_total) * 100
            print(f"  n={n}: {estatisticas['nodos_visitados']} nos visitados "
                  f"de {espaco_total} totais ({perc:.4f}%)")


# ===================================================================
# GERAÇÃO DE GRÁFICOS
# ===================================================================

import pandas as pd

def gerar_graficos():
    print("\n--- GERANDO GRAFICOS COM MATPLOTLIB ---")
    
    # Carrega dados
    try:
        df_esc = pd.read_csv("resultados/csv/escalabilidade.csv")
        df_qual = pd.read_csv("resultados/csv/qualidade.csv")
        df_poda = pd.read_csv("resultados/csv/poda.csv")
    except FileNotFoundError as e:
        print(f"Erro ao carregar CSVs: {e}. Execute os experimentos primeiro.")
        return

    # 1. grafico_tempo_exponenciais.png
    plt.figure(figsize=(10, 6))
    algoritmos_expo = ["Forca Bruta", "Divisao e Conquista", "Backtracking", "Prog Dinamica"]
    for alg in algoritmos_expo:
        dados = df_esc[(df_esc["algoritmo"] == alg) & (df_esc["n"] <= LIMITE_EXPONENCIAL)]
        if not dados.empty:
            plt.plot(dados["n"], dados["tempo_medio"], marker='o', label=alg)
    
    plt.yscale("log")
    plt.title("Tempo de Execução vs N (Algoritmos Exatos)")
    plt.xlabel("Número de Itens (n)")
    plt.ylabel("Tempo (segundos) - Escala Log")
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.tight_layout()
    plt.savefig("resultados/graficos/grafico_tempo_exponenciais.png", dpi=300)
    plt.close()
    
    # 2. grafico_tempo_escalaveis.png
    plt.figure(figsize=(10, 6))
    algoritmos_esc = ["Prog Dinamica", "Guloso", "FPTAS (e=0.1)"]
    for alg in algoritmos_esc:
        dados = df_esc[df_esc["algoritmo"] == alg]
        if not dados.empty:
            plt.plot(dados["n"], dados["tempo_medio"], marker='s', label=alg)
            
    plt.title("Escalabilidade de Tempo vs N (Algoritmos Eficientes)")
    plt.xlabel("Número de Itens (n)")
    plt.ylabel("Tempo (segundos)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("resultados/graficos/grafico_tempo_escalaveis.png", dpi=300)
    plt.close()

    # 3. grafico_instrucoes_exponenciais.png
    plt.figure(figsize=(10, 6))
    for alg in algoritmos_expo:
        dados = df_esc[(df_esc["algoritmo"] == alg) & (df_esc["n"] <= LIMITE_EXPONENCIAL)]
        if not dados.empty:
            plt.plot(dados["n"], dados["instrucoes"], marker='^', label=alg)
            
    plt.yscale("log")
    plt.title("Total de Instruções vs N (Algoritmos Exatos)")
    plt.xlabel("Número de Itens (n)")
    plt.ylabel("Número de Instruções - Escala Log")
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.tight_layout()
    plt.savefig("resultados/graficos/grafico_instrucoes_exponenciais.png", dpi=300)
    plt.close()
    
    # 4. grafico_gap_guloso.png
    plt.figure(figsize=(10, 6))
    dados_guloso = df_qual[df_qual["experimento"] == "Adversarial_Guloso"]
    if not dados_guloso.empty:
        plt.plot(dados_guloso["n"], dados_guloso["gap_percentual"], marker='o', color='red')
        plt.title("Gap de Otimalidade do Guloso em Instâncias Adversariais")
        plt.xlabel("Número de Itens (n)")
        plt.ylabel("Gap em relação ao Ótimo (%)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("resultados/graficos/grafico_gap_guloso.png", dpi=300)
    plt.close()

    # 5. grafico_gap_fptas_epsilon.png
    plt.figure(figsize=(10, 6))
    dados_fptas = df_qual[df_qual["experimento"] == "Epsilon_FPTAS"].sort_values("epsilon")
    if not dados_fptas.empty:
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        color = 'tab:blue'
        ax1.set_xlabel("Epsilon (ε)")
        ax1.set_ylabel("Gap em relação ao Ótimo (%)", color=color)
        ax1.plot(dados_fptas["epsilon"], dados_fptas["gap_percentual"], marker='o', color=color, label="Gap %")
        ax1.tick_params(axis='y', labelcolor=color)
        
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel("Tempo de Execução (s)", color=color)
        ax2.plot(dados_fptas["epsilon"], dados_fptas["tempo"], marker='s', color=color, linestyle='--', label="Tempo (s)")
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.title("Trade-off do FPTAS: Gap e Tempo vs Epsilon (n=25)")
        fig.tight_layout()
        plt.savefig("resultados/graficos/grafico_gap_fptas_epsilon.png", dpi=300)
    plt.close()

    # 6. grafico_eficacia_poda.png
    plt.figure(figsize=(10, 6))
    if not df_poda.empty:
        plt.plot(df_poda["n"], df_poda["espaco_total"], marker='_', label="Espaço Total (2^n)")
        plt.plot(df_poda["n"], df_poda["nodos_visitados"], marker='o', label="Nós Visitados (BT)")
        
        plt.yscale("log")
        plt.title("Eficácia da Poda: Nós Visitados vs Espaço Total")
        plt.xlabel("Número de Itens (n)")
        plt.ylabel("Quantidade de Nós (Escala Log)")
        plt.grid(True, which="both", ls="--")
        plt.legend()
        plt.tight_layout()
        plt.savefig("resultados/graficos/grafico_eficacia_poda.png", dpi=300)
    plt.close()
    
    print("Graficos gerados e salvos em resultados/graficos/")


def main():
    parser = argparse.ArgumentParser(description="Gera dados para a Analise de Resultados.")
    parser.add_argument("--skip-exp", action="store_true", help="Pula os experimentos e gera apenas os graficos.")
    args = parser.parse_args()

    if not args.skip_exp:
        # Configurações de N para os testes
        ns_exponenciais = [4, 6, 8, 10, 12, 14, 16, 18]
        ns_escalaveis = [4, 6, 8, 10, 12, 14, 16, 18, 50, 100, 200, 500, 1000]
        
        ns_adversariais = [5, 10, 20, 50, 100]
        epsilons_fptas = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8]
        
        tempo_inicio = time.time()
        
        rodar_experimento_escalabilidade(ns_exponenciais, ns_escalaveis)
        rodar_experimento_qualidade(ns_adversariais, epsilons_fptas)
        rodar_experimento_poda(ns_exponenciais)
        
        tempo_total = time.time() - tempo_inicio
        print(f"\nExperimentos concluidos em {tempo_total:.2f} segundos.")
    
    gerar_graficos()


if __name__ == "__main__":
    main()
