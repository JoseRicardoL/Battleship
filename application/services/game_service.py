import json
from domain.entities.boat import Boat

class GameService:
    def __init__(self, player_repository, boat_repository):
        self.player_repository = player_repository
        self.boat_repository = boat_repository
        self.shots = {1: set(), 2: set()}
        self.current_player = 1
        self.game_over = False
        self.defense_boards = {1: [[' ' for _ in range(10)] for _ in range(10)],
                               2: [[' ' for _ in range(10)] for _ in range(10)]}
        self.attack_boards = {1: [[' ' for _ in range(10)] for _ in range(10)],
                              2: [[' ' for _ in range(10)] for _ in range(10)]}
        self.initialize_boats()

    def initialize_boats(self):
        self.boat_repository.add_boat(Boat("Destroyer", 3, ["A5", "A6", "A7"], 1))
        self.boat_repository.add_boat(Boat("Submarine", 3, ["B2", "C2", "D2"], 1))
        self.boat_repository.add_boat(Boat("Destroyer", 3, ["D5", "D6", "D7"], 2))
        self.boat_repository.add_boat(Boat("Submarine", 3, ["E2", "F2", "G2"], 2))
        for boat in self.boat_repository.get_all_boats():
            for position in boat.positions:
                col, row = ord(position[0].upper()) - ord('A'), int(position[1:]) - 1
                self.defense_boards[boat.owner][row][col] = boat.name[0]

    def process_shot(self, coordinates):
        if not self.is_valid_shot(coordinates):
            return "invalid"
        hit_boat = self.is_hit(coordinates)
        if hit_boat:
            self.update_game_state_after_hit(coordinates, hit_boat)
            return "hit"
        else:
            self.update_attack_board(coordinates, "miss")
            self.update_defense_board(coordinates, "miss")
            self.switch_player()
            return "miss"

    def is_hit(self, coordinates):
        for boat in self.boat_repository.get_all_boats():
            if boat.owner != self.current_player and coordinates in boat.positions:
                return boat
        return None

    def update_game_state_after_hit(self, hit_coordinates, hit_boat):
        hit_boat.positions.remove(hit_coordinates)
        self.update_attack_board(hit_coordinates, "hit")
        self.update_defense_board(hit_coordinates, "hit")
        if not hit_boat.positions:
            self.check_all_boats_sunk()
        if not self.game_over:
            self.switch_player()

    def check_all_boats_sunk(self):
        opponent = 1 if self.current_player == 2 else 2
        all_sunk = all(not boat.positions for boat in self.boat_repository.get_all_boats() if boat.owner == opponent)
        if all_sunk:
            self.game_over = True

    def switch_player(self):
        self.current_player = 1 if self.current_player == 2 else 2

    def is_valid_shot(self, coordinates):
        if coordinates in self.shots[self.current_player] or not self.is_within_board(coordinates):
            return False
        self.shots[self.current_player].add(coordinates)
        return True

    def is_within_board(self, coordinates):
        col = ord(coordinates[0].upper()) - ord('A')
        row = int(coordinates[1:]) - 1
        return 0 <= col < 10 and 0 <= row < 10

    def check_game_over(self):
        return self.game_over

    def get_current_player(self):
        return self.current_player

    def save_game_state(self, filename):
        game_state = {
            "shots": {1: list(self.shots[1]), 2: list(self.shots[2])},
            "current_player": self.current_player,
            "game_over": self.game_over,
            "boats": [
                {
                    "name": boat.name,
                    "size": boat.size,
                    "positions": boat.positions,
                    "owner": boat.owner,
                }
                for boat in self.boat_repository.get_all_boats()
            ],
            "defense_boards": {str(k): v for k, v in self.defense_boards.items()},
            "attack_boards": {str(k): v for k, v in self.attack_boards.items()},
        }
        with open(filename, 'w') as file:
            json.dump(game_state, file)

    def load_game_state(self, filename):
        with open(filename, 'r') as file:
            game_state = json.load(file)
        self.shots = {1: set(game_state["shots"]["1"]), 2: set(game_state["shots"]["2"])}
        self.current_player = game_state["current_player"]
        self.game_over = game_state["game_over"]
        self.boat_repository.clear_boats()
        for boat_data in game_state["boats"]:
            boat = Boat(
                name=boat_data["name"],
                size=boat_data["size"],
                positions=boat_data["positions"],
                owner=boat_data["owner"]
            )
            self.boat_repository.add_boat(boat)
        self.defense_boards = {int(k): v for k, v in game_state["defense_boards"].items()}
        self.attack_boards = {int(k): v for k, v in game_state["attack_boards"].items()}

    def update_attack_board(self, coordinates, result):
        col, row = ord(coordinates[0].upper()) - ord('A'), int(coordinates[1:]) - 1
        if result == "hit":
            self.attack_boards[self.current_player][row][col] = 'H'
        elif result == "miss":
            self.attack_boards[self.current_player][row][col] = 'M'

    def update_defense_board(self, coordinates, result):
        opponent = 1 if self.current_player == 2 else 2
        col, row = ord(coordinates[0].upper()) - ord('A'), int(coordinates[1:]) - 1
        if result == "hit":
            self.defense_boards[opponent][row][col] = 'H'
        elif result == "miss":
            self.defense_boards[opponent][row][col] = 'X'

    def update_boards(self, coordinates, result, player_id):
        if result == "hit":
            self.update_attack_board(coordinates, "hit")
            self.update_defense_board(coordinates, "hit")
        elif result == "miss":
            self.update_attack_board(coordinates, "miss")
            self.update_defense_board(coordinates, "miss")
