from abc import ABC, abstractmethod

class PlayerRepositoryInterface(ABC):
    @abstractmethod
    def add_player(self, player):
        pass

    @abstractmethod
    def remove_player(self, player):
        pass

    @abstractmethod
    def find_player(self, criteria):
        pass
