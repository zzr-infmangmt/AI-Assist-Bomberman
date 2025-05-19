import pygame
import random
from constants import TILE_SIZE, TILE_EMPTY, TILE_SOLID, TILE_EXPLODABLE,resource_path
from powerup import Powerup

class Map:
    def __init__(self, map_data):
        self.map_data = map_data
        self.solid_block = self._load_image("assets/pictures/Blocks/SolidBlock.png")
        self.explodable_block = self._load_image("assets/pictures/Blocks/ExplodableBlock.png")
        self.powerups = []

    def _load_image(self, path):
        try:
            # 使用resource_path函数获取正确的路径
            return pygame.image.load(resource_path(path)).convert()
        except pygame.error:
            print(f"Failed to load image: {path}")
            return pygame.Surface((TILE_SIZE, TILE_SIZE))

    def draw(self, screen,offset =(0,0)):
        """绘制地图到指定屏幕"""
        for row_index, row in enumerate(self.map_data):
            for col_index, tile in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE

                if tile == TILE_SOLID:
                    screen.blit(self.solid_block, (x, y))
                elif tile == TILE_EXPLODABLE:
                    screen.blit(self.explodable_block, (x, y))
        # 绘制道具
        for powerup in self.powerups:
            powerup.draw(screen, offset)

    def is_tile_passable(self, x, y):
        """检查指定坐标的格子是否可通过"""
        if 0 <= y < len(self.map_data) and 0 <= x < len(self.map_data[0]):
            return self.map_data[y][x] == TILE_EMPTY
        return False

    def get_tile_type(self, x, y):
        """获取指定坐标的格子类型"""
        if 0 <= y < len(self.map_data) and 0 <= x < len(self.map_data[0]):
            return self.map_data[y][x]
        return TILE_SOLID  # 边界视为固体墙

    def destroy_tile(self, x, y):
        """摧毁指定坐标的格子(如果是可爆炸的)"""
        if self.get_tile_type(x, y) == TILE_EXPLODABLE:
            self.map_data[y][x] = TILE_EMPTY

            # 有一定概率生成道具
            if random.random() < 0.25:  # 25% 的概率生成道具
                powerup_type = random.choice(["BombPowerup", "FlamePowerup", "SpeedPowerup"])
                powerup = Powerup(x * TILE_SIZE, y * TILE_SIZE, powerup_type)
                self.powerups.append(powerup)
            return True
        return False

    def update(self, players):
        """更新道具状态"""
        for powerup in self.powerups[:]:  # 使用副本遍历
            powerup_rect = pygame.Rect(powerup.rect.x, powerup.rect.y, TILE_SIZE, TILE_SIZE)

            for player in players:
                if player.alive and player.rect.colliderect(powerup_rect):
                    self.powerups.remove(powerup)
                    # 这里添加道具效果（如增加炸弹范围/数量等）
                    if powerup.type == "BombPowerup":
                        player.max_bombs = min(player.max_bombs + 1, 10)
                    elif powerup.type == "FlamePowerup":
                        player.bomb_range = min(player.bomb_range + 1, 5)
                    break