import socket
import threading
import json
import os

clients = {}
lock = threading.Lock()
game_service = None
SAVE_FILE = "game_save.json"

def broadcast(message, exclude_client=None):
    with lock:
        disconnected_clients = []
        for client in list(clients.keys()):
            if client != exclude_client:
                try:
                    client.sendall((message + "\n").encode())  # Ensure each message ends with a newline
                except Exception as e:
                    print(f"Error sending message to client: {e}")
                    disconnected_clients.append(client)
        for client in disconnected_clients:
            del clients[client]

def handle_client(client_socket, addr, player_id):
    global game_service
    clients[client_socket] = {"id": player_id}
    print(f"Player {player_id} connected from {addr}")

    try:
        while True:
            message = client_socket.recv(2048).decode().strip()
            if message == "":
                raise Exception("Client disconnected")
            # Resto de la lógica de manejo de mensajes aquí...
    except Exception as e:
        print(f"Connection lost with player {player_id}: {e}")
        client_socket.close()
        del clients[client_socket]
        broadcast(f"Player {player_id} disconnected. Waiting for player...", exclude_client=client_socket)
    finally:
        client_socket.close()

def main():
    global game_service
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen(2)  # Solo permite hasta 2 conexiones pendientes.

    print("Servidor iniciado en el puerto 8888")
    active_players = 0

    while True:
        if active_players < 2:
            client_socket, addr = server.accept()
            print(f"Conexión aceptada de: {addr}")

            # Incrementar contador de jugadores activos.
            active_players += 1
            player_id = active_players

            threading.Thread(target=handle_client, args=(client_socket, addr, player_id)).start()
        else:
            # Cerrar conexiones extras inmediatamente.
            extra_socket, addr = server.accept()
            extra_socket.send("Server is full. Please try again later.\n".encode())
            extra_socket.close()


if __name__ == "__main__":
    main()
