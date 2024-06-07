from abc import ABC, abstractmethod

class BoatRepositoryInterface(ABC):
    @abstractmethod
    def add_boat(self, boat):
        pass

    @abstractmethod
    def remove_boat(self, boat):
        pass

    @abstractmethod
    def find_boat(self, criteria):
        pass

    @abstractmethod
    def get_all_boats(self):
        pass
