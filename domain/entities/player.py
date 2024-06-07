class Player:
    def __init__(self, name):
        self.name = name
        self.boats = []
        self.attacks_made = []

    def add_boat(self, boat):
        self.boats.append(boat)

    def record_attack(self, attack):
        self.attacks_made.append(attack)
