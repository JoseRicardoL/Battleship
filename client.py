import socket
import threading
import json
from colorama import init, Fore, Back, Style

init(autoreset=True)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_to_server():
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(("localhost", 8888))
    except Exception as e:
        print(f"Error connecting to server: {e}")
        exit()

connect_to_server()

player_id = None
attack_board = [[" " for _ in range(10)] for _ in range(10)]
defense_board = [[" " for _ in range(10)] for _ in range(10)]
current_player = None

def receive_messages():
    global player_id, attack_board, defense_board, current_player
    buffer = ""
    while True:
        try:
            buffer += client_socket.recv(2048).decode()
            while "\n" in buffer:
                message, buffer = buffer.split("\n", 1)
                if message:
                    if message.startswith("You are"):
                        print(message)
                        if "Player 1" in message:
                            player_id = 1
                        else:
                            player_id = 2
                    elif message == "start game":
                        print("Game started!")
                    elif message.startswith("update_boards"):
                        _, board_state = message.split(":", 1)
                        update_boards(json.loads(board_state))
                    elif message.startswith("current_player"):
                        _, current_player_id = message.split(":")
                        current_player = int(current_player_id)
                        if current_player == player_id:
                            print("Your turn!")
                        else:
                            print("Waiting for the other player to shoot.")
                    elif "hit" in message or "miss" in message:
                        result, coords, player = message.split(":")
                        if int(player) == player_id:
                            print(f"You {result} at {coords}!")
                        else:
                            print(f"Player {player} {result} at {coords}!")
                        print_board()
                    elif message == "Game over!":
                        print("Game over!")
                        client_socket.close()
                        break
                    elif "disconnected" in message:
                        print(message)
                        print("Trying to reconnect...")
                        client_socket.close()
                        connect_to_server()
                        continue
                    else:
                        print(message)
        except Exception as e:
            print(f"Error receiving message: {e}")
            print("Disconnected. Trying to reconnect...")
            client_socket.close()
            connect_to_server()
            continue

def print_board():
    print("\033c", end="")  # Clear console
    print("Your attack board:")
    print("  A B C D E F G H I J")
    for i, row in enumerate(attack_board):
        print(f"{i+1:2} {' '.join(row)}")
    print("Your defense board:")
    print("  A B C D E F G H I J")
    for i, row in enumerate(defense_board):
        print(f"{i+1:2} {' '.join([colorize_cell(cell) for cell in row])}")

def colorize_cell(cell):
    if cell == 'H':
        return Fore.RED + cell + Style.RESET_ALL
    elif cell == 'M':
        return Fore.BLUE + cell + Style.RESET_ALL
    elif cell == 'S':
        return Fore.GREEN + cell + Style.RESET_ALL
    elif cell == 'D':
        return Fore.YELLOW + cell + Style.RESET_ALL
    elif cell == 'X':
        return Back.WHITE + ' ' + Style.RESET_ALL
    return cell

def update_boards(state):
    global attack_board, defense_board
    attack_board = state["attack"]
    defense_board = state["defense"]
    print_board()

def main():
    threading.Thread(target=receive_messages).start()

    try:
        while True:
            if player_id and current_player == player_id:
                shot = input("Enter coordinates for your shot (e.g., A5), 'save' to save the game, 'load' to load the game, or 'exit' to exit: ")
                if shot.lower() == "exit":
                    client_socket.send("exit\n".encode())
                    break
                client_socket.send((shot + "\n").encode())
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client_socket.send("exit\n".encode())
        client_socket.close()


if __name__ == "__main__":
    main()
