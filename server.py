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
