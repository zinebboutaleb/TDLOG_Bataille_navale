from battlefield import Battlefield


class Player:
    def __init__(self, name: str, battlefield: Battlefield):
        self.id = None
        self.name = name
        self.battlefield = battlefield

    def get_name(self) -> str:
        return self.name

    def get_battlefield(self) -> Battlefield:
        return self.battlefield
