import rpyc
from rpyc.utils.server import ThreadedServer
import pymongo
import os
import time
import threading
import sys

# Força o print aparecer no log do Docker imediatamente
sys.stdout.reconfigure(line_buffering=True)

MONGO_URI = os.getenv("MONGO_URI")
# Batch size reduzido para 1 para garantir que TUDO seja salvo na hora durante o teste
BATCH_SIZE = 1

print(f"🔧 SSACP INICIANDO... Tentando conectar ao Mongo: {MONGO_URI}")

try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["f1_telemetria"]
    collection = db["logs_corrida"]
    # Teste de conexão real
    client.server_info()
    print("✅ SSACP: Conectado ao Cluster MongoDB com sucesso!")
except Exception as e:
    print(f"❌ SSACP: ERRO FATAL DE CONEXÃO MONGO: {e}")


class TelemetryService(rpyc.Service):
    def __init__(self):
        self.buffer = []
        self.lock = threading.Lock()

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_receber_dados(self, dados):
        # PRINT DE DEBUG: Mostra exatamente o que chegou
        print(f"📥 RECEBIDO: Carro {dados.get('numero')} | {dados.get('sensor_responsavel')}")

        with self.lock:
            self.buffer.append(dados)
            if len(self.buffer) >= BATCH_SIZE:
                self.flush()

    def flush(self):
        if not self.buffer: return
        try:
            # Tenta salvar
            result = collection.insert_many(self.buffer)
            print(f"💾 SALVO NO BANCO: {len(result.inserted_ids)} registros.")
            self.buffer = []
        except Exception as e:
            print(f"❌ ERRO AO SALVAR NO MONGO: {e}")


if __name__ == "__main__":
    print("🚀 SSACP Servidor RPC Pronto na porta 50051")
    t = ThreadedServer(TelemetryService, port=50051, protocol_config={'allow_public_attrs': True})
    t.start()