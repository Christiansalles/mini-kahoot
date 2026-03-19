"""Testes unitários — Fases 1, 2 e 3: lógica pura + infra TCP + loop do quiz."""

import sys
from pathlib import Path

# Garante que o diretório raiz do projeto está no sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from unittest.mock import patch, MagicMock
from server import (QUESTOES, formatar_questao, calcular_resultado,
                    criar_servidor, aceitar_conexao, executar_quiz)


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


# ---------- criar_servidor (mock) ----------

@patch("server.socket.socket")
def test_criar_servidor_configura_socket(mock_socket_cls):
    mock_sock = MagicMock()
    mock_socket_cls.return_value = mock_sock

    resultado = criar_servidor("0.0.0.0", 5000)

    # Verifica que criou socket TCP
    import socket as _socket
    mock_socket_cls.assert_called_once_with(_socket.AF_INET, _socket.SOCK_STREAM)

    # Verifica SO_REUSEADDR
    mock_sock.setsockopt.assert_called_once_with(
        _socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1
    )

    # Verifica bind e listen
    mock_sock.bind.assert_called_once_with(("0.0.0.0", 5000))
    mock_sock.listen.assert_called_once_with(1)

    assert resultado is mock_sock


# ---------- aceitar_conexao (mock) ----------

def test_aceitar_conexao_retorna_nome():
    mock_server = MagicMock()
    mock_conn = MagicMock()
    mock_server.accept.return_value = (mock_conn, ("127.0.0.1", 12345))
    mock_conn.recv.return_value = b"  Joao  \n"

    conn, nome = aceitar_conexao(mock_server)

    assert conn is mock_conn
    assert nome == "Joao"
    mock_conn.recv.assert_called_once_with(1024)


# ---------- executar_quiz (mock) ----------

def test_executar_quiz_todas_corretas():
    mock_conn = MagicMock()
    # Simula respostas corretas: B, C, D
    mock_conn.recv.side_effect = [b"B\n", b"C\n", b"D\n"]

    executar_quiz(mock_conn, "Alice", QUESTOES)

    # 3 questões + 1 resultado = 4 chamadas a sendall
    assert mock_conn.sendall.call_count == 4
    # 3 chamadas a recv (uma por questão)
    assert mock_conn.recv.call_count == 3

    # O último sendall deve conter o resultado com 3/3
    ultimo_envio = mock_conn.sendall.call_args_list[-1][0][0].decode()
    assert "Acertos: 3/3" in ultimo_envio


def test_executar_quiz_respostas_erradas():
    mock_conn = MagicMock()
    # Simula respostas todas erradas
    mock_conn.recv.side_effect = [b"A\n", b"A\n", b"A\n"]

    executar_quiz(mock_conn, "Bob", QUESTOES)

    ultimo_envio = mock_conn.sendall.call_args_list[-1][0][0].decode()
    assert "Acertos: 0/3" in ultimo_envio
