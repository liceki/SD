import socket
import time
import hashlib
import os

# Configurações de Rede (Lê do Docker ou usa localhost)
HOST = '0.0.0.0'  # No Docker tem que ser 0.0.0.0
PORT = 5000
SEGREDO = "segredo_comp"  # Senha compartilhada


def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print(f"--- Servidor ouvindo em {HOST}:{PORT} ---")

    while True:
        try:
            print("Aguardando conexão...")
            conn, addr = server.accept()
            print(f"Conectado por {addr}")

            # Parte 2 (Falhas): Simulando um processamento lento (Delay)
            # Descomente a linha abaixo para testar o Timeout no cliente
            time.sleep(1)

            # Recebe dados
            data = conn.recv(1024).decode()
            if not data:
                break

            print(f"Dados brutos recebidos: {data}")

            # Parte 3 (Segurança): Validação do Token
            try:
                msg, token_recebido = data.split('|')

                # Recalcula o hash para ver se bate
                hash_esperado = hashlib.sha256(SEGREDO.encode()).hexdigest()

                if token_recebido == hash_esperado:
                    resposta = f"SUCESSO: Mensagem '{msg}' autenticada!"
                    print("Status: Token Válido.")
                else:
                    resposta = "ERRO: Falha na autenticação (Token inválido)."
                    print("Status: Token Inválido.")

            except ValueError:
                resposta = "ERRO: Formato da mensagem incorreto."

            conn.send(resposta.encode())
            conn.close()

        except Exception as e:
            print(f"Erro no servidor: {e}")


if __name__ == "__main__":
    iniciar_servidor()