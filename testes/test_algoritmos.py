"""
Testes Unitários para os Algoritmos da Mochila Binária
========================================================

Verifica a corretude dos algoritmos comparando seus resultados com
soluções conhecidas (instâncias pequenas resolvidas manualmente) e
entre si (todos os algoritmos exatos devem encontrar o mesmo valor ótimo).

Para executar:
    python -m pytest testes/test_algoritmos.py -v

Autor: Projeto APA — Problema da Mochila Binária
"""

import sys
import os
import warnings

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from instrumentacao import Contador, ResultadoAlgoritmo
from gerador_instancias import gerar_instancia, salvar_instancia, carregar_instancia
from prog_dinamica import (
    programacao_dinamica,
    programacao_dinamica_espaco_otimizado,
    executar_programacao_dinamica,
)
from forca_bruta import forca_bruta, executar_forca_bruta
from backtracking import backtracking, executar_backtracking
from divisao_conquista import divisao_conquista, executar_divisao_conquista
from guloso import guloso, executar_guloso
from heuristica import fptas, executar_heuristica_fptas


# ===================================================================
# Instâncias de teste com solução conhecida
# ===================================================================

class InstanciaTeste:
    """Agrupa uma instância de teste com sua solução conhecida."""

    def __init__(self, nome, pesos, valores, capacidade, valor_otimo):
        self.nome = nome
        self.pesos = pesos
        self.valores = valores
        self.capacidade = capacidade
        self.valor_otimo = valor_otimo
        self.instancia = {
            "n": len(pesos),
            "capacidade": capacidade,
            "pesos": pesos,
            "valores": valores,
        }


# Instâncias manuais para validação
INSTANCIAS_TESTE = [
    InstanciaTeste(
        nome="Exemplo classico (4 itens)",
        pesos=[2, 3, 4, 5],
        valores=[3, 4, 5, 6],
        capacidade=8,
        valor_otimo=10,  # Itens {1, 3}, peso=8, valor=10
    ),
    InstanciaTeste(
        nome="Mochila vazia (capacidade 0)",
        pesos=[5, 10, 15],
        valores=[10, 20, 30],
        capacidade=0,
        valor_otimo=0,
    ),
    InstanciaTeste(
        nome="Todos os itens cabem",
        pesos=[1, 2, 3],
        valores=[10, 20, 30],
        capacidade=100,
        valor_otimo=60,
    ),
    InstanciaTeste(
        nome="Um unico item que cabe",
        pesos=[5],
        valores=[10],
        capacidade=5,
        valor_otimo=10,
    ),
    InstanciaTeste(
        nome="Um unico item que NAO cabe",
        pesos=[10],
        valores=[100],
        capacidade=5,
        valor_otimo=0,
    ),
    InstanciaTeste(
        nome="Itens com mesmo peso e valor",
        pesos=[3, 3, 3, 3],
        valores=[5, 5, 5, 5],
        capacidade=9,
        valor_otimo=15,  # 3 itens de peso 3 = 9
    ),
]


# ===================================================================
# Testes do Contador de Instruções
# ===================================================================

class TestContador:
    """Testes para a classe Contador de instrumentação."""

    def test_inicializacao_zerada(self):
        """Todos os contadores devem iniciar em zero."""
        c = Contador()
        assert c.comparacoes == 0
        assert c.somas == 0
        assert c.acessos == 0
        assert c.total == 0

    def test_incremento_e_total(self):
        """Total deve ser a soma de todas as categorias."""
        c = Contador()
        c.comparacoes = 10
        c.somas = 20
        c.acessos = 30
        assert c.total == 60

    def test_detalhes(self):
        """Método detalhes() deve retornar dicionário correto."""
        c = Contador()
        c.comparacoes = 5
        c.somas = 3
        c.acessos = 7
        d = c.detalhes()
        assert d == {"comparacoes": 5, "somas": 3, "acessos": 7, "total": 15}

    def test_resetar(self):
        """Resetar deve zerar todos os contadores."""
        c = Contador()
        c.comparacoes = 100
        c.somas = 200
        c.acessos = 300
        c.resetar()
        assert c.total == 0


# ===================================================================
# Testes do Gerador de Instâncias
# ===================================================================

class TestGeradorInstancias:
    """Testes para o gerador de instâncias."""

    def test_tamanho_correto(self):
        """Instância deve ter o número correto de itens."""
        inst = gerar_instancia(n=20, seed=42)
        assert inst["n"] == 20
        assert len(inst["pesos"]) == 20
        assert len(inst["valores"]) == 20

    def test_reprodutibilidade(self):
        """Mesma seed deve gerar a mesma instância."""
        inst1 = gerar_instancia(n=15, seed=123)
        inst2 = gerar_instancia(n=15, seed=123)
        assert inst1["pesos"] == inst2["pesos"]
        assert inst1["valores"] == inst2["valores"]
        assert inst1["capacidade"] == inst2["capacidade"]

    def test_capacidade_positiva(self):
        """Capacidade deve ser pelo menos 1."""
        inst = gerar_instancia(n=5, seed=0)
        assert inst["capacidade"] >= 1

    def test_fracao_capacidade(self):
        """Capacidade deve ser aproximadamente a fração da soma dos pesos."""
        inst = gerar_instancia(n=100, seed=42, fracao_capacidade=0.5)
        soma_pesos = sum(inst["pesos"])
        # Tolerância: capacidade = int(soma * 0.5), pode diferir por truncamento
        assert abs(inst["capacidade"] - int(soma_pesos * 0.5)) <= 1

    def test_validacao_parametros(self):
        """Parâmetros inválidos devem gerar ValueError."""
        with pytest.raises(ValueError):
            gerar_instancia(n=0)
        with pytest.raises(ValueError):
            gerar_instancia(n=5, peso_min=100, peso_max=1)
        with pytest.raises(ValueError):
            gerar_instancia(n=5, fracao_capacidade=0)
        with pytest.raises(ValueError):
            gerar_instancia(n=5, fracao_capacidade=1.5)

    def test_salvar_e_carregar(self, tmp_path):
        """Salvar e carregar devem preservar todos os dados."""
        inst_original = gerar_instancia(n=10, seed=99)
        caminho = str(tmp_path / "teste.json")

        salvar_instancia(inst_original, caminho)
        inst_carregada = carregar_instancia(caminho)

        assert inst_carregada["n"] == inst_original["n"]
        assert inst_carregada["pesos"] == inst_original["pesos"]
        assert inst_carregada["valores"] == inst_original["valores"]
        assert inst_carregada["capacidade"] == inst_original["capacidade"]


# ===================================================================
# Testes da Programação Dinâmica
# ===================================================================

class TestProgramacaoDinamica:
    """Testes para o algoritmo de Programação Dinâmica."""

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_valor_otimo_tabela(self, instancia_teste):
        """Tabela completa deve encontrar o valor ótimo correto."""
        valor, itens, peso = programacao_dinamica(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        assert valor == instancia_teste.valor_otimo, (
            f"Esperado {instancia_teste.valor_otimo}, obteve {valor}"
        )

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_valor_otimo_espaco_otimizado(self, instancia_teste):
        """Versão otimizada deve encontrar o mesmo valor ótimo."""
        valor, itens, peso = programacao_dinamica_espaco_otimizado(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        assert valor == instancia_teste.valor_otimo, (
            f"Esperado {instancia_teste.valor_otimo}, obteve {valor}"
        )

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_peso_nao_excede_capacidade(self, instancia_teste):
        """Peso total dos itens selecionados não deve exceder a capacidade."""
        _, itens, peso = programacao_dinamica(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        assert peso <= instancia_teste.capacidade

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_valor_corresponde_aos_itens(self, instancia_teste):
        """Valor retornado deve ser a soma dos valores dos itens selecionados."""
        valor, itens, peso = programacao_dinamica(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        valor_calculado = sum(instancia_teste.valores[i] for i in itens)
        assert valor == valor_calculado

    def test_concordancia_tabela_vs_otimizada(self):
        """Ambas as versões devem encontrar o mesmo valor para instâncias aleatórias."""
        for seed in range(10):
            inst = gerar_instancia(n=20, seed=seed)
            v1, _, _ = programacao_dinamica(
                inst["pesos"], inst["valores"], inst["capacidade"]
            )
            v2, _, _ = programacao_dinamica_espaco_otimizado(
                inst["pesos"], inst["valores"], inst["capacidade"]
            )
            assert v1 == v2, f"Seed {seed}: tabela={v1}, otimizada={v2}"

    def test_contagem_instrucoes_nao_zerada(self):
        """Contador de instruções deve registrar operações."""
        inst = gerar_instancia(n=10, seed=42)
        contador = Contador()
        programacao_dinamica(
            inst["pesos"], inst["valores"], inst["capacidade"], contador
        )
        assert contador.total > 0
        assert contador.comparacoes > 0
        assert contador.somas > 0
        assert contador.acessos > 0

    def test_resultado_padronizado(self):
        """executar_programacao_dinamica deve retornar ResultadoAlgoritmo."""
        inst = gerar_instancia(n=10, seed=42)
        resultado = executar_programacao_dinamica(inst)
        assert isinstance(resultado, ResultadoAlgoritmo)
        assert resultado.valor > 0
        assert resultado.tempo_execucao >= 0
        assert resultado.num_instrucoes > 0
        assert len(resultado.nome_algoritmo) > 0


# ===================================================================
# Testes da Forca Bruta
# ===================================================================

class TestForcaBruta:
    """Testes para o algoritmo de Forca Bruta."""

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_valor_otimo(self, instancia_teste):
        """Forca Bruta deve encontrar o valor otimo correto."""
        valor, itens, peso = forca_bruta(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        assert valor == instancia_teste.valor_otimo, (
            f"Esperado {instancia_teste.valor_otimo}, obteve {valor}"
        )

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_peso_nao_excede_capacidade(self, instancia_teste):
        """Peso dos itens selecionados nao deve exceder a capacidade."""
        _, itens, peso = forca_bruta(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        assert peso <= instancia_teste.capacidade

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_valor_corresponde_aos_itens(self, instancia_teste):
        """Valor retornado deve ser a soma dos valores dos itens selecionados."""
        valor, itens, peso = forca_bruta(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        valor_calculado = sum(instancia_teste.valores[i] for i in itens)
        assert valor == valor_calculado

    def test_contagem_instrucoes_nao_zerada(self):
        """Contador de instrucoes deve registrar operacoes."""
        inst = gerar_instancia(n=10, seed=42)
        contador = Contador()
        forca_bruta(
            inst["pesos"], inst["valores"], inst["capacidade"], contador
        )
        assert contador.total > 0
        assert contador.comparacoes > 0

    def test_resultado_padronizado(self):
        """executar_forca_bruta deve retornar ResultadoAlgoritmo."""
        inst = gerar_instancia(n=10, seed=42)
        resultado = executar_forca_bruta(inst)
        assert isinstance(resultado, ResultadoAlgoritmo)
        assert resultado.valor > 0
        assert resultado.tempo_execucao >= 0
        assert resultado.num_instrucoes > 0

    def test_warning_n_grande(self):
        """Deve emitir RuntimeWarning quando n excede o limite recomendado."""
        inst = gerar_instancia(n=5, seed=0)
        # Simula n grande alterando a lista (nao vamos rodar n=25 no teste)
        import forca_bruta as fb
        limite_original = fb.N_MAXIMO_RECOMENDADO
        try:
            fb.N_MAXIMO_RECOMENDADO = 3  # Temporariamente reduz o limite
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                forca_bruta(inst["pesos"], inst["valores"], inst["capacidade"])
                assert len(w) == 1
                assert issubclass(w[0].category, RuntimeWarning)
                assert "excede o limite recomendado" in str(w[0].message)
        finally:
            fb.N_MAXIMO_RECOMENDADO = limite_original


# ===================================================================
# Testes do Backtracking
# ===================================================================

class TestBacktracking:
    """Testes para o algoritmo de Backtracking."""

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_valor_otimo(self, instancia_teste):
        """Backtracking deve encontrar o valor otimo correto."""
        valor, itens, peso, _ = backtracking(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        assert valor == instancia_teste.valor_otimo, (
            f"Esperado {instancia_teste.valor_otimo}, obteve {valor}"
        )

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_peso_nao_excede_capacidade(self, instancia_teste):
        """Peso dos itens selecionados nao deve exceder a capacidade."""
        _, itens, peso, _ = backtracking(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        assert peso <= instancia_teste.capacidade

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_valor_corresponde_aos_itens(self, instancia_teste):
        """Valor retornado deve ser a soma dos valores dos itens selecionados."""
        valor, itens, peso, _ = backtracking(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        valor_calculado = sum(instancia_teste.valores[i] for i in itens)
        assert valor == valor_calculado

    def test_estatisticas_poda_presentes(self):
        """Backtracking deve retornar estatisticas de poda."""
        inst = gerar_instancia(n=10, seed=42)
        _, _, _, estatisticas = backtracking(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        assert "nodos_visitados" in estatisticas
        assert "podas_viabilidade" in estatisticas
        assert "podas_bound" in estatisticas
        assert estatisticas["nodos_visitados"] > 0

    def test_poda_reduz_espaco_busca(self):
        """Backtracking deve visitar menos nos que 2^(n+1)-1 (arvore completa)."""
        inst = gerar_instancia(n=15, seed=42)
        _, _, _, estatisticas = backtracking(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        arvore_completa = 2 ** (inst["n"] + 1) - 1
        assert estatisticas["nodos_visitados"] < arvore_completa, (
            f"Visitou {estatisticas['nodos_visitados']} nos, mas a arvore "
            f"completa tem {arvore_completa}. As podas nao estao funcionando."
        )

    def test_contagem_instrucoes_nao_zerada(self):
        """Contador de instrucoes deve registrar operacoes."""
        inst = gerar_instancia(n=10, seed=42)
        contador = Contador()
        backtracking(
            inst["pesos"], inst["valores"], inst["capacidade"], contador
        )
        assert contador.total > 0
        assert contador.comparacoes > 0

    def test_resultado_padronizado_com_poda(self):
        """executar_backtracking deve retornar ResultadoAlgoritmo com estatisticas."""
        inst = gerar_instancia(n=10, seed=42)
        resultado = executar_backtracking(inst)
        assert isinstance(resultado, ResultadoAlgoritmo)
        assert resultado.valor > 0
        assert hasattr(resultado, "estatisticas_poda")
        assert resultado.estatisticas_poda["nodos_visitados"] > 0

    def test_warning_n_grande(self):
        """Deve emitir RuntimeWarning quando n excede o limite recomendado."""
        inst = gerar_instancia(n=5, seed=0)
        import backtracking as bt
        limite_original = bt.N_MAXIMO_RECOMENDADO
        try:
            bt.N_MAXIMO_RECOMENDADO = 3
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                backtracking(inst["pesos"], inst["valores"], inst["capacidade"])
                assert len(w) == 1
                assert issubclass(w[0].category, RuntimeWarning)
                assert "excede o limite recomendado" in str(w[0].message)
        finally:
            bt.N_MAXIMO_RECOMENDADO = limite_original


# ===================================================================
# Testes de Divisao e Conquista
# ===================================================================

class TestDivisaoConquista:
    """Testes para o algoritmo de Divisao e Conquista."""

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_valor_otimo(self, instancia_teste):
        """D&C deve encontrar o valor otimo correto."""
        valor, itens, peso = divisao_conquista(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        assert valor == instancia_teste.valor_otimo, (
            f"Esperado {instancia_teste.valor_otimo}, obteve {valor}"
        )

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_peso_nao_excede_capacidade(self, instancia_teste):
        """Peso dos itens selecionados nao deve exceder a capacidade."""
        _, itens, peso = divisao_conquista(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        assert peso <= instancia_teste.capacidade

    @pytest.mark.parametrize("instancia_teste", INSTANCIAS_TESTE,
                             ids=[i.nome for i in INSTANCIAS_TESTE])
    def test_valor_corresponde_aos_itens(self, instancia_teste):
        """Valor retornado deve ser a soma dos valores dos itens selecionados."""
        valor, itens, peso = divisao_conquista(
            instancia_teste.pesos,
            instancia_teste.valores,
            instancia_teste.capacidade,
        )
        valor_calculado = sum(instancia_teste.valores[i] for i in itens)
        assert valor == valor_calculado

    def test_contagem_instrucoes_nao_zerada(self):
        """Contador de instrucoes deve registrar operacoes."""
        inst = gerar_instancia(n=10, seed=42)
        contador = Contador()
        divisao_conquista(
            inst["pesos"], inst["valores"], inst["capacidade"], contador
        )
        assert contador.total > 0
        assert contador.comparacoes > 0

    def test_resultado_padronizado(self):
        """executar_divisao_conquista deve retornar ResultadoAlgoritmo."""
        inst = gerar_instancia(n=10, seed=42)
        resultado = executar_divisao_conquista(inst)
        assert isinstance(resultado, ResultadoAlgoritmo)
        assert resultado.valor > 0
        assert resultado.tempo_execucao >= 0
        assert resultado.num_instrucoes > 0

    def test_warning_n_grande(self):
        """Deve emitir RuntimeWarning quando n excede o limite recomendado."""
        inst = gerar_instancia(n=5, seed=0)
        import divisao_conquista as dc
        limite_original = dc.N_MAXIMO_RECOMENDADO
        try:
            dc.N_MAXIMO_RECOMENDADO = 3
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                divisao_conquista(inst["pesos"], inst["valores"], inst["capacidade"])
                assert len(w) == 1
                assert issubclass(w[0].category, RuntimeWarning)
                assert "excede o limite" in str(w[0].message)
        finally:
            dc.N_MAXIMO_RECOMENDADO = limite_original


# ===================================================================
# Validacao cruzada: FB vs BT vs D&C vs PD (4 algoritmos exatos)
# ===================================================================

# Instancias aleatorias com seeds fixas para validacao cruzada.
# Essencial para a documentacao: afirmar que os quatro algoritmos exatos
# sao equivalentes em corretude.
SEEDS_VALIDACAO_CRUZADA = [7, 13, 42, 99, 256]
TAMANHOS_VALIDACAO = [5, 8, 10, 12, 15]


class TestValidacaoCruzada:
    """
    Validacao cruzada entre os quatro algoritmos exatos.

    Verifica que Forca Bruta, Backtracking, Divisao e Conquista e
    Programacao Dinamica encontram exatamente o mesmo valor otimo
    para as mesmas instancias. Este teste e fundamental para garantir
    corretude e sera referenciado na secao de Analise de Resultados.
    """

    @pytest.mark.parametrize(
        "n, seed",
        [(n, s) for n, s in zip(TAMANHOS_VALIDACAO, SEEDS_VALIDACAO_CRUZADA)],
        ids=[f"n={n}_seed={s}" for n, s in zip(TAMANHOS_VALIDACAO, SEEDS_VALIDACAO_CRUZADA)],
    )
    def test_quatro_algoritmos_mesmo_valor(self, n, seed):
        """FB, BT, D&C e PD devem encontrar o mesmo valor otimo."""
        inst = gerar_instancia(n=n, seed=seed)

        valor_pd, _, _ = programacao_dinamica(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        valor_fb, _, _ = forca_bruta(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        valor_bt, _, _, _ = backtracking(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        valor_dc, _, _ = divisao_conquista(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )

        assert valor_pd == valor_fb, (
            f"PD ({valor_pd}) != FB ({valor_fb}) para n={n}, seed={seed}"
        )
        assert valor_pd == valor_bt, (
            f"PD ({valor_pd}) != BT ({valor_bt}) para n={n}, seed={seed}"
        )
        assert valor_pd == valor_dc, (
            f"PD ({valor_pd}) != D&C ({valor_dc}) para n={n}, seed={seed}"
        )

    @pytest.mark.parametrize(
        "n, seed",
        [(n, s) for n, s in zip(TAMANHOS_VALIDACAO, SEEDS_VALIDACAO_CRUZADA)],
        ids=[f"n={n}_seed={s}" for n, s in zip(TAMANHOS_VALIDACAO, SEEDS_VALIDACAO_CRUZADA)],
    )
    def test_pesos_solucoes_viaveis(self, n, seed):
        """Todas as solucoes dos quatro algoritmos devem respeitar a capacidade."""
        inst = gerar_instancia(n=n, seed=seed)
        W = inst["capacidade"]

        _, _, peso_pd = programacao_dinamica(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        _, _, peso_fb = forca_bruta(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        _, _, peso_bt, _ = backtracking(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        _, _, peso_dc = divisao_conquista(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )

        assert peso_pd <= W, f"PD: peso {peso_pd} > capacidade {W}"
        assert peso_fb <= W, f"FB: peso {peso_fb} > capacidade {W}"
        assert peso_bt <= W, f"BT: peso {peso_bt} > capacidade {W}"
        assert peso_dc <= W, f"D&C: peso {peso_dc} > capacidade {W}"

    def test_backtracking_menos_instrucoes_que_forca_bruta(self):
        """Backtracking deve usar menos instrucoes que Forca Bruta (poda eficaz)."""
        inst = gerar_instancia(n=15, seed=42)

        contador_fb = Contador()
        forca_bruta(inst["pesos"], inst["valores"], inst["capacidade"], contador_fb)

        contador_bt = Contador()
        backtracking(inst["pesos"], inst["valores"], inst["capacidade"], contador_bt)

        assert contador_bt.total < contador_fb.total, (
            f"Backtracking ({contador_bt.total:,}) nao reduziu instrucoes "
            f"comparado a Forca Bruta ({contador_fb.total:,})"
        )

    def test_dc_mesma_ordem_grandeza_que_forca_bruta(self):
        """D&C e FB devem ter instrucoes na mesma ordem de grandeza (ambos O(2^n)).

        Como nenhum dos dois aplica podas, o numero de instrucoes deve ser
        similar. Verificamos que a razao entre eles esta entre 0.1 e 10
        (mesma ordem de grandeza), sustentando a afirmacao na documentacao
        de que ambos sao O(2^n) na pratica.
        """
        inst = gerar_instancia(n=15, seed=42)

        contador_fb = Contador()
        forca_bruta(inst["pesos"], inst["valores"], inst["capacidade"], contador_fb)

        contador_dc = Contador()
        divisao_conquista(inst["pesos"], inst["valores"], inst["capacidade"], contador_dc)

        razao = contador_dc.total / contador_fb.total
        assert 0.1 <= razao <= 10.0, (
            f"D&C ({contador_dc.total:,}) e FB ({contador_fb.total:,}) "
            f"diferem em mais de uma ordem de grandeza (razao={razao:.2f}). "
            f"Ambos deveriam ser O(2^n)."
        )


# ===================================================================
# Testes do Algoritmo Guloso
# ===================================================================

class TestGuloso:
    """Testes para a heuristica Gulosa (Razao Valor/Peso)."""

    def test_instancia_falha_guloso(self):
        """Verifica a instancia documentada onde o guloso falha."""
        pesos = [6, 5, 5]
        valores = [8, 5, 5]
        capacidade = 10
        
        valor_guloso, itens_guloso, peso_guloso = guloso(pesos, valores, capacidade)
        
        # O guloso pega o item 0 (razao 1.33) e nao consegue pegar mais nada
        assert valor_guloso == 8
        assert itens_guloso == [0]
        assert peso_guloso == 6
        
        # O otimo seria pegar itens 1 e 2 (valor 10)
        valor_pd, _, _ = programacao_dinamica(pesos, valores, capacidade)
        assert valor_pd == 10
        assert valor_guloso < valor_pd, "Guloso deveria ser subotimo nesta instancia."

    @pytest.mark.parametrize(
        "n, seed",
        [(n, s) for n, s in zip(TAMANHOS_VALIDACAO, SEEDS_VALIDACAO_CRUZADA)],
        ids=[f"n={n}_seed={s}" for n, s in zip(TAMANHOS_VALIDACAO, SEEDS_VALIDACAO_CRUZADA)],
    )
    def test_guloso_nunca_supera_otimo(self, n, seed):
        """Guloso e admissivel quanto a capacidade, mas valor <= otimo."""
        inst = gerar_instancia(n=n, seed=seed)
        W = inst["capacidade"]

        valor_pd, _, _ = programacao_dinamica(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        valor_guloso, _, peso_guloso = guloso(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )

        assert peso_guloso <= W, f"Guloso excedeu a capacidade: {peso_guloso} > {W}"
        assert valor_guloso <= valor_pd, (
            f"Guloso ({valor_guloso}) superou o otimo da PD ({valor_pd})? Impossivel!"
        )


# ===================================================================
# Testes do FPTAS
# ===================================================================

class TestHeuristica:
    """Testes para o FPTAS por escalonamento de valores."""

    @pytest.mark.parametrize(
        "n, seed",
        [(10, 42), (12, 99), (15, 256)]
    )
    @pytest.mark.parametrize("epsilon", [0.01, 0.1, 0.3, 0.5])
    def test_garantia_teorica_fptas(self, n, seed, epsilon):
        """FPTAS deve garantir valor >= (1 - epsilon) * otimo."""
        inst = gerar_instancia(n=n, seed=seed)
        W = inst["capacidade"]

        valor_pd, _, _ = programacao_dinamica(
            inst["pesos"], inst["valores"], inst["capacidade"]
        )
        
        valor_fptas, _, peso_fptas, eps_usado, K = fptas(
            inst["pesos"], inst["valores"], inst["capacidade"], epsilon=epsilon
        )

        # 1. Deve respeitar a capacidade
        assert peso_fptas <= W
        
        # 2. Garantia teorica de aproximacao
        import math
        garantia = math.ceil(valor_pd * (1 - epsilon))
        assert valor_fptas >= garantia, (
            f"Falhou garantia: otimo={valor_pd}, epsilon={epsilon}, "
            f"garantido={garantia}, obteve={valor_fptas}"
        )
        
        # 3. Nunca superar o otimo (sao itens reais)
        assert valor_fptas <= valor_pd

    def test_trade_off_epsilon(self):
        """Verifica se epsilon menor resulta em solucao igual ou melhor (porem mais lenta)."""
        inst = gerar_instancia(n=20, seed=12345)
        
        contador_eps_alto = Contador()
        val_eps_alto, _, _, _, _ = fptas(
            inst["pesos"], inst["valores"], inst["capacidade"], 
            epsilon=0.5, contador=contador_eps_alto
        )
        
        contador_eps_baixo = Contador()
        val_eps_baixo, _, _, _, _ = fptas(
            inst["pesos"], inst["valores"], inst["capacidade"], 
            epsilon=0.01, contador=contador_eps_baixo
        )
        
        # Valor com epsilon pequeno deve ser no minimo o mesmo ou melhor
        assert val_eps_baixo >= val_eps_alto
        
        # O FPTAS com epsilon pequeno (0.01) exige uma tabela maior, 
        # logo devera realizar mais instrucoes que o epsilon grande (0.5)
        assert contador_eps_baixo.total > contador_eps_alto.total


# ===================================================================
# Ponto de entrada para execução direta
# ===================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

