from domain.entities.boat import Boat

class BoatRepository:
    def __init__(self):
        self.boats = []

    def add_boat(self, boat):
        self.boats.append(boat)

    def get_all_boats(self):
        return self.boats

    def clear_boats(self):
        self.boats = []
