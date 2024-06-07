from domain.entities.player import Player

class PlayerRepository:
    def __init__(self):
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def get_all_players(self):
        return self.players

    def clear_players(self):
        self.players = []
