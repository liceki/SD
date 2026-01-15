import paho.mqtt.client as mqtt
import json
import time
import os

BROKER = os.getenv("BROKER", "localhost")
TOPIC_JOIN = "game/join"
TOPIC_LEAVE = "game/leave"  # Novo tópico para cancelar busca
TOPIC_RESP = "game/response"
TOPIC_STATUS = "game/status"

# Listas de Estado
fila = []  # Jogadores procurando (Tela 2)
em_aprovacao = []  # Os 3 selecionados (Tela 3)
aceites = []  # Quem já deu 'S' (Tela 3)


def on_connect(client, userdata, flags, rc):
    print("Matchmaker Online!")
    client.subscribe([(TOPIC_JOIN, 0), (TOPIC_LEAVE, 0), (TOPIC_RESP, 0)])


def on_message(client, userdata, msg):
    global fila, em_aprovacao, aceites
    payload = msg.payload.decode()
    topico = msg.topic

    # --- JOGADOR QUER ENTRAR NA FILA ---
    if topico == TOPIC_JOIN:
        pid = payload
        if pid not in fila and pid not in em_aprovacao:
            fila.append(pid)
            print(f"[FILA] {pid} entrou. Total: {len(fila)}")

            # Verifica se formou trio
            verificar_match(client)

    # --- JOGADOR CANCELOU BUSCA (TELA 2 -> 1) ---
    elif topico == TOPIC_LEAVE:
        pid = payload
        if pid in fila:
            fila.remove(pid)
            print(f"[SAIU] {pid} saiu da fila.")

    # --- RESPOSTA DO ACEITE (TELA 3) ---
    elif topico == TOPIC_RESP:
        dados = json.loads(payload)
        pid = dados['id']
        resp = dados['resp']

        if resp == 'DECLINE':
            print(f"[RECUSA] {pid} recusou a partida.")
            tratar_recusa(client, pid)

        elif resp == 'ACCEPT':
            if pid in em_aprovacao and pid not in aceites:
                aceites.append(pid)
                print(f"[ACEITE] {pid} confirmou. ({len(aceites)}/3)")

                if len(aceites) == 3:
                    iniciar_partida(client)


def verificar_match(client):
    global fila, em_aprovacao, aceites
    # Se tem 3 ou mais na fila, puxa os 3 primeiros para aprovação
    if len(fila) >= 3:
        em_aprovacao = fila[:3]  # Pega os 3 primeiros
        fila = fila[3:]  # Remove eles da fila