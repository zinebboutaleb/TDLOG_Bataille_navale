import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from model.game import Game
from services.game_service import GameService
app = FastAPI()
game_service = GameService()


class CreateGameData(BaseModel):
    player_name: str
    min_x: int
    max_x: int
    min_y: int
    max_y: int
    min_z: int
    max_z: int


@app.post("/create-game")
async def create_game(game_data: CreateGameData):
    return game_service.create_game(game_data.player_name, game_data.min_x,
                                    game_data.max_x, game_data.min_y,
                                    game_data.max_y, game_data.min_z,
                                    game_data.max_z)


@app.get("/get-game")
async def get_game(game_id: int) -> Game:
    return game_service.get_game(game_id)
