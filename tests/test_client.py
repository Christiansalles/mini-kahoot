"""
Testes unitários para o client.py — Mini Kahoot (TCP).

Cada fase de implementação adiciona novos testes neste arquivo.
"""

import socket
import threading

from client import criar_conexao, enviar_nome


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
