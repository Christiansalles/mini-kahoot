import socket

# --- Configuração ---
HOST = '0.0.0.0'
PORT = 5000

# --- Banco de Questões ---
QUESTOES = [
    {
        "enunciado": "Q1. Em redes, qual protocolo é orientado à conexão?",
        "alternativas": "A) UDP  B) TCP  C) ICMP  D) ARP",
        "correta": "B"
    },
    {
        "enunciado": "Q2. Qual camada do modelo OSI é responsável pelo endereçamento IP?",
        "alternativas": "A) Transporte  B) Enlace  C) Rede  D) Física",
        "correta": "C"
    },
    {
        "enunciado": "Q3. Qual comando exibe as interfaces de rede no Linux?",
        "alternativas": "A) netstat  B) ping  C) traceroute  D) ifconfig",
        "correta": "D"
    },
]


def formatar_questao(q):
    """Monta a string de uma questão para envio ao cliente."""
    return f"{q['enunciado']}\n{q['alternativas']}\nSua resposta: "


def calcular_resultado(nome, questoes, respostas):
    """Calcula acertos e retorna o bloco de resultado formatado."""
    acertos = 0
    linhas_resultado = []

    for i, (q, resp) in enumerate(zip(questoes, respostas)):
        correta = q["correta"]
        if resp == correta:
            acertos += 1
        linhas_resultado.append(f"Q{i+1} | Sua resposta: {resp} | Correta: {correta}")

    resultado = (
        f"\n=== RESULTADO ===\n"
        f"Jogador: {nome}\n"
        f"Acertos: {acertos}/{len(questoes)}\n\n"
        + "\n".join(linhas_resultado) +
        "\n================\n"
    )
    return resultado


def criar_servidor(host=HOST, port=PORT):
    """Cria e configura o socket TCP do servidor."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    print(f"[*] Servidor aguardando conexão na porta {port}...")
    return server


def aceitar_conexao(server_socket):
    """Aceita uma conexão e retorna (conn, nome_do_jogador)."""
    conn, addr = server_socket.accept()
    print(f"[+] Conexão recebida de {addr}")
    nome = conn.recv(1024).decode().strip()
    print(f"[+] Jogador conectado: {nome}")
    return conn, nome


def executar_quiz(conn, nome, questoes):
    """Envia questões, recebe respostas, calcula e envia resultado."""
    respostas_usuario = []

    for q in questoes:
        mensagem = formatar_questao(q)
        conn.sendall(mensagem.encode())

        resposta = conn.recv(1024).decode().strip().upper()
        respostas_usuario.append(resposta)
        print(f"[>] {nome} respondeu: {resposta}")

    resultado = calcular_resultado(nome, questoes, respostas_usuario)
    conn.sendall(resultado.encode())
    print(f"[*] Resultado enviado para {nome}. Encerrando conexão.")


if __name__ == "__main__":
    server = criar_servidor()
    try:
        conn, nome = aceitar_conexao(server)
        executar_quiz(conn, nome, QUESTOES)
        conn.close()
    finally:
        server.close()
