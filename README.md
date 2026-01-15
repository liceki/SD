# Portifolio de Sistemas Distribuidos

Este repositorio contem o conjunto de atividades praticas e o trabalho final desenvolvidos para a disciplina de Sistemas Distribuidos. O projeto explora conceitos fundamentais como RPC, Mensageria (MQTT), Sockets, Tolerancia a Falhas e Arquiteturas de Microsservicos.

## Estrutura do Repositorio

O projeto esta organizado em modulos independentes:

* **TP-SD/**: Sistema de Monitoramento F1 (Arquitetura Distribuida Complexa).
* **atv_02/**: API RESTful com Flask e MongoDB (CRUD).
* **atv_03/**: Jogo Multiplayer via RPC (Remote Procedure Call).
* **atv_04/**: Sistema de Matchmaking (Lobby) usando MQTT e RPC.
* **atv_05/**: Estudo de Sockets, Falhas e Seguranca.

## Tecnologias Utilizadas

* **Linguagem:** Python 3.9+
* **Containerizacao:** Docker & Docker Compose
* **Comunicacao:** gRPC, MQTT (Mosquitto), HTTP (REST), Sockets TCP, RPyC
* **Banco de Dados:** MongoDB (NoSQL)
* **Frontend:** HTML5, Bootstrap 5, SVG (Mapas Vetoriais)

## Como Executar os Projetos

Pre-requisitos: Ter **Docker** e **Docker Compose** instalados.

### 1. Trabalho Pratico: Monitoramento F1
O sistema simula 24 carros de F1 enviando telemetria em tempo real, processada por microsservicos e exibida em um dashboard.

    cd TP-SD
    # Inicia toda a infraestrutura (40+ containers simulados)
    docker-compose -f docker-compose.prod.yml up --build -d

    # Acessar Dashboard: http://localhost:5000

### 2. Atividade 02: CRUD Pessoas (NoSQL)
Gerenciamento de usuarios com interface web e persistencia em MongoDB.

    cd atv_02
    docker-compose up --build
    # Acessar: http://localhost:5000/painel

### 3. Atividade 03: Jogo RPC
Demonstracao de chamadas remotas. O servidor roda no Docker e os clientes (com interface grafica) rodam no host.

    # Terminal 1 (Servidor):
    cd atv_03
    docker-compose up --build

    # Terminal 2 e 3 (Jogadores Locais - fora do Docker):
    python3 game.py

### 4. Atividade 04: Matchmaking (MQTT + RPC)
Simula um lobby de jogo. Usa MQTT para fila e RPC para a partida.

    # Terminal 1 (Infraestrutura):
    cd atv_04
    docker-compose up --build

    # Terminal 2, 3 e 4 (Jogadores - Necessario 3 para iniciar):
    # Dica: rode o comando abaixo para abrir 3 simultaneos
    python3 player.py & python3 player.py & python3 player.py

### 5. Atividade 05: Sockets & Seguranca
Estudo de primitivas de comunicacao, timeouts e autenticacao via hash.

    cd atv_05
    docker-compose up --build

## Dicas de Execucao (Linux/Fish)

Para limpar o ambiente entre as execucoes e liberar memoria RAM (importante para evitar conflitos de portas), recomenda-se utilizar o seguinte comando para parar todos os containers antes de trocar de atividade:

    docker stop (docker ps -aq); and docker rm (docker ps -aq)

## Autor

Desenvolvido por Henrique Leão Paim
Disciplina de Sistemas Distribuidos.