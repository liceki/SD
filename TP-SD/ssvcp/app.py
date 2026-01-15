import os
from flask import Flask, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

# --- CONFIGURAÇÃO DE CONEXÃO ---
# Tenta conectar no ReplicaSet. Se falhar, tenta localhost (fallback)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")

try:
    # Timeout ajustado para não travar se o banco demorar
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    db = client["f1_telemetria"]
    collection = db["logs_corrida"]

    # Força um teste de conexão imediato
    client.server_info()
    print("✅ DASHBOARD: Conectado ao MongoDB com sucesso!")
except Exception as e:
    print(f"❌ DASHBOARD: Erro ao conectar no Mongo: {e}")


# --- ROTAS ---
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/telemetria')
def get_telemetria():
    try:
        # PIPELINE DE AGREGAÇÃO
        # Este é o segredo para pegar o último dado de cada carro
        pipeline = [
            # 1. Ordena TUDO por tempo (do mais recente para o mais antigo)
            {"$sort": {"timestamp": -1}},

            # 2. Agrupa pelos carros
            # ATENÇÃO: O campo "$car_id" deve ser exatamente como está no teu banco.
            # Se no banco for 'driver_number', muda para "$driver_number"
            {"$group": {
                "_id": "$car_id",
                "doc_inteiro": {"$first": "$$ROOT"}  # Pega o primeiro que encontrar (o mais recente)
            }},

            # 3. Limpa a estrutura para retornar o objeto original
            {"$replaceRoot": {"newRoot": "$doc_inteiro"}},

            # 4. Remove o _id interno do Mongo (opcional, mas deixa o JSON mais limpo)
            {"$project": {"_id": 0}},

        ]

        # Executa o comando no banco
        dados_agrupados = list(collection.aggregate(pipeline))

        # Se a lista vier vazia, imprime um aviso no terminal do Python
        if not dados_agrupados:
            print("⚠️ AVISO: A consulta retornou 0 carros. Verifique se o nome do campo 'car_id' está correto.")

        return jsonify(dados_agrupados)

    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)