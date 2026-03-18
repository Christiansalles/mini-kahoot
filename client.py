import socket

HOST = 'localhost'   # IP do servidor (trocar se for testar em rede)
PORT = 5000


def main():
    # 1. Conectar ao servidor
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print("[*] Conectado ao servidor!")

    # 2. Solicitar e enviar o nome do jogador
    nome = input("Digite seu nome: ").strip()
    client.sendall(nome.encode())

    # 3. Loop de recebimento de questões e envio de respostas
    for _ in range(3):
        # Recebe a questão do servidor
        questao = client.recv(4096).decode()
        print("\n" + questao)

        # Valida a entrada do usuário (case-insensitive)
        while True:
            resposta = input().strip().upper()
            if resposta in ["A", "B", "C", "D"]:
                break
            print("❌ Resposta inválida. Digite apenas A, B, C ou D:")

        # Envia a resposta
        client.sendall(resposta.encode())

    # 4. Receber e exibir o resultado final
    resultado = client.recv(4096).decode()
    print(resultado)

    client.close()


if __name__ == "__main__":
    main()
