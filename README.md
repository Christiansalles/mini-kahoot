# Mini Kahoot

Este projeto é um jogo de perguntas e respostas (Kahoot) implementado em Python, com uma arquitetura cliente-servidor que permite jogar via terminal.

## Integrantes

- Christian Salles Castilho
- Rafael Areias Silveira

## Funcionalidades

- **Arquitetura Cliente-Servidor**: O jogo roda em um servidor e os jogadores se conectam através de clientes.
- **Interface de Terminal**: Jogo e administração realizados diretamente no terminal.
- **Sistema de Pontuação**: Pontuação baseada em acertos.
- **Validação de Respostas**: O servidor valida as respostas e envia o resultado para o cliente.

## Pré-requisitos

- Python 3.6 ou superior
- Sem dependências externas (apenas biblioteca padrão `socket`)

## Instalação

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd mini-kahoot
   ```

## Como Jogar

### 1. Iniciar o Servidor

Abra um terminal e execute o servidor:

```bash
python server.py
```

O servidor iniciará na porta padrão `5000` e aguardará a conexão de um cliente.

### 2. Iniciar o Cliente

Abra **outro** terminal e execute o cliente:

```bash
python client.py
```

O cliente solicitará o **nome do jogador** e conectará automaticamente ao servidor em `localhost:5000`.

### 3. Jogar

Responda às 3 questões digitando `A`, `B`, `C` ou `D`. Ao final, o servidor exibirá o seu resultado.

## Exemplo de Saída

**Terminal do Servidor:**
```
[*] Servidor aguardando conexão na porta 5000...
[+] Conexão recebida de ('127.0.0.1', 52341)
[+] Jogador conectado: Christian
[>] Christian respondeu: B
[>] Christian respondeu: A
[>] Christian respondeu: D
[*] Resultado enviado para Christian. Encerrando conexão.
```

**Terminal do Cliente:**
```
[*] Conectado ao servidor!
Digite seu nome: Christian

Q1. Em redes, qual protocolo é orientado à conexão?
A) UDP  B) TCP  C) ICMP  D) ARP
Sua resposta: B

Q2. Qual camada do modelo OSI é responsável pelo endereçamento IP?
A) Transporte  B) Enlace  C) Rede  D) Física
Sua resposta: A

Q3. Qual comando exibe as interfaces de rede no Linux?
A) netstat  B) ping  C) traceroute  D) ifconfig
Sua resposta: D

=== RESULTADO ===
Jogador: Christian
Acertos: 2/3

Q1 | Sua resposta: B | Correta: B
Q2 | Sua resposta: A | Correta: C
Q3 | Sua resposta: D | Correta: D
================
```

## Testes

O projeto inclui testes unitários e de integração para garantir a qualidade do código.

Para executar os testes:

```bash
python -m pytest tests/
```

## Estrutura do Projeto

```
mini-kahoot/
├── server.py          # Lógica do servidor e loop do quiz
├── client.py          # Lógica do cliente e interface do usuário
├── tests/             # Testes do projeto
│   ├── test_server.py
│   ├── test_integration.py
│   └── __init__.py
└── README.md          # Este arquivo
```