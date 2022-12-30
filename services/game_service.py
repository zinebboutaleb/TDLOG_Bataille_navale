from dao.game_dao import GameDao
from model.game import Game
from model.battlefield import Battlefield
from model.player import Player
from model.vessel import Vessel


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
        battle_field = Battlefield(game.players[0].battle_field.min_x, game.players[0].battle_field.max_x,
                                   game.players[0].battle_field.min_y, game.players[0].battle_field.max_y,
                                   game.players[0].battle_field.min_z, game.players[0].battle_field.max_z)
        player = Player(player_name, battle_field)
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
        if (x < player.battle_field.min_x or x > player.battle_field.max_x or
                y < player.battle_field.min_y or y > player.battle_field.max_y or
                z < player.battle_field.min_z or z > player.battle_field.max_z):
            return False
        # Vérifier si le joueur a atteint la limite de vaisseaux autorisés sur son champ de bataille
        if len(player.battle_field.vessels) >= player.battle_field.max_hits:
            return False
        # Créer le vaisseau et l'ajouter au champ de bataille du joueur
        vessel = Vessel(x, y, z, vessel_type)

        if not Battlefield.add_vessel(vessel):
            return False
        self.game_dao.db_session.merge(player)
        return True
