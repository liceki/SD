import time
import json
import random
import os
import socket
import paho.mqtt.client as mqtt

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

# Ordem Lógica da Pista
TRACK = [
    "Reta Principal", "S do Senna", "Saída S", "Reta Oposta",
    "Descida do Lago", "Ferradura", "Laranjinha", "Pinheirinho",
    "Bico de Pato", "Mergulho", "Junção", "Subida Boxes"
]


def get_identity():
    try:
        # Pega o IP do container (ex: 172.18.0.5)
        ip = socket.gethostbyname(socket.gethostname())
        # Pega o último número (5)
        last_octet = int(ip.split('.')[-1])
        # Garante unicidade usando o IP como índice
        # Subtraímos um offset (geralmente .2 é o primeiro container) para alinhar com o array
        idx = (last_octet) % len(GRID)
        return GRID[idx]
    except:
        return random.choice(GRID)


MEU_DADO = get_identity()
CAR_ID = f"{MEU_DADO['equipe']}-{MEU_DADO['nome']}"
CAR_NUM = MEU_DADO['num']

print(f"CARRO INICIADO: {CAR_ID} (#{CAR_NUM}) | IP: {socket.gethostbyname(socket.gethostname())}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"Car_{socket.gethostname()}")

while True:
    try:
        client.connect(BROKER, 1883, 60)
        break
    except:
        time.sleep(2)

client.loop_start()

# --- FÍSICA CORRIGIDA ---
# Todos começam no GRID (Index 0 = Reta Principal)
idx_pista = 0
volta = 0

# Pequeno delay inicial baseado no número do carro para eles não largarem EXATAMENTE juntos
# Isso cria um efeito de fila indiana na largada
time.sleep(MEU_DADO['num'] * 0.1)

while True:
    sensor = TRACK[idx_pista]

    # Velocidade variável
    vel = random.randint(200, 330)
    # Curvas lentas
    if sensor in ["S do Senna", "Laranjinha", "Bico de Pato", "Junção"]:
        vel = random.randint(80, 140)

    payload = {
        "carro_id": CAR_ID,
        "numero": CAR_NUM,
        "sensor_responsavel": sensor,
        "volta": volta,
        "velocidade": vel,
        "timestamp": time.time(),
        "pneus": {
            "fl": {"desgaste": random.uniform(0, 10), "temperatura": random.uniform(90, 100)},
            "fr": {"desgaste": random.uniform(0, 10), "temperatura": random.uniform(90, 100)},
            "rl": {"desgaste": random.uniform(0, 10), "temperatura": random.uniform(90, 100)},
            "rr": {"desgaste": random.uniform(0, 10), "temperatura": random.uniform(90, 100)}
        }
    }

    client.publish(TOPIC, json.dumps(payload))

    # LÓGICA DE MOVIMENTO LINEAR
    idx_pista += 1
    if idx_pista >= len(TRACK):
        idx_pista = 0
        volta += 1

    # O tempo de espera simula o tempo gasto no setor.
    # Se for muito rápido (< 1s), o dashboard pode pular sensores visualmente (sampling).
    # Vamos manter entre 1.5s e 2.5s para dar tempo de ver no mapa.
    delay = random.uniform(1.5, 2.5)
    time.sleep(delay)