import rpyc
from rpyc.utils.server import ThreadedServer

JOGADORES = {}

class GameService(rpyc.Service):
    def exposed_registrar(self, pid, x, y, cor):
        JOGADORES[pid] = {'x': x, 'y': y, 'cor': cor}
        print(f"Novo Jogador: {pid} ({cor})")

    def exposed_mover(self, pid, x, y):
        if pid in JOGADORES:
            JOGADORES[pid]['x'] = x
            JOGADORES[pid]['y'] = y

    def exposed_get_estado(self):
        return JOGADORES

if __name__ == "__main__":
    t = ThreadedServer(GameService, port=18861, protocol_config={'allow_public_attrs': True})
    print("RPC Server Rodando...")
    t.start()