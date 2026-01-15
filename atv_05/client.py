import socket
import time
import hashlib
import os

# Configurações
# Se estiver no Docker, o host é o nome do serviço ('server'). Se local, 'localhost'
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
PORT = 5000
SEGREDO = "segredo_comp"


def conectar():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Parte 2 (Falhas): Timeout
    # Se o servidor demorar mais que 3s, o cliente desiste
    client.settimeout(3.0)

    # Parte 2 (Falhas): Retry (Tentativas Automáticas)
    max_tentativas = 5
    for i in range(max_tentativas):
        try:
            print(f"Tentativa de conexão {i + 1}/{max_tentativas} em {SERVER_HOST}...")
            client.connect((SERVER_HOST, PORT))
            print("Conectado!")
            return client
        except Exception as e:
            print(f"Falha ao conectar: {e}. Tentando novamente em 2s...")
            time.sleep(2)
            # Recria o socket para nova tentativa
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(3.0)

    return None


def enviar_mensagem():
    client = conectar()
    if not client:
        print("FATAL: Não foi possível conectar ao servidor após várias tentativas.")
        return

    try:
        # Parte 3 (Segurança): Criando o Token
        msg = "Ola Professor!"
        token = hashlib.sha256(SEGREDO.encode()).hexdigest()
        payload = f"{msg}|{token}"

        print(f"Enviando: {payload}")
        client.send(payload.encode())

        # Aguarda resposta (sujeito ao timeout)
        data = client.recv(1024).decode()
        print(f"RESPOSTA DO SERVIDOR: {data}")

    except socket.timeout:
        print("ERRO DE FALHA (TIMEOUT): O servidor demorou muito para responder.")
    except Exception as e:
        print(f"Erro durante a comunicação: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    # Aguarda um pouco para garantir que o servidor subiu no Docker
    time.sleep(2)
    enviar_mensagem()