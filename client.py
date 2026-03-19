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
