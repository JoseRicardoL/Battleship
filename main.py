from application.views.cli_view import CLIView
from application.services.game_service import GameService
from infrastructure.persistence.player_repository import PlayerRepository
from infrastructure.persistence.boat_repository import BoatRepository

def main():
    while True:
        player_repository = PlayerRepository()
        boat_repository = BoatRepository()
        game_service = GameService(player_repository, boat_repository)
        cli_view = CLIView(game_service)
        cli_view.start_game_interface()
        break

if __name__ == "__main__":
    main()
