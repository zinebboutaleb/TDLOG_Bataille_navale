from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from war_simulator.model.game import Game
from war_simulator.model.player import Player
from war_simulator.model.vessel import Vessel

engine = create_engine('sqlite:////tmp/tdlog.db', echo=True, future=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)


class GameEntity(Base):
    __tablename__ = 'game'
    id = Column(Integer, primary_key=True)
    players = relationship("PlayerEntity", back_populates="game", cascade="all, delete-orphan")


class PlayerEntity(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    game = relationship("GameEntity", back_populates="players")
    battlefield = relationship("BattlefieldEntity",
                                back_populates="player",
                                uselist=False, cascade="all, delete-orphan")


class BattlefieldEntity(Base):
    __tablename__ = 'battlefield'
    id = Column(Integer, primary_key=True)
    min_x = Column(Integer, nullable=False)
    min_y = Column(Integer, nullable=False)
    min_z = Column(Integer, nullable=False)
    max_x = Column(Integer, nullable=False)
    max_y = Column(Integer, nullable=False)
    max_z = Column(Integer, nullable=False)
    max_power = Column(Integer, nullable=False)
    player_id = Column(Integer, ForeignKey("player.id"), nullable=False)
    player = relationship("PlayerEntity", back_populates="battlefield")
    vessel = relationship("VesselEntity", back_populates="battlefield",
                          uselist=False, cascade="all, delete-orphan")


class VesselEntity(Base):
    __tablename__ = 'vessel'
    id = Column(Integer, primary_key=True)
    coord_x = Column(Integer, nullable=False)
    coord_y = Column(Integer, nullable=False)
    coord_z = Column(Integer, nullable=False)
    hits_to_be_destroyed = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    battlefield_id = Column(Integer, ForeignKey("battlefield.id"), nullable=False)
    battlefield = relationship("BattlefieldEntity", back_populates="vessel")
    weapon = relationship("WeaponEntity", back_populates="vessel",
                          uselist=False, cascade="all, delete-orphan")


class WeaponEntity(Base):
    __tablename__ = 'weapon'
    id = Column(Integer, primary_key=True)
    ammunitions = Column(Integer, nullable=False)
    range = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    vessel_id = Column(Integer, ForeignKey("vessel.id"), nullable=False)
    vessel = relationship("VesselEntity", back_populates="weapon")


class GameDao:
    def __init__(self):
        Base.metadata.create_all()
        self.db_session = Session()
    def create_game(self, game: Game) -> int:
        game_entity = self.map_to_game_entity(game)
        self.db_session.add(game_entity)
        self.db_session.commit()
        return game_entity.id
    def find_game(self, game_id: int) -> Game:
        stmt = select(GameEntity).where(GameEntity.id == game_id)
        game_entity = self.db_session.scalars(stmt).one()
        return self.map_to_game(game_entity)

    def update_game(self, game: Game):
        game_entity = self.map_to_game_entity(game)
        self.db_session.merge(game_entity)              #La méthode merge de la session SQLAlchemy
        self.db_session.commit()                        # permet de mettre à jour
                                                        # une entité en base de données.

    def map_to_game_entity(game : Game) -> GameEntity:
        game_entity = GameEntity()
        return GameEntity

    def map_to_game(game_entity : GameEntity) -> Game:
        game = Game(game_entity.id)
        game.id = game_entity.id
        return game


class PlayerDao:
    def __init__(self):
        Base.metadata.create_all()
        self.db_session = Session()

    def create_player(self, player: Player) -> int:
        player_entity = self.map_to_player(Player)
        self.db_session.add(player_entity)
        self.db_session.commit()
        return player_entity.id

    def find_player(self, player_id: int) -> Player:
        stmt = select(PlayerEntity).where(PlayerEntity.id == player_id)
        player_entity = self.db_session.scalars(stmt).one()
        return self.map_to_player(player_entity)

    def map_to_player_entity(player : Player) -> PlayerEntity:
        player_entity = PlayerEntity()
        player_entity.name = player.name
        player_entity.battlefield = player.battlefield
        return PlayerEntity

    def map_to_player(player_entity : PlayerEntity) -> Player:
        player = Player(player_entity.name,player_entity.battlefield)
        player.id = ( player_entity.id)
        return player

class VesselDao:
    def __init__(self):
        Base.metadata.create_all()
        self.db_session = Session()

    def create_vessel(self, vessel: Vessel) -> int:
        vessel_entity = self.map_to_vessel(vessel)
        self.db_session.add(vessel_entity)
        self.db_session.commit()
        return vessel_entity.id

    def find_vessel(self, vessel_id: int) -> Vessel:
        stmt = select(VesselEntity).where(Vessel.id == vessel_id)
        vessel_entity = self.db_session.scalars(stmt).one()
        return self.map_to_vessel(vessel_entity)

    def map_to_vessel_entity(vessel : Vessel,type) -> VesselEntity:
        vessel_entity = VesselEntity()
        vessel_entity.coordinates = (VesselEntity.coord_x,VesselEntity.coord_y,VesselEntity.coord_z)
        vessel_entity.hits_to_be_destroyed = vessel.hits_to_be_destroyed
        vessel_entity.weapon = vessel.weapon
        vessel_entity.type = type
        return vessel_entity

    def map_to_vessel(vessel_entity : VesselEntity,type) -> Vessel:
        vessel = Vessel((vessel_entity.coord_x,vessel_entity.coord_y,vessel_entity.coord_z),
                        vessel_entity.hits_to_be_destroyed,vessel_entity.weapon)
        vessel.id = ( vessel_entity.id)
        return vessel
