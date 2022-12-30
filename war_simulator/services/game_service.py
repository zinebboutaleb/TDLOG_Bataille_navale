from war_simulator.dao.game_dao import GameDao
from war_simulator.model.game import Game
from war_simulator.model.battlefield import Battlefield
from war_simulator.model.player import Player
from war_simulator.model.vessel import Vessel


class GameService:
    def __init__(self):
        self.game_dao = GameDao()

    def create_game(self, player_name: str, min_x: int, max_x: int, min_y: int,
                    max_y: int, min_z: int, max_z: int) -> int:
        game = Game()
        battlefield = Battlefield(min_x, max_x, min_y, max_y, min_z, max_z)
        game.add_player(Player(player_name, battlefield))
        return self.game_dao.create_game(game)

    def join_game(self, game_id: int, player_name: str) -> bool:
        game = self.game_dao.find_game(game_id)
        if game is None:
            return False
        # Vérifiez s'il y a déjà deux joueurs dans la partie
        if len(game.players) >= 2:
            return False
        # Créez le nouveau joueur et ajoutez-le à la partie
        battlefield = Battlefield(game.players[0].battlefield.min_x, game.players[0].battlefield.max_x,
                                   game.players[0].battlefield.min_y, game.players[0].battlefield.max_y,
                                   game.players[0].battlefield.min_z, game.players[0].battlefield.max_z)
        player = Player(player_name, battlefield)
        game.add_player(player)
        # Enregistrez la partie mise à jour dans la base de données
        self.game_dao.update_game(game)
        return True

    def get_game(self, game_id: int) -> Game:
        return self.game_dao.find_game(game_id)

    def add_vessel(self, game_id: int, player_name: str, vessel_type: str, x: int, y: int, z: int) -> bool:
        # Récupérer la partie en base de données
        game = self.game_dao.find_game(game_id)
        if game is None:
            return False
        # Vérifier si le joueur fait partie de la partie
        player = next((p for p in game.players if p.name == player_name), None)
        if player is None:
            return False
        # Vérifier si la position est disponible sur le champ de bataille du joueur
        if (x < player.battlefield.min_x or x > player.battlefield.max_x or
                y < player.battlefield.min_y or y > player.battlefield.max_y or
                z < player.battlefield.min_z or z > player.battlefield.max_z):
            return False
        # Vérifier si le joueur a atteint la limite de vaisseaux autorisés sur son champ de bataille
        if len(player.battlefield.vessels) >= player.battlefield.max_hits:
            return False
        # Créer le vaisseau et l'ajouter au champ de bataille du joueur
        vessel = Vessel(x, y, z, vessel_type)

        if not Battlefield.add_vessel(vessel):
            return False
        self.game_dao.db_session.merge(player)
        return True

    def shoot_at(self, game_id: int, shooter_name: str, vessel_id: int, x: int, y: int, z: int) -> bool:
        # Vérifier si la partie existe
        game = self.game_dao.find_game(game_id)
        if game is None:
            return False
        # Vérifier si le joueur fait partie de la partie
        shooter = next((p for p in game.players if p.name == shooter_name), None)
        if shooter is None:
            return False
        # Vérifier si le vaisseau appartient au joueur et s'il peut tirer
        vessel = next((v for v in shooter.battlefield.vessels if v.id == vessel_id and v.can_shoot()), None)
        if vessel is None:
            return False
        # Vérifier si la cible est dans la portée de l'arme du vaisseau
        if not vessel.in_range(x, y, z):
            return False
        # Trouver la cible (un vaisseau adverse)
        for p in game.players:
            if p.name == shooter_name:
                continue
            target = next((v for v in p.battlefield.vessels if v.coord_x == x and v.coord_y == y and v.coord_z == z),
                          None)
            if target is not None:
                break
        # Si la cible n'a pas été trouvée, cela signifie que
        # la coordonnée (x, y, z) ne correspond à aucun vaisseau
        # dans la partie
            if target is None:
                return False
        # Tirer sur la cible
            vessel.fire_at(target)
        # Mettre à jour la base de données
        self.game_dao.db_session.merge(shooter)

    def get_game_status(self, game_id: int, player_name: str) -> str:
        game = self.game_dao.find_game(game_id)
        if game is None:
            return "ENCOURS"

        # Vérifier si le joueur fait partie de la partie
        player = next((p for p in game.players if p.name == player_name), None)
        if player is None:
            return "ENCOURS"

        # Vérifier si le joueur a perdu
        if player.battlefield.all_vessels_destroyed():
            return "PERDU"

        # Vérifier si le joueur a gagné
        opponent = next((p for p in game.players if p.name != player_name), None)
        if opponent is not None and opponent.battlefield.all_vessels_destroyed():
            return "GAGNE"

        return "ENCOURS"
