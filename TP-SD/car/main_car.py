import time
import json
import random
import os
import socket
import paho.mqtt.client as mqtt

BROKER = os.getenv("BROKER_ADDRESS", "mosquitto")
TOPIC = "f1/pneus"

GRID = [
    {"num": 1, "nome": "Verstappen", "equipe": "Mercedes"},
    {"num": 12, "nome": "Senna", "equipe": "Mercedes"},
    {"num": 16, "nome": "Leclerc", "equipe": "Ferrari"},
    {"num": 44, "nome": "Hamilton", "equipe": "Ferrari"},
    {"num": 11, "nome": "Perez", "equipe": "RedBull"},
    {"num": 30, "nome": "Lawson", "equipe": "RedBull"},
    {"num": 4, "nome": "Norris", "equipe": "McLaren"},
    {"num": 81, "nome": "Piastri", "equipe": "McLaren"},
    {"num": 14, "nome": "Alonso", "equipe": "Aston Martin"},
    {"num": 18, "nome": "Stroll", "equipe": "Aston Martin"},
    {"num": 10, "nome": "Gasly", "equipe": "Alpine"},
    {"num": 31, "nome": "Doohan", "equipe": "Alpine"},
    {"num": 23, "nome": "Albon", "equipe": "Williams"},
    {"num": 55, "nome": "Sainz", "equipe": "Williams"},
    {"num": 27, "nome": "Hulkenberg", "equipe": "Audi"},
    {"num": 99, "nome": "Bortoleto", "equipe": "Audi"},
    {"num": 31, "nome": "Ocon", "equipe": "Haas"},
    {"num": 87, "nome": "Bearman", "equipe": "Haas"},
    {"num": 22, "nome": "Tsunoda", "equipe": "RB"},
    {"num": 6, "nome": "Hadjar", "equipe": "RB"},
    {"num": 5, "nome": "Vettel", "equipe": "Porsche"},
    {"num": 9, "nome": "Webber", "equipe": "Porsche"},
    {"num": 7, "nome": "Hakkinen", "equipe": "Lotus"},
    {"num": 8, "nome": "Massa", "equipe": "Lotus"},
]

# --- 15 SENSORES EXATOS ---
# Removido "S do Senna Saida"
TRACK = [
    "Reta Principal", "Linha de Chegada", "S do Senna (Entrada)", "Curva do Sol",
    "Reta Oposta", "Descida do Lago", "Ferradura", "Laranjinha",
    "Pinheirinho", "Bico de Pato", "Mergulho", "Junção",
    "Subida dos Boxes", "Arquibancada A", "Arquibancada B"
]


def get_identity():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        last_octet = int(ip.split('.')[-1])
        idx = (last_octet) % len(GRID)
        return GRID[idx]
    except:
        return random.choice(GRID)


MEU_DADO = get_identity()
CAR_ID = f"{MEU_DADO['equipe']}-{MEU_DADO['nome']}"
CAR_NUM = MEU_DADO['num']

print(f"🏎️ PILOTO: {CAR_ID} (#{CAR_NUM})")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"Car_{socket.gethostname()}")

while True:
    try:
        client.connect(BROKER, 1883, 60)
        break
    except:
        time.sleep(2)

client.loop_start()

idx_pista = 0
volta = 1
# Estado inicial aleatório para não começarem todos iguais
estado_pneus = {
    "fl": random.uniform(0, 10),
    "fr": random.uniform(0, 10),
    "rl": random.uniform(0, 10),
    "rr": random.uniform(0, 10)
}
# Agressividade varia muito de piloto para piloto (0.8 a 1.8)
agressividade = random.uniform(0.8, 1.8)

time.sleep(MEU_DADO['num'] * 0.2)

while True:
    sensor = TRACK[idx_pista]

    # --- FÍSICA CAÓTICA ---
    # Desgaste base muito mais alto e variável
    desgaste_base = random.uniform(0.4, 1.2) * agressividade

    # Assimetria: Pneus da direita gastam mais em Interlagos
    wear_mult = {"fl": 1.0, "fr": 1.5, "rl": 1.1, "rr": 1.4}

    if "Curva" in sensor or "S do Senna" in sensor:
        desgaste_base *= 2.0  # Curvas comem pneu

    for p in estado_pneus:
        # Aplica desgaste normal
        estado_pneus[p] += desgaste_base * wear_mult[p]

        # EVENTO ALEATÓRIO: Travada de roda ou zebra agressiva
        # 5% de chance a cada sensor de um pneu específico sofrer muito dano
        if random.random() > 0.95:
            estado_pneus[p] += random.uniform(3.0, 8.0)

        # Troca de pneus
        if estado_pneus[p] >= 100:
            print(f"🔧 PIT STOP: {CAR_ID}")
            # Reseta todos, simulando troca completa
            estado_pneus = {k: 0.0 for k in estado_pneus}
            time.sleep(4)

            # Temperatura instável
    temp_target = 100
    if "Reta" in sensor: temp_target = 80
    if "S do Senna" in sensor: temp_target = 125

    pneus_payload = {}
    for p, val in estado_pneus.items():
        # Variação grande (+/- 15 graus) para ficar visualmente distinto
        t = random.uniform(temp_target - 15, temp_target + 15)
        pneus_payload[p] = {"desgaste": val, "temperatura": t}

    vel = random.randint(210, 330)
    if "S do Senna" in sensor or "Junção" in sensor: vel = random.randint(80, 140)

    payload = {
        "carro_id": CAR_ID,
        "numero": CAR_NUM,
        "sensor_responsavel": sensor,
        "volta": volta,
        "velocidade": vel,
        "timestamp": time.time(),
        "pneus": pneus_payload
    }

    client.publish(TOPIC, json.dumps(payload))

    idx_pista += 1
    if idx_pista >= len(TRACK):
        idx_pista = 0
        volta += 1

    time.sleep(random.uniform(2.5, 3.5))