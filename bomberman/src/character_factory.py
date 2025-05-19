from constants import resource_path
class CharacterFactory:
    _characters = {
        "bomberman": {
            "name": "Bomberman",
            "base_path": resource_path("assets/pictures/Bomberman/"),
            "speed": 5,
            "max_bombs": 3,
            "bomb_range": 3
        },
        "creep": {
            "name": "Creep",
            "base_path": resource_path("assets/pictures/Creep/"),
            "speed": 3,
            "max_bombs": 1,
            "bomb_range": 6
        },
        "grass": {
            "name": "Grass",
            "base_path": resource_path("assets/pictures/Grass/"),
            "speed": 6,
            "max_bombs": 2,
            "bomb_range": 3
        },
        "potato": {
            "name": "Potato",
            "base_path": resource_path("assets/pictures/Potato/"),
            "speed": 3,
            "max_bombs": 4,
            "bomb_range": 4
        },
        "wizard": {
            "name": "Wizard",
            "base_path": resource_path("assets/pictures/Wizard/"),
            "speed": 10,
            "max_bombs": 1,
            "bomb_range": 4
        },
    }

    @classmethod
    def create_character(cls, character_type: str, x: int, y: int):
        from character import Character
        if character_type not in cls._characters:
            raise ValueError(f"Unknown character type: {character_type}")

        config = cls._characters[character_type]
        char = Character(
            name=config["name"],
            base_path=config["base_path"],
            speed=config["speed"],
            max_bombs=config["max_bombs"],
            bomb_range=config["bomb_range"]
        )
        char.rect.update(x, y, char.rect.width, char.rect.height)
        return char

    @classmethod
    def get_available_characters(cls) -> list:
        return list(cls._characters.keys())