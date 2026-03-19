"""
Testes unitários para o client.py — Mini Kahoot (TCP).

Cada fase de implementação adiciona novos testes neste arquivo.
"""

import socket
import threading

from client import (
    criar_conexao,
    enviar_nome,
    validar_resposta,
    receber_questao,
    enviar_resposta,
    processar_questoes,
)


# ======================== Fase 1 — Conexão TCP ========================


def _servidor_temporario(host, port, evento_pronto, evento_conectou):
    """Sobe um servidor TCP temporário para testes de conexão."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(1)
    evento_pronto.set()  # sinaliza que o servidor está ouvindo
    conn, _ = srv.accept()
    evento_conectou.set()  # sinaliza que um cliente conectou
    conn.close()
    srv.close()


def test_criar_conexao_sucesso():
    """Verifica que criar_conexao() retorna um socket conectado."""
    host = 'localhost'
    port = 0  # SO escolhe porta livre

    # Servidor temporário para descobrir a porta
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, 0))
    port = srv.getsockname()[1]
    srv.listen(1)

    # Aceita a conexão em thread separada
    conexoes = []

    def aceitar():
        conn, _ = srv.accept()
        conexoes.append(conn)

    t = threading.Thread(target=aceitar)
    t.start()

    # Testa a função
    client = criar_conexao(host, port)

    try:
        # Verifica que o socket está conectado (getpeername não lança erro)
        peer = client.getpeername()
        assert peer[0] in ('127.0.0.1', '::1', 'localhost')
        assert peer[1] == port
    finally:
        client.close()
        t.join(timeout=2)
        for c in conexoes:
            c.close()
        srv.close()


def test_criar_conexao_falha():
    """Verifica que criar_conexao() levanta erro quando o servidor não existe."""
    import pytest

    # Porta que certamente não tem servidor escutando
    with pytest.raises((ConnectionRefusedError, OSError)):
        criar_conexao('localhost', 59999)


# =================== Fase 2 — Envio do nome do jogador ===================


def test_enviar_nome():
    """Verifica que o nome é enviado corretamente via socket."""
    s1, s2 = socket.socketpair()
    try:
        enviar_nome(s1, "João")
        recebido = s2.recv(1024).decode()
        assert recebido == "João"
    finally:
        s1.close()
        s2.close()


def test_enviar_nome_com_espacos():
    """Verifica que espaços extras são removidos antes do envio."""
    s1, s2 = socket.socketpair()
    try:
        enviar_nome(s1, "  Maria  ")
        recebido = s2.recv(1024).decode()
        assert recebido == "Maria"
    finally:
        s1.close()
        s2.close()


# ================ Fase 3 — Validação de entrada (A/B/C/D) ================


def test_validar_resposta_validas():
    """Verifica que A, B, C, D (maiúsculas e minúsculas) são aceitas."""
    assert validar_resposta("A") is True
    assert validar_resposta("b") is True
    assert validar_resposta("c") is True
    assert validar_resposta("D") is True


def test_validar_resposta_invalidas():
    """Verifica que entradas fora de A/B/C/D são rejeitadas."""
    assert validar_resposta("E") is False
    assert validar_resposta("AB") is False
    assert validar_resposta("") is False
    assert validar_resposta("1") is False
    assert validar_resposta("sim") is False


def test_validar_resposta_com_espacos():
    """Verifica que espaços ao redor da letra são ignorados."""
    assert validar_resposta(" a ") is True
    assert validar_resposta("  B  ") is True


# ========= Fase 4 — Loop de questões e envio de respostas =========


def test_receber_questao():
    """Verifica que receber_questao() retorna a string enviada pelo servidor."""
    s1, s2 = socket.socketpair()
    try:
        questao = "Q1. Pergunta de teste?\nA) Op1  B) Op2  C) Op3  D) Op4\nSua resposta: "
        s1.sendall(questao.encode())
        resultado = receber_questao(s2)
        assert resultado == questao
    finally:
        s1.close()
        s2.close()


def test_enviar_resposta():
    """Verifica que enviar_resposta() envia a letra corretamente."""
    s1, s2 = socket.socketpair()
    try:
        enviar_resposta(s1, "b")
        recebido = s2.recv(1024).decode()
        assert recebido == "B"
    finally:
        s1.close()
        s2.close()


def test_processar_questoes_respostas_validas():
    """Simula 3 questões com 3 respostas válidas."""
    s_cliente, s_servidor = socket.socketpair()
    respostas = iter(["A", "B", "C"])

    def fake_input():
        return next(respostas)

    def servidor():
        for i in range(1, 4):
            s_servidor.sendall(
                f"Q{i}. Pergunta?\nA) X  B) Y  C) Z  D) W\nSua resposta: ".encode()
            )
            resp = s_servidor.recv(1024).decode()
            assert resp in ("A", "B", "C", "D")

    t = threading.Thread(target=servidor)
    t.start()

    try:
        processar_questoes(s_cliente, input_fn=fake_input, num_questoes=3)
    finally:
        s_cliente.close()
        t.join(timeout=5)
        s_servidor.close()


def test_processar_questoes_com_retentativa():
    """Simula uma resposta inválida seguida de uma válida."""
    s_cliente, s_servidor = socket.socketpair()
    # Primeira tentativa "X" é inválida, depois "A" é válida
    respostas = iter(["X", "A"])

    def fake_input():
        return next(respostas)

    def servidor():
        s_servidor.sendall(
            "Q1. Pergunta?\nA) X  B) Y  C) Z  D) W\nSua resposta: ".encode()
        )
        resp = s_servidor.recv(1024).decode()
        assert resp == "A"

    t = threading.Thread(target=servidor)
    t.start()

    try:
        processar_questoes(s_cliente, input_fn=fake_input, num_questoes=1)
    finally:
        s_cliente.close()
        t.join(timeout=5)
        s_servidor.close()
