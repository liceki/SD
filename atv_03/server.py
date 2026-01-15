import rpyc
from rpyc.utils.server import ThreadedServer
import random

# Estado Global do Jogo (Memória do Servidor)
# Formato: { id_jogador: {'x': 0, 'y': 0, 'cor': 'red'} }
JOGADORES = {}

CORES_DISPONIVEIS = ["red", "blue", "green", "yellow", "purple", "orange", "black", "pink"]


class GameService(rpyc.Service):
    def on_connect(self, conn):
        print("Novo jogador conectado!")

    def on_disconnect(self, conn):
        print("Jogador desconectado.")

    # --- MÉTODOS EXPOSTOS (RPC) ---

    def exposed_entrar(self):
        """Registra um novo jogador e retorna ID e Cor"""
        novo_id = len(JOGADORES) + 1
        cor = random.choice(CORES_DISPONIVEIS)

        # Posição inicial aleatória para não nascerem todos encavalados
        start_x = random.randint(-100, 100)
        start_y = random.randint(-100, 100)

        JOGADORES[novo_id] = {'x': start_x, 'y': start_y, 'cor': cor}
        print(f"Jogador {novo_id} ({cor}) entrou em ({start_x}, {start_y})")
        return novo_id, cor, start_x, start_y

    def exposed_mover(self, id_jogador, x, y):
        """Atualiza a posição de um jogador"""
        if id_jogador in JOGADORES:
            JOGADORES[id_jogador]['x'] = x
            JOGADORES[id_jogador]['y'] = y

    def exposed_get_estado(self):
        """Retorna a lista de todos os jogadores para atualização da tela"""
        return JOGADORES


if __name__ == "__main__":
    # allow_public_attrs=True é essencial para passar dicionários via rede
    t = ThreadedServer(GameService, port=18861, protocol_config={'allow_public_attrs': True})
    print("🚀 Servidor de Jogo RPC rodando na porta 18861...")
    t.start()