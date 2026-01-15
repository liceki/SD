import turtle
import time
import rpyc
import sys

# --- CONFIGURAÇÃO RPC ---
SERVER_IP = "localhost"  # Se rodar o servidor no Docker, isso funciona
SERVER_PORT = 18861

try:
    print("Conectando ao servidor...")
    conn = rpyc.connect(SERVER_IP, SERVER_PORT, config={'allow_public_attrs': True})

    # Faz login e pega nossos dados iniciais
    MY_ID, MY_COLOR, start_x, start_y = conn.root.entrar()
    print(f"Conectado! Sou o Jogador {MY_ID} cor {MY_COLOR}")

except Exception as e:
    print(f"ERRO: Não foi possível conectar ao servidor RPC.\n{e}")
    sys.exit(1)

# --- CONFIGURAÇÃO GRÁFICA ---
wn = turtle.Screen()
wn.title(f"Mover Bola - JOGADOR {MY_ID}")
wn.bgcolor("white")
wn.setup(width=600, height=600)
wn.tracer(0)  # Desliga atualização automática (nós controlamos o frame)

# Minha Tartaruga
head = turtle.Turtle()
head.speed(0)
head.shape("circle")
head.color(MY_COLOR)
head.penup()
head.goto(start_x, start_y)
head.direction = "stop"

# Dicionário para guardar os "bonecos" dos outros jogadores
# { id_jogador: objeto_turtle }
outros_jogadores = {}


# --- LÓGICA DE MOVIMENTO ---
def go_up(): head.direction = "up"


def go_down(): head.direction = "down"


def go_left(): head.direction = "left"


def go_right(): head.direction = "right"


def stop_move(): head.direction = "stop"


def move_local():
    """Calcula movimento local"""
    step = 3
    if head.direction == "up": head.sety(head.ycor() + step)
    if head.direction == "down": head.sety(head.ycor() - step)
    if head.direction == "left": head.setx(head.xcor() - step)
    if head.direction == "right": head.setx(head.xcor() + step)

    # Envia nova posição para o servidor (RPC)
    if head.direction != "stop":
        conn.root.mover(MY_ID, head.xcor(), head.ycor())


def atualizar_outros():
    """Pega estado do servidor e desenha os inimigos"""
    global outros_jogadores

    # Pede a lista completa pro servidor
    estado_geral = conn.root.get_estado()

    for pid, dados in estado_geral.items():
        pid = int(pid)  # Garante que é int

        # Ignora a mim mesmo
        if pid == MY_ID:
            continue

        # Se é um jogador novo que eu não conhecia, cria o boneco
        if pid not in outros_jogadores:
            novo_boneco = turtle.Turtle()
            novo_boneco.speed(0)
            novo_boneco.shape("circle")
            novo_boneco.color(dados['cor'])
            novo_boneco.penup()
            outros_jogadores[pid] = novo_boneco

        # Atualiza a posição dele na minha tela
        outros_jogadores[pid].goto(dados['x'], dados['y'])


# Bindings de Teclado
wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
# wn.onkeyrelease(stop_move, "w") # Opcional: Parar ao soltar tecla

# --- GAME LOOP ---
while True:
    wn.update()

    move_local()  # 1. Move meu boneco e avisa o servidor
    atualizar_outros()  # 2. Pergunta onde estão os outros e desenha

    time.sleep(0.02)  # 50 FPS