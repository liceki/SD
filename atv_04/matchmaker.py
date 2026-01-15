import paho.mqtt.client as mqtt
import json
import os
import sys

# --- CONFIGURAÇÕES ---
BROKER = os.getenv("BROKER", "localhost")
PORT = 1883

# Tópicos
TOPIC_JOIN = "game/join"
TOPIC_LEAVE = "game/leave"
TOPIC_RESP = "game/response"
TOPIC_STATUS = "game/status"

# Estado Global do Lobby
fila = []  # Jogadores aguardando (Tela 2)
em_aprovacao = []  # Os 3 selecionados para confirmar (Tela 3)
aceites = []  # Quem já apertou 'S' (Tela 3)


# --- CALLBACKS MQTT ---

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Matchmaker Conectado ao Broker! (Reason: {reason_code})")
    # Inscreve nos tópicos de entrada
    client.subscribe(TOPIC_JOIN)
    client.subscribe(TOPIC_LEAVE)
    client.subscribe(TOPIC_RESP)


def on_message(client, userdata, msg):
    global fila, em_aprovacao, aceites

    try:
        payload = msg.payload.decode()
        topico = msg.topic

        # --- 1. ENTRAR NA FILA ---
        if topico == TOPIC_JOIN:
            pid = payload
            # Só adiciona se não estiver em lugar nenhum
            if pid not in fila and pid not in em_aprovacao:
                fila.append(pid)
                print(f"[FILA] {pid} entrou. Total na fila: {len(fila)}")
                verificar_match(client)

        # --- 2. SAIR DA FILA (CANCELAR) ---
        elif topico == TOPIC_LEAVE:
            pid = payload
            if pid in fila:
                fila.remove(pid)
                print(f"[SAIU] {pid} cancelou a busca.")

        # --- 3. RESPOSTA (ACEITAR/RECUSAR) ---
        elif topico == TOPIC_RESP:
            dados = json.loads(payload)
            pid = dados.get('id')
            resp = dados.get('resp')

            if resp == 'DECLINE':
                print(f"[RECUSA] {pid} recusou a partida.")
                tratar_recusa(client, pid)

            elif resp == 'ACCEPT':
                if pid in em_aprovacao and pid not in aceites:
                    aceites.append(pid)
                    print(f"[ACEITE] {pid} confirmou. ({len(aceites)}/3)")

                    if len(aceites) == 3:
                        iniciar_partida(client)

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")


# --- LÓGICA DO JOGO ---

def verificar_match(client):
    global fila, em_aprovacao, aceites

    # Se tiver 3 ou mais pessoas na fila, inicia o processo de match
    if len(fila) >= 3:
        # Pega os 3 primeiros da fila
        em_aprovacao = fila[:3]
        # Remove eles da fila de espera
        fila = fila[3:]
        # Reseta lista de aceites
        aceites = []

        print(f"[MATCH FOUND] Players: {em_aprovacao}")

        # Avisa os jogadores para irem para a Tela 3 (FOUND)
        msg = json.dumps({"status": "FOUND", "players": em_aprovacao})
        client.publish(TOPIC_STATUS, msg)


def tratar_recusa(client, pid_recusou):
    global fila, em_aprovacao, aceites

    # Remove quem recusou da lista de aprovação
    if pid_recusou in em_aprovacao:
        em_aprovacao.remove(pid_recusou)

    # Os que sobraram (inocentes) voltam para o INÍCIO da fila (prioridade máxima)
    if em_aprovacao:
        print(f"[RESET] Devolvendo {em_aprovacao} para o início da fila.")
        fila = em_aprovacao + fila

    # Limpa as listas temporárias
    em_aprovacao = []
    aceites = []

    # Manda mensagem avisando para voltar a buscar (SEARCHING_AGAIN)
    # Isso faz a tela dos inocentes voltar de "Partida Encontrada" para "Procurando..."
    client.publish(TOPIC_STATUS, json.dumps({"status": "SEARCHING_AGAIN"}))

    # Tenta formar nova partida imediatamente com quem está na fila
    verificar_match(client)


def iniciar_partida(client):
    global em_aprovacao, aceites

    print("--- TODOS ACEITARAM! INICIANDO JOGO ---")

    # Define quem é quem e onde nasce (conforme imagem da atividade)
    configs = {
        em_aprovacao[0]: {'cor': 'red', 'x': -150},  # Esquerda
        em_aprovacao[1]: {'cor': 'green', 'x': 0},  # Meio
        em_aprovacao[2]: {'cor': 'yellow', 'x': 150}  # Direita
    }

    # Envia comando de START com as configurações
    msg = json.dumps({"status": "START", "config": configs})
    client.publish(TOPIC_STATUS, msg)

    # Limpa tudo para a próxima rodada
    em_aprovacao = []
    aceites = []


# --- EXECUÇÃO PRINCIPAL ---

if __name__ == "__main__":
    # Configura cliente MQTT compatível com Paho versão 2.0+
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Matchmaker_Server")

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Tentando conectar ao broker: {BROKER}...")

    try:
        client.connect(BROKER, PORT, 60)
        # O PULO DO GATO: loop_forever trava o script aqui e impede o 'exit code 0'
        client.loop_forever()
    except Exception as e:
        print(f"Erro fatal na conexão: {e}")
        sys.exit(1)