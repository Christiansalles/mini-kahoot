"""
client.py — Cliente TCP do Mini Kahoot.

Conecta ao servidor, exibe questões e envia respostas do jogador.
"""

import socket

HOST = 'localhost'
PORT = 5000


def criar_conexao(host=HOST, port=PORT):
    """Cria e retorna um socket TCP conectado ao servidor.

    Args:
        host: Endereço do servidor (padrão: localhost).
        port: Porta do servidor (padrão: 5000).

    Returns:
        Socket TCP conectado.

    Raises:
        ConnectionRefusedError: Se o servidor não estiver acessível.
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print("[*] Conectado ao servidor!")
    return client


def enviar_nome(sock, nome):
    """Envia o nome do jogador ao servidor.

    O nome é limpo (strip) antes de ser enviado.

    Args:
        sock: Socket TCP conectado ao servidor.
        nome: Nome do jogador (string).
    """
    nome_limpo = nome.strip()
    sock.sendall(nome_limpo.encode())
