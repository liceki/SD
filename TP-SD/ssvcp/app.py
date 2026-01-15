import os
from flask import Flask, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Configuração de Conexão
# Tenta conectar no ReplicaSet. Se falhar, tenta localhost (fallback)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    db = client["f1_telemetria"]
    collection = db["logs_corrida"]
    # Força um teste de conexão
    client.server_info()
    print("✅ DASHBOARD: Conectado ao MongoDB com sucesso!")
except Exception as e:
    print(f"❌ DASHBOARD: Erro ao conectar no Mongo: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/telemetria')
def get_telemetria():
    try:
        # A MÁGICA ESTÁ AQUI: {"_id": 0}
        # Dizemos ao Mongo: "Me traga tudo, MENOS o campo _id que trava o JSON"
        cursor = collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(50)

        # Converte para lista
        data = list(cursor)

        # Retorna para o navegador
        return jsonify(data)

    except Exception as e:
        print(f"Erro na API: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)