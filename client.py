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


def validar_resposta(resposta):
    """Valida se a resposta é uma das alternativas aceitas (A, B, C ou D).

    A entrada é case-insensitive e espaços são ignorados.

    Args:
        resposta: String digitada pelo jogador.

    Returns:
        True se a resposta (após strip/upper) for A, B, C ou D.
    """
    return resposta.strip().upper() in ("A", "B", "C", "D")


def receber_questao(sock):
    """Recebe o texto de uma questão do servidor.

    Args:
        sock: Socket TCP conectado ao servidor.

    Returns:
        String com o texto da questão recebida.
    """
    dados = sock.recv(4096).decode()
    return dados


def enviar_resposta(sock, resposta):
    """Envia a letra da resposta ao servidor.

    Args:
        sock: Socket TCP conectado ao servidor.
        resposta: Letra da resposta (A, B, C ou D).
    """
    sock.sendall(resposta.strip().upper().encode())


def processar_questoes(sock, input_fn=None, num_questoes=3):
    """Executa o loop de recebimento de questões e envio de respostas.

    Para cada questão:
      1. Recebe e exibe a questão.
      2. Lê a resposta do jogador (com validação).
      3. Envia a resposta ao servidor.

    Args:
        sock: Socket TCP conectado ao servidor.
        input_fn: Função para leitura de entrada (padrão: input builtin).
                  Permite injetar mock nos testes.
        num_questoes: Número de questões a processar (padrão: 3).
    """
    if input_fn is None:
        input_fn = input

    for _ in range(num_questoes):
        questao = receber_questao(sock)
        print("\n" + questao)

        while True:
            resposta = input_fn().strip().upper()
            if validar_resposta(resposta):
                break
            print("❌ Resposta inválida. Digite apenas A, B, C ou D:")

        enviar_resposta(sock, resposta)


def receber_resultado(sock):
    """Recebe o bloco de resultado final do servidor.

    Args:
        sock: Socket TCP conectado ao servidor.

    Returns:
        String com o bloco de resultado.
    """
    resultado = sock.recv(4096).decode()
    return resultado


def main(host=HOST, port=PORT, input_fn=None):
    """Fluxo principal do cliente Mini Kahoot.

    1. Conecta ao servidor.
    2. Solicita e envia o nome do jogador.
    3. Processa 3 questões (recebe, valida resposta, envia).
    4. Recebe e exibe o resultado final.
    5. Fecha a conexão.

    Args:
        host: Endereço do servidor.
        port: Porta do servidor.
        input_fn: Função de entrada (padrão: input builtin).
    """
    if input_fn is None:
        input_fn = input

    sock = criar_conexao(host, port)

    try:
        nome = input_fn("Digite seu nome: ").strip()
        enviar_nome(sock, nome)

        processar_questoes(sock, input_fn=lambda: input_fn(), num_questoes=3)

        resultado = receber_resultado(sock)
        print(resultado)
    finally:
        sock.close()


if __name__ == "__main__":
    main()
