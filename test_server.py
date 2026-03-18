"""Testes unitários — Fase 1: lógica pura (dados + formatação + resultado)."""

from server import QUESTOES, formatar_questao, calcular_resultado


# ---------- Estrutura de dados ----------

def test_questoes_tem_3_itens():
    assert len(QUESTOES) == 3


def test_questoes_chaves_obrigatorias():
    chaves = {"enunciado", "alternativas", "correta"}
    for q in QUESTOES:
        assert chaves.issubset(q.keys()), f"Faltam chaves em: {q}"


# ---------- formatar_questao ----------

def test_formatar_questao_contem_enunciado():
    q = QUESTOES[0]
    texto = formatar_questao(q)
    assert q["enunciado"] in texto


def test_formatar_questao_contem_alternativas():
    q = QUESTOES[0]
    texto = formatar_questao(q)
    assert q["alternativas"] in texto


def test_formatar_questao_termina_com_prompt():
    texto = formatar_questao(QUESTOES[0])
    assert texto.endswith("Sua resposta: ")


# ---------- calcular_resultado ----------

def test_calcular_resultado_todas_corretas():
    respostas = [q["correta"] for q in QUESTOES]
    resultado = calcular_resultado("Alice", QUESTOES, respostas)
    assert "Acertos: 3/3" in resultado
    assert "Jogador: Alice" in resultado


def test_calcular_resultado_nenhuma_correta():
    respostas = ["X", "X", "X"]
    resultado = calcular_resultado("Bob", QUESTOES, respostas)
    assert "Acertos: 0/3" in resultado


def test_calcular_resultado_parcial():
    # Acerta Q1 (B) e Q3 (D), erra Q2
    respostas = ["B", "X", "D"]
    resultado = calcular_resultado("Carol", QUESTOES, respostas)
    assert "Acertos: 2/3" in resultado
    assert "Sua resposta: B" in resultado
    assert "Sua resposta: X" in resultado
    assert "Sua resposta: D" in resultado


def test_calcular_resultado_formato_bloco():
    respostas = ["B", "C", "D"]
    resultado = calcular_resultado("Test", QUESTOES, respostas)
    assert "=== RESULTADO ===" in resultado
    assert "================" in resultado
