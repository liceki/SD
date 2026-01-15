import rpyc
from rpyc.utils.server import ThreadedServer
import pymongo
import os
import time
import threading

# Configurações
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
BATCH_SIZE = 10  # Salva a cada 10 registros
FLUSH_INTERVAL = 2 # Ou a cada 2 segundos (o que vier primeiro)

# Conexão Banco
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["f1_telemetria"]
    collection = db["logs_corrida"]
    print("✅ SSACP: Conectado ao Mongo!")
except Exception as e:
    print(f"❌ SSACP: Erro Mongo: {e}")

class TelemetryService(rpyc.Service):
    def __init__(self):
        self.buffer = []
        self.last_flush = time.time()
        self.lock = threading.Lock()
        # Inicia thread de limpeza por tempo
        t = threading.Thread(target=self._periodic_flush, daemon=True)
        t.start()

    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_receber_dados(self, dados):
        """Recebe um objeto (dicionário) do ISCCP"""
        with self.lock:
            self.buffer.append(dados)
            # Se encheu o balde, salva no banco
            if len(self.buffer) >= BATCH_SIZE:
                self._flush_to_db()

    def _flush_to_db(self):
        if not self.buffer:
            return

        try:
            # BULK INSERT (O segredo da performance)
            collection.insert_many(self.buffer)
            print(f"BATCH SAVE: {len(self.buffer)} registros salvos.")
            self.buffer = [] # Limpa balde
            self.last_flush = time.time()
        except Exception as e:
            print(f"⚠️ Erro ao salvar batch: {e}")

    def _periodic_flush(self):
        """Garante que dados não fiquem presos se o batch não encher"""
        while True:
            time.sleep(1)
            with self.lock:
                if self.buffer and (time.time() - self.last_flush > FLUSH_INTERVAL):
                    print("⏰ Time Flush...")
                    self._flush_to_db()

if __name__ == "__main__":
    # Inicia Servidor RPC na porta 18861 (Padrão RPyC)
    print("SSACP (Aggregator) rodando na porta 50051...")
    t = ThreadedServer(TelemetryService, port=50051, protocol_config={'allow_public_attrs': True})
    t.start()