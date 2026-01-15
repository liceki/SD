import time
import json
import random
import os
import socket
import zlib
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES ---
BROKER = os.getenv("BROKER_ADDRESS", "mosquitto")
TOPIC = "f1/pneus"

GRID = [
    {"num": 1, "nome": "Verstappen", "equipe": "RedBull"},
    {"num": 11, "nome": "Perez", "equipe": "RedBull"},
    {"num": 16, "nome": "Leclerc", "equipe": "Ferrari"},
    {"num": 55, "nome": "Sainz", "equipe": "Ferrari"},
    {"num": 44, "nome": "Hamilton", "equipe": "Mercedes"},
    {"num": 63, "nome": "Russell", "equipe": "Mercedes"},
    {"num": 4, "nome": "Norris", "equipe": "McLaren"},
    {"num": 81, "nome": "Piastri", "equipe": "McLaren"},
    {"num": 14, "nome": "Alonso", "equipe": "Aston Martin"},
    {"num": 18, "nome": "Stroll", "equipe": "Aston Martin"},
    {"num": 10, "nome": "Gasly", "equipe": "Alpine"},
    {"num": 31, "nome": "Ocon", "equipe": "Alpine"},
    {"num": 23, "nome": "Albon", "equipe": "Williams"},
    {"num": 2, "nome": "Sargeant", "equipe": "Williams"},
    {"num": 3, "nome": "Ricciardo", "equipe": "RB"},
    {"num": 22, "nome": "Tsunoda", "equipe": "RB"},
    {"num": 77, "nome": "Bottas", "equipe": "Sauber"},
    {"num": 24, "nome": "Zhou", "equipe": "Sauber"},
    {"num": 20, "nome": "Magnussen", "equipe": "Haas"},
    {"num": 27, "nome": "Hulkenberg", "equipe": "Haas"},
    {"num": 98, "nome": "Drugovich", "equipe": "Reserva"},
    {"num": 99, "nome": "Fittipaldi", "equipe": "Reserva"},
    {"num": 0, "nome": "Safety Car A", "equipe": "FIA"},
    {"num": 97, "nome": "Safety Car B", "equipe": "FIA"},
]

TRACK = ["S do Senna", "Reta Oposta", "Descida do Lago", "Ferradura", "Laranjinha", "Pinheirinho", "Bico de Pato",
         "Mergulho", "Junção", "Subida Boxes", "Reta Principal"]


# --- IDENTIDADE DO CONTAINER ---
def get_my_identity():
    # O Docker gera hostnames tipo "f1-project_car_5" ou hash aleatório "a1b2c3d4"
    hostname = socket.gethostname()
    # Usamos CRC32 para transformar a string num número e pegamos o resto da divisão por 24
    # Isso distribui os containers pelo grid. Pode haver repetição (colisão), mas é raro.
    idx = zlib.crc32(hostname.encode()) % len(GRID)
    return GRID[idx]


MEU_CARRO = get_my_identity()
CAR_ID = f"{MEU_CARRO['equipe']}-{MEU_CARRO['nome']}"
CAR_NUM = MEU_CARRO['num']

print(f" SOU O CARRO: {CAR_ID} (#{CAR_NUM}) - Hostname: {socket.gethostname()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"Car_{CAR_NUM}_{socket.gethostname()}")

while True:
    try:
        client.connect(BROKER, 1883, 60)
        break
    except:
        time.sleep(2)

client.loop_start()

idx_pista = random.randint(0, len(TRACK) - 1)  # Começa em lugar aleatório
volta = 1

while True:
    sensor = TRACK[idx_pista]
    vel = random.randint(120, 330)
    if any(c in sensor for c in ["S do Senna", "Laranjinha", "Junção"]): vel = random.randint(80, 160)

    payload = {
        "carro_id": CAR_ID,
        "numero": CAR_NUM,
        "sensor_responsavel": sensor,
        "volta": volta,
        "velocidade": vel,
        "timestamp": time.time(),
        "pneus": {
            "fl": {"desgaste": random.uniform(0, 100), "temperatura": random.uniform(80, 120)},
            "fr": {"desgaste": random.uniform(0, 100), "temperatura": random.uniform(80, 120)},
            "rl": {"desgaste": random.uniform(0, 100), "temperatura": random.uniform(80, 120)},
            "rr": {"desgaste": random.uniform(0, 100), "temperatura": random.uniform(80, 120)}
        }
    }

    client.publish(TOPIC, json.dumps(payload))

    idx_pista = (idx_pista + 1) % len(TRACK)
    if idx_pista == 0: volta += 1

    time.sleep(random.uniform(1.0, 3.0))  # Delay pra não floodar