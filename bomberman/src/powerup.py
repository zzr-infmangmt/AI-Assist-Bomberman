import pygame
from constants import resource_path
class Powerup:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 64, 64)
        self.type = type
        self.image = self._load_image(f"assets/pictures/Powerups/{type}.png")

    def _load_image(self, path):
        try:
            # 使用resource_path函数获取正确的路径
            full_path = resource_path(path)
            return pygame.image.load(full_path).convert_alpha()
        except pygame.error:
            # print(f"Failed to load powerup image: {path}")
            return pygame.Surface(((64, 64), pygame.SRCALPHA))

    def draw(self, screen, offset=(0, 0)):
        """绘制道具，支持抖动偏移"""
        screen.blit(self.image, (self.rect.x + offset[0], self.rect.y + offset[1]))