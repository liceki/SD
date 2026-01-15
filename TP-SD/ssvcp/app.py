import os
from flask import Flask, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Configuração de Conexão
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    db = client["f1_telemetria"]
    collection = db["logs_corrida"]
    client.server_info()
    print("DASHBOARD: Conectado ao MongoDB Cluster")
except Exception as e:
    print(f"DASHBOARD: Erro Conexão: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/telemetria')
def get_telemetria():
    try:
        pipeline = [
            {"$sort": {"timestamp": -1}},
            # O ERRO ESTAVA AQUI. Mudado de $car_id para $carro_id
            {"$group": {
                "_id": "$carro_id",
                "doc_inteiro": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$doc_inteiro"}},
            {"$project": {"_id": 0}},
            {"$sort": {"numero": 1}}
        ]

        data = list(collection.aggregate(pipeline))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)