import os
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI)
    db = client["atividade2"]
    collection = db["pessoas"]
except Exception as e:
    print(f"Erro ao conectar no Mongo: {e}")


@app.route('/painel', methods=['GET'])
def painel():
    return render_template('index.html')



@app.route('/', methods=['GET'])
def query_records():
    name = request.args.get('name')
    if name:
        # Busca específica
        record = collection.find_one({"name": name}, {"_id": 0})
        if record:
            return jsonify(record)
        return jsonify({'error': 'data not found'})

    # Se não passar nome, retorna tudo (para preencher nossa tabela)
    records = list(collection.find({}, {"_id": 0}))
    return jsonify(records)


@app.route('/', methods=['POST'])
def create_record():
    # Suporta JSON (curl) ou Form (navegador)
    record = request.get_json() or request.form.to_dict()

    if not record.get('name'):
        return jsonify({'error': 'Nome obrigatorio'}), 400

    if collection.find_one({"name": record['name']}):
        return jsonify(
            {'error': 'Registro ja existe'}), 400  # O original apenas sobrescrevia ou duplicava, aqui protegemos

    collection.insert_one(record)

    if '_id' in record: del record['_id']

    return jsonify(record)


@app.route('/', methods=['PUT'])
def update_record():
    record = request.get_json()
    # Atualiza o email onde o nome for igual
    result = collection.update_one(
        {"name": record['name']},
        {"$set": {"email": record['email']}}
    )

    if result.matched_count > 0:
        return jsonify(record)
    return jsonify({'error': 'data not found'})


@app.route('/', methods=['DELETE'])
def delete_record():
    record = request.get_json()
    result = collection.delete_one({"name": record['name']})

    if result.deleted_count > 0:
        return jsonify(record)
    return jsonify({'error': 'data not found'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)