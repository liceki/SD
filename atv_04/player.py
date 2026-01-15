import turtle
import time
import json
import random
import paho.mqtt.client as mqtt
import rpyc
import threading
import sys

# Identidade
MY_ID = f"Player_{random.randint(1000, 9999)}"
BROKER = "localhost"
RPC_HOST = "localhost"

# Estado
estado_atual = "MENU"  # MENU, SEARCHING, FOUND, PLAYING
dados_partida = {}
rpc_conn = None

# --- CONFIGURAÇÃO GRÁFICA ---
wn = turtle.Screen()
wn.title(f"Atividade 4 - {MY_ID}")
wn.setup(600, 400)
wn.tracer(0)  # DESLIGA ATUALIZAÇÃO AUTOMÁTICA (Essencial para performance)

# Caneta para escrever textos (UI)
caneta = turtle.Turtle()
caneta.hideturtle()
caneta.penup()


# --- MQTT ---
def on_message(client, userdata, msg):
    global estado_atual, dados_partida
    try:
        data = json.loads(msg.payload.decode())
        status = data.get('status')
        players = data.get('players', [])

        # TELA 3: Partida Encontrada
        if status == 'FOUND':
            # Só muda se eu for um dos selecionados
            if MY_ID in players:
                estado_atual = 'FOUND'
                desenhar_interface()

        # VOLTAR PARA TELA 2 (Alguém recusou)
        elif status == 'SEARCHING_AGAIN':
            if estado_atual == 'FOUND':
                estado_atual = 'SEARCHING'
                desenhar_interface()

        # TELA 4: Jogo Iniciado
        elif status == 'START':
            config = data.get('config', {})
            if MY_ID in config:
                dados_partida = config[MY_ID]
                estado_atual = 'PLAYING'
                client.loop_stop()  # Para MQTT
                iniciar_jogo_rpc()  # Vai para o loop do jogo
    except Exception as e:
        print(e)


mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
try:
    mqtt_client.connect(BROKER, 1883, 60)
    mqtt_client.subscribe("game/status")
    mqtt_client.loop_start()
except:
    print("ERRO: Broker não rodando!")


# --- FUNÇÕES DE DESENHO (UI) ---
def desenhar_interface():
    caneta.clear()

    if estado_atual == "MENU":
        wn.bgcolor("white")
        caneta.goto(0, 50);
        caneta.write("TELA 1: MENU", align="center", font=("Arial", 20, "bold"))
        caneta.goto(0, -50);
        caneta.write("[ESPAÇO] Buscar Partida", align="center")

    elif estado_atual == "SEARCHING":
        wn.bgcolor("lightgray")
        caneta.goto(0, 20);
        caneta.write("TELA 2: PROCURANDO...", align="center", font=("Arial", 16, "bold"))
        caneta.goto(0, -20);
        caneta.write("Aguardando outros jogadores...", align="center")
        caneta.goto(0, -80);
        caneta.color("red");
        caneta.write("[X] CANCELAR BUSCA", align="center");
        caneta.color("black")

    elif estado_atual == "FOUND":
        wn.bgcolor("lightblue")
        caneta.goto(0, 50);
        caneta.write("TELA 3: PARTIDA ENCONTRADA!", align="center", font=("Arial", 16, "bold"))
        caneta.goto(-100, -50);
        caneta.write("[S] ACEITAR", align="center", font=("Arial", 12, "bold"))
        caneta.goto(100, -50);
        caneta.write("[N] RECUSAR", align="center", font=("Arial", 12, "bold"))

    wn.update()


# --- COMANDOS DE ENTRADA (LOBBY) ---
def cmd_buscar():
    global estado_atual
    if estado_atual == "MENU":
        estado_atual = "SEARCHING"
        desenhar_interface()
        mqtt_client.publish("game/join", MY_ID)


def cmd_cancelar_busca():
    global estado_atual
    if estado_atual == "SEARCHING":
        estado_atual = "MENU"
        desenhar_interface()
        mqtt_client.publish("game/leave", MY_ID)


def cmd_aceitar():
    if estado_atual == "FOUND":
        caneta.goto(0, -120);
        caneta.write("Aceito! Aguardando...", align="center")
        wn.update()
        mqtt_client.publish("game/response", json.dumps({"id": MY_ID, "resp": "ACCEPT"}))


def cmd_recusar():
    global estado_atual
    if estado_atual == "FOUND":
        estado_atual = "MENU"
        desenhar_interface()
        mqtt_client.publish("game/response", json.dumps({"id": MY_ID, "resp": "DECLINE"}))


# --- FASE DE JOGO (MOVIMENTAÇÃO FLUIDA) ---
teclas_pressionadas = {
    "w": False, "s": False, "a": False, "d": False
}


def press_w(): teclas_pressionadas["w"] = True


def release_w(): teclas_pressionadas["w"] = False


def press_s(): teclas_pressionadas["s"] = True


def release_s(): teclas_pressionadas["s"] = False


def press_a(): teclas_pressionadas["a"] = True


def release_a(): teclas_pressionadas["a"] = False


def press_d(): teclas_pressionadas["d"] = True


def release_d(): teclas_pressionadas["d"] = False


def iniciar_jogo_rpc():
    # 1. Limpa TUDO da tela anterior
    caneta.clear()
    wn.clearscreen()
    wn.bgcolor("white")
    wn.tracer(0)  # Garante que animação continua desligada

    # 2. Conecta RPC
    try:
        conn = rpyc.connect(RPC_HOST, 18861, config={'allow_public_attrs': True})
        conn.root.registrar(MY_ID, dados_partida['x'], 0, dados_partida['cor'])
    except:
        print("Erro RPC")
        return

    # 3. Cria Meu Boneco
    eu = turtle.Turtle()
    eu.shape("circle");
    eu.color(dados_partida['cor']);
    eu.penup()
    eu.goto(dados_partida['x'], 0)

    # 4. Configura Controles Fluidos
    wn.listen()
    wn.onkeypress(press_w, "w");
    wn.onkeyrelease(release_w, "w")
    wn.onkeypress(press_s, "s");
    wn.onkeyrelease(release_s, "s")
    wn.onkeypress(press_a, "a");
    wn.onkeyrelease(release_a, "a")
    wn.onkeypress(press_d, "d");
    wn.onkeyrelease(release_d, "d")

    inimigos = {}

    # 5. LOOP DO JOGO (FPS)
    while True:
        # Movimentação Fluida
        velocidade = 8
        moveu = False
        if teclas_pressionadas["w"]: eu.sety(eu.ycor() + velocidade); moveu = True
        if teclas_pressionadas["s"]: eu.sety(eu.ycor() - velocidade); moveu = True
        if teclas_pressionadas["a"]: eu.setx(eu.xcor() - velocidade); moveu = True
        if teclas_pressionadas["d"]: eu.setx(eu.xcor() + velocidade); moveu = True

        # Envia posição via RPC
        if moveu:
            conn.root.mover(MY_ID, eu.xcor(), eu.ycor())

        # Recebe inimigos
        try:
            estado = conn.root.get_estado()
            for pid, info in estado.items():
                if pid == MY_ID: continue

                if pid not in inimigos:
                    t = turtle.Turtle();
                    t.shape("circle");
                    t.color(info['cor']);
                    t.penup()
                    inimigos[pid] = t

                inimigos[pid].goto(info['x'], info['y'])
        except:
            pass

        wn.update()
        time.sleep(0.03)  # ~30 FPS


# --- SETUP INICIAL ---
wn.listen()
wn.onkeypress(cmd_buscar, "space")
wn.onkeypress(cmd_cancelar_busca, "x")  # Tecla X adicionada para cancelar
wn.onkeypress(cmd_aceitar, "s")
wn.onkeypress(cmd_recusar, "n")

desenhar_interface()
wn.mainloop()