import rpyc
from rpyc.utils.server import ThreadedServer
import pymongo
import os
import time
import threading

MONGO_URI = os.getenv("MONGO_URI")
BATCH_SIZE = 5  # Lote pequeno pra ver dados mais rápido na tela

try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["f1_telemetria"]
    collection = db["logs_corrida"]
    print("✅ SSACP: Conectado ao Mongo!")
except Exception as e:
    print(f"❌ Erro Mongo: {e}")


class TelemetryService(rpyc.Service):
    def __init__(self):
        self.buffer = []
        self.lock = threading.Lock()

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_receber_dados(self, dados):
        with self.lock:
            self.buffer.append(dados)
            if len(self.buffer) >= BATCH_SIZE:
                self.flush()

    def flush(self):
        if not self.buffer: return
        try:
            collection.insert_many(self.buffer)
            print(f"💾 Salvo lote de {len(self.buffer)} registros.")
            self.buffer = []
        except Exception as e:
            print(f"Erro save: {e}")


if __name__ == "__main__":
    print("🚀 SSACP Rodando...")
    t = ThreadedServer(TelemetryService, port=50051, protocol_config={'allow_public_attrs': True})
    t.start()
