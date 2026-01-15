import time
import json
import random
import os
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES ---
# Pega o endereço do broker do Docker ou usa localhost
BROKER = os.getenv("BROKER_ADDRESS", "mosquitto")
TOPIC = "f1/pneus"

# --- IDENTIDADE (Sem Banco de Dados para ser rápido) ---
PILOTOS = ["RedBull-Verstappen", "Ferrari-Leclerc", "Mercedes-Hamilton", "McLaren-Norris"]
CAR_ID = random.choice(PILOTOS) + f"-{random.randint(10, 99)}"

# --- FÍSICA ---
TRACK = ["S do Senna", "Reta Oposta", "Descida do Lago", "Ferradura", "Laranjinha", "Pinheirinho", "Bico de Pato",
         "Mergulho", "Junção", "Subida Boxes", "Reta Principal"]
idx = 0
volta = 1


# --- MQTT SETUP (Versão 2) ---
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[{CAR_ID}] 🟢 CONECTADO AO BROKER! ENVIANDO DADOS...")
    else:
        print(f"[{CAR_ID}] 🔴 FALHA CONEXÃO: {reason_code}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect

print(f"[{CAR_ID}] TENTANDO CONECTAR EM {BROKER}...")

# Loop de conexão insistente
while True:
    try:
        client.connect(BROKER, 1883, 60)
        client.loop_start()
        break
    except Exception as e:
        print(f"[{CAR_ID}] Broker indisponível, tentando em 2s... ({e})")
        time.sleep(2)

# --- LOOP DA CORRIDA ---
while True:
    # 1. Simula dados
    payload = {
        "carro_id": CAR_ID,
        "sensor_responsavel": TRACK[idx],
        "volta": volta,
        "velocidade": random.randint(200, 320),
        "timestamp": time.time(),
        "pneus": {
            "fl": {"desgaste": random.randint(0, 90), "temperatura": random.randint(80, 130)},
            "fr": {"desgaste": random.randint(0, 90), "temperatura": random.randint(80, 130)},
            "rl": {"desgaste": random.randint(0, 90), "temperatura": random.randint(80, 130)},
            "rr": {"desgaste": random.randint(0, 90), "temperatura": random.randint(80, 130)}
        }
    }

    # 2. Publica e Printa (pra você ver no log)
    client.publish(TOPIC, json.dumps(payload))
    print(f"[{CAR_ID}] Enviou: {TRACK[idx]} (V.{volta})")

    # 3. Avança Pista
    idx += 1
    if idx >= len(TRACK):
        idx = 0
        volta += 1

    time.sleep(1.0)  # 1 segundo por setor