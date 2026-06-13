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
        nome="Exemplo clássico (4 itens)",
        pesos=[2, 3, 4, 5],
        valores=[3, 4, 5, 6],
        capacidade=8,
        valor_otimo=11,  # Itens {0, 2, 3} → peso=11? Não. Itens {1,3} → 4+6=10, peso=8.
        # Recalculando: Item 0(p=2,v=3), Item 2(p=4,v=5), Item 1(p=3,v=4) = p=9>8.
        # Item 0(p=2,v=3) + Item 3(p=5,v=6) = p=7, v=9. Cabe mais Item 1(p=3)? 7+3=10>8. Não.
        # Item 1(p=3,v=4) + Item 3(p=5,v=6) = p=8, v=10.
        # Item 0(p=2,v=3) + Item 2(p=4,v=5) = p=6, v=8. + Item 1? 6+3=9>8.
        # Item 0(p=2,v=3) + Item 1(p=3,v=4) + Item 2(p=4,v=5) = p=9>8.
        # Item 0+1 = p=5,v=7. + Item 3? 5+5=10>8.
        # Melhor: {1,3} = 10. Vamos corrigir.
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
        nome="Um único item que cabe",
        pesos=[5],
        valores=[10],
        capacidade=5,
        valor_otimo=10,
    ),
    InstanciaTeste(
        nome="Um único item que NÃO cabe",
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

# Corrige o valor ótimo da primeira instância
INSTANCIAS_TESTE[0].valor_otimo = 10  # Itens {1, 3}, peso=8, valor=10


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
# Ponto de entrada para execução direta
# ===================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
