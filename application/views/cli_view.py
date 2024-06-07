from termcolor import colored, cprint

class CLIView:
    def __init__(self, game_service, player_id, client_socket):
        self.game_service = game_service
        self.player_id = player_id
        self.client_socket = client_socket

    def start_game_interface(self):
        self.display_boards()
        while not self.game_service.check_game_over():
            if self.game_service.get_current_player() == self.player_id:
                self.display_turn()
                self.prompt_for_shot()
            else:
                print("Waiting for the other player to shoot.")
                self.receive_server_updates()

    def display_boards(self):
        print("Your attack board:")
        self.display_board(self.game_service.attack_boards[self.player_id])
        print("Your defense board:")
        self.display_board(self.game_service.defense_boards[self.player_id])

    def display_board(self, board):
        print("  A B C D E F G H I J")
        for i, row in enumerate(board):
            print(f"{i+1:2} {' '.join(row)}")

    def display_turn(self):
        print(f"Player {self.game_service.get_current_player()}'s turn")

    def prompt_for_shot(self):
        coordinates = input("Enter coordinates for your shot (e.g., A5) or 'P' to pause: ")
        if coordinates.lower() == 'p':
            self.pause_game()
        else:
            self.client_socket.send(coordinates.encode())
            self.receive_server_updates()

    def display_result(self, result):
        if result == "hit":
            print(colored("You hit an enemy ship!", "green"))
        elif result == "miss":
            print(colored("You missed!", "red"))
        elif result == "invalid":
            print(colored("Invalid coordinates, please try again.", "yellow"))

    def pause_game(self):
        print("Game Paused")
        while True:
            print("1. Resume Game")
            print("2. Save Game")
            print("3. Load Game")
            print("4. Return to Main Menu")
            choice = input("Enter your choice: ")
            if choice == '1':
                break
            elif choice == '2':
                filename = input("Enter the filename to save the game: ")
                self.game_service.save_game_state(filename)
                print("Game saved successfully.")
            elif choice == '3':
                filename = input("Enter the filename to load the game: ")
                self.game_service.load_game_state(filename)
                print("Game loaded successfully.")
                self.display_boards()
            elif choice == '4':
                exit()
            else:
                print("Invalid choice, please try again.")

    def receive_server_updates(self):
        try:
            while True:
                server_message = self.client_socket.recv(1024).decode()
                if server_message.startswith("hit") or server_message.startswith("miss") or server_message.startswith("invalid"):
                    result, coordinates, player_id = server_message.split(":")
                    self.game_service.update_boards(coordinates, result, int(player_id))
                    self.display_boards()
                    self.display_result(result)
                    if self.game_service.get_current_player() == self.player_id:
                        break
                elif server_message == "Game over!":
                    print("Game over!")
                    exit()
                elif server_message == "start game":
                    self.display_boards()
                else:
                    print(server_message)
        except Exception as e:
            print("Error receiving message.", e)
            self.client_socket.close()
            exit()
