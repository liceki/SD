import paho.mqtt.client as mqtt
import rpyc
import json
import os
import time
import sys

# Configurações
BROKER = os.getenv("BROKER_ADDRESS", "mosquitto")
SSACP_HOST = os.getenv("SSACP_HOST", "ssacp")
SSACP_PORT = 50051
TOPIC = "f1/pneus"

rpc_conn = None


def get_rpc_connection():
    global rpc_conn
    try:
        if rpc_conn is None or rpc_conn.closed:
            print(f"🔌 ISCCP: Conectando ao SSACP ({SSACP_HOST}:{SSACP_PORT})...")
            rpc_conn = rpyc.connect(SSACP_HOST, SSACP_PORT, config={'allow_public_attrs': True})
            print("✅ ISCCP: Link RPC estabelecido!")
        return rpc_conn
    except Exception as e:
        print(f"❌ ISCCP: Falha ao conectar no SSACP: {e}")
        return None


# MQTT Callbacks
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"📡 ISCCP: Conectado ao Broker! Ouvindo {TOPIC}...")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        # 1. Decodifica msg do Carro
        payload = json.loads(msg.payload.decode())

        # 2. Garante timestamp
        if 'timestamp' not in payload:
            payload['timestamp'] = time.time()

        # 3. ENVIA VIA RPC (Objeto) PARA O SSACP
        conn = get_rpc_connection()
        if conn:
            # Chamada Remota de Método
            conn.root.receber_dados(payload)
            print(".", end="", flush=True)  # Feedback visual

    except Exception as e:
        print(f"⚠️ Erro no processamento: {e}")


# Setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ISCCP_Collector")
client.on_connect = on_connect
client.on_message = on_message

print("⏳ ISCCP: Iniciando...")
# Conexão inicial RPC
get_rpc_connection()

while True:
    try:
        client.connect(BROKER, 1883, 60)
        break
    except:
        time.sleep(2)

client.loop_forever()