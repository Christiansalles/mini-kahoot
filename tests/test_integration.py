"""
Testes de integração end-to-end para o client.py — Mini Kahoot (TCP).

Simula um servidor fake completo em thread separada e valida
o fluxo inteiro do cliente.
"""

import socket
import threading
import time

from client import main


QUESTOES = [
    {
        "texto": "Q1. Em redes, qual protocolo é orientado à conexão?\n"
                 "A) UDP  B) TCP  C) ICMP  D) ARP\nSua resposta: ",
        "correta": "B",
    },
    {
        "texto": "Q2. Qual camada do modelo OSI é responsável pelo endereçamento IP?\n"
                 "A) Transporte  B) Enlace  C) Rede  D) Física\nSua resposta: ",
        "correta": "C",
    },
    {
        "texto": "Q3. Qual comando exibe as interfaces de rede no Linux?\n"
                 "A) netstat  B) ping  C) traceroute  D) ifconfig\nSua resposta: ",
        "correta": "D",
    },
]


def _criar_fake_server(port_holder, pronto):
    """Cria um servidor fake que simula o protocolo do mini-kahoot.

    Args:
        port_holder: lista onde a porta escolhida será armazenada.
        pronto: threading.Event sinalizado quando o servidor está ouvindo.
    """
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('localhost', 0))
    port_holder.append(srv.getsockname()[1])
    srv.listen(1)
    pronto.set()

    conn, _ = srv.accept()

    # Recebe nome
    nome = conn.recv(1024).decode().strip()

    # Envia questões e recebe respostas
    respostas_recebidas = []
    for q in QUESTOES:
        conn.sendall(q["texto"].encode())
        resp = conn.recv(1024).decode().strip()
        respostas_recebidas.append(resp)

    # Calcula e envia resultado
    acertos = sum(
        1 for r, q in zip(respostas_recebidas, QUESTOES)
        if r == q["correta"]
    )

    linhas_detalhe = ""
    for i, (r, q) in enumerate(zip(respostas_recebidas, QUESTOES), 1):
        linhas_detalhe += f"\nQ{i} | Sua resposta: {r} | Correta: {q['correta']}"

    resultado = (
        f"\n=== RESULTADO ==="
        f"\nJogador: {nome}"
        f"\nAcertos: {acertos}/3"
        f"{linhas_detalhe}"
        f"\n================\n"
    )
    conn.sendall(resultado.encode())
    conn.close()
    srv.close()


def test_fluxo_completo():
    """Testa o fluxo completo: nome → 3 respostas corretas → resultado 3/3."""
    port_holder = []
    pronto = threading.Event()

    t = threading.Thread(target=_criar_fake_server, args=(port_holder, pronto))
    t.start()
    pronto.wait(timeout=5)
    port = port_holder[0]

    # Simula: nome "João", depois as 3 respostas corretas (B, C, D)
    entradas = iter(["João", "B", "C", "D"])

    saida = []
    _print_original = __builtins__["print"] if isinstance(__builtins__, dict) else __builtins__.print

    def captura_print(*args, **kwargs):
        saida.append(" ".join(str(a) for a in args))
        _print_original(*args, **kwargs)

    import builtins
    builtins.print = captura_print

    try:
        main(host='localhost', port=port, input_fn=lambda prompt="": next(entradas))
    finally:
        builtins.print = _print_original

    t.join(timeout=5)

    texto_saida = "\n".join(saida)
    assert "Conectado ao servidor" in texto_saida
    assert "RESULTADO" in texto_saida
    assert "Acertos: 3/3" in texto_saida
    assert "Jogador: João" in texto_saida


def test_fluxo_com_resposta_invalida():
    """Testa o fluxo com uma resposta inválida seguida de correção."""
    port_holder = []
    pronto = threading.Event()

    t = threading.Thread(target=_criar_fake_server, args=(port_holder, pronto))
    t.start()
    pronto.wait(timeout=5)
    port = port_holder[0]

    # Simula: nome "Maria", Q1: "X" (inválida) → "B", Q2: "C", Q3: "A" (errada)
    entradas = iter(["Maria", "X", "B", "C", "A"])

    saida = []
    _print_original = __builtins__["print"] if isinstance(__builtins__, dict) else __builtins__.print

    def captura_print(*args, **kwargs):
        saida.append(" ".join(str(a) for a in args))
        _print_original(*args, **kwargs)

    import builtins
    builtins.print = captura_print

    try:
        main(host='localhost', port=port, input_fn=lambda prompt="": next(entradas))
    finally:
        builtins.print = _print_original

    t.join(timeout=5)

    texto_saida = "\n".join(saida)
    # Validação de retry apareceu
    assert "Resposta inválida" in texto_saida
    # Resultado com 2/3 (B e C corretas, A errada na Q3)
    assert "RESULTADO" in texto_saida
    assert "Jogador: Maria" in texto_saida
    assert "Acertos: 2/3" in texto_saida
