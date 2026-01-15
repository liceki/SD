import paho.mqtt.client as mqtt
import rpyc
import json
import os
import time

BROKER = os.getenv("BROKER_ADDRESS", "mosquitto")
SSACP_HOST = os.getenv("SSACP_HOST", "ssacp") # Nome do serviço no Docker
SSACP_PORT = 50051
# Usamos $share/sensors/ para balancear a carga entre as 15 instâncias
TOPIC = "$share/sensors/f1/pneus"

def send_rpc(payload):
    try:
        # Conecta no SSACP (o Docker DNS faz Round-Robin entre as 3 instâncias do SSACP)
        conn = rpyc.connect(SSACP_HOST, SSACP_PORT, config={'allow_public_attrs': True})
        conn.root.receber_dados(payload)
        conn.close()
        print(f" Enviado via RPC (Carro {payload.get('numero')})")
    except Exception as e:
        print(f"❌ Erro RPC: {e}")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f" ISCCP Conectado. Ouvindo {TOPIC}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        send_rpc(payload)
    except Exception as e:
        print(e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

while True:
    try:
        client.connect(BROKER, 1883, 60)
        client.loop_forever()
    except:
        time.sleep(2)