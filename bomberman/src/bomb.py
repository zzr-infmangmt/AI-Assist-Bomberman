import pygame
from constants import TILE_SIZE, BOMB_DELAY, FLAME_DURATION,resource_path
from animations import Animation
import math

class Bomb:
    _shared_hint_surface = pygame.Surface((1, 1), pygame.SRCALPHA)  # 初始占位，后续动态调整大小
    _last_pulse_update = 0
    _current_pulse_factor = 0
    def __init__(self, x, y, owner, bomb_range, game_map):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.owner = owner
        self.plant_time = pygame.time.get_ticks()
        self.exploded = False
        self.flames = []
        self.bomb_range = bomb_range
        self.game_map = game_map

        # 预加载动画资源
        self._load_animations()
        self.explosion_range = self._calculate_explosion_range(game_map)
    @classmethod
    def update_pulse_factor(cls):
        """类方法：统一更新所有炸弹的脉冲因子（每帧调用一次）"""
        cls._last_pulse_update = pygame.time.get_ticks()
        cls._current_pulse_factor = 0.5 * (1 + math.sin(cls._last_pulse_update / 200))

    def _calculate_explosion_range(self, game_map):
        """计算爆炸范围，返回所有会被火焰覆盖的格子坐标"""
        center_x = self.rect.centerx // TILE_SIZE
        center_y = self.rect.centery // TILE_SIZE
        range_tiles = [(center_x, center_y)]  # 中心点

        # 四个方向检查
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            for i in range(1, self.bomb_range + 1):
                x, y = center_x + dx * i, center_y + dy * i
                # 检查game_map是Map对象还是直接是map_data列表
                map_data = game_map.map_data if hasattr(game_map, 'map_data') else game_map
                if not (0 <= y < len(map_data) and 0 <= x < len(map_data[0])):
                    break  # 超出地图边界
                if map_data[y][x] == 1:  # 碰到不可摧毁的墙
                    break
                range_tiles.append((x, y))
                if map_data[y][x] == 2:  # 碰到可摧毁的墙，火焰会停止传播但包含该位置
                    break
        return range_tiles

    def _load_animations(self):
        bomb_frames = [
            resource_path(f"assets/pictures/Bomb/Bomb_f0{i}.png") for i in range(1, 4)
        ]
        self.animation = Animation(bomb_frames, interval=200)

        flame_sheet_path = resource_path("assets/pictures/Flame/Flame.png")
        flame_sheet = pygame.image.load(flame_sheet_path).convert_alpha()
        self.flame_animation = Animation(flame_sheet, interval=100)

    def update(self, current_time, game_map):
        """更新炸弹状态"""
        if not self.exploded:
            self.animation.update(current_time)
            if current_time - self.plant_time > BOMB_DELAY:
                # 确保传递正确的map_data
                map_data = game_map.map_data if hasattr(game_map, 'map_data') else game_map
                self.explode(current_time, map_data)
        else:
            for flame in self.flames[:]:
                if current_time - flame['time'] > FLAME_DURATION:
                    self.flames.remove(flame)

    def explode(self, current_time, game_map):
        """炸弹爆炸"""
        self.exploded = True
        # 确保传递的是map_data而不是Map对象
        map_data = game_map.map_data if hasattr(game_map, 'map_data') else game_map
        self.create_flames(current_time, map_data)

        # 通知游戏地图哪些格子被炸了
        for flame in self.flames:
            x, y = flame['pos']
            if 0 <= y < len(map_data) and 0 <= x < len(map_data[0]):
                if map_data[y][x] == 2:  # TILE_EXPLODABLE
                    if hasattr(self.game_map, 'destroy_tile'):
                        self.game_map.destroy_tile(x, y)

    def create_flames(self, current_time, game_map):
        """创建爆炸火焰效果"""
        # 确保处理的是map_data
        map_data = game_map.map_data if hasattr(game_map, 'map_data') else game_map

        center_x = self.rect.centerx // TILE_SIZE
        center_y = self.rect.centery // TILE_SIZE

        # 中心火焰
        self.flames.append({'pos': (center_x, center_y), 'time': current_time})

        # 四个方向的火焰
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in directions:
            for i in range(1, self.bomb_range):
                x, y = center_x + dx * i, center_y + dy * i

                # 检查是否超出地图边界
                if not (0 <= y < len(map_data) and 0 <= x < len(map_data[0])):
                    break

                # 添加火焰
                self.flames.append({'pos': (x, y), 'time': current_time})

                # 如果是固体墙则停止传播
                if map_data[y][x] == 1:  # TILE_SOLID
                    break

                # 如果是可爆炸墙则只传播到这里
                if map_data[y][x] == 2:  # TILE_EXPLODABLE
                    break

    def _get_pulse_color(self):
        """根据所有者返回脉冲颜色"""
        if self.owner.__class__.__name__ == "Player":
            if hasattr(self.owner, 'controls') and self.owner.controls["bomb"] == pygame.K_SPACE:
                # 玩家1：深蓝到浅蓝
                return 50, 50, int(150 + Bomb._current_pulse_factor * 100)
            else:
                # 玩家2：深红到橙红
                return int(150 + Bomb._current_pulse_factor * 100), 50, int(150 + Bomb._current_pulse_factor * 50)
        else:
            # 敌人：红色到橙色
            return 255, int(50 + Bomb._current_pulse_factor * 100), 50

    def draw(self, screen, offset=(0, 0)):
        if not self.exploded:
            # 1. 绘制炸弹本体
            screen.blit(self.animation.get_current_frame(),
                        (self.rect.x + offset[0], self.rect.y + offset[1]))

            # 2. 根据所有者设置颜色
            if self.owner.__class__.__name__ == "Player":
                # 玩家1或玩家2的炸弹
                if hasattr(self.owner, 'controls') and self.owner.controls["bomb"] == pygame.K_SPACE:
                    # 玩家1（默认WSAD+空格键控制）
                    r, g, b = self._get_pulse_color()
                else:
                    # 玩家2（默认方向键+回车键控制）
                    r, g, b = self._get_pulse_color()
            else:
                # 敌人的炸弹（保持原来的红色到橙色）
                r, g, b = self._get_pulse_color()

            alpha = int(30 + Bomb._current_pulse_factor * 20)
            scale = 0.9 + Bomb._current_pulse_factor * 0.2

            # 3. 调整共享Surface尺寸
            scaled_size = int(TILE_SIZE * scale)
            if Bomb._shared_hint_surface.get_size() != (scaled_size, scaled_size):
                Bomb._shared_hint_surface = pygame.Surface(
                    (scaled_size, scaled_size), pygame.SRCALPHA
                )

            # 4. 填充颜色
            Bomb._shared_hint_surface.fill((r, g, b, alpha))

            # 5. 绘制爆炸范围格子
            for x, y in self.explosion_range:
                draw_x = x * TILE_SIZE + offset[0] - (scaled_size - TILE_SIZE) // 2
                draw_y = y * TILE_SIZE + offset[1] - (scaled_size - TILE_SIZE) // 2
                screen.blit(Bomb._shared_hint_surface, (draw_x, draw_y))
                border_rect = pygame.Rect(
                    draw_x, draw_y, scaled_size, scaled_size
                )
                pygame.draw.rect(screen, (r, g, b, alpha + 70), border_rect, 1)
        else:
            # 原有火焰绘制逻辑
            for flame in self.flames:
                x, y = flame['pos']
                screen.blit(self.flame_animation.get_current_frame(),
                            (x * TILE_SIZE + offset[0], y * TILE_SIZE + offset[1]))

    def is_active(self):
        """检查炸弹或火焰是否还在活跃状态"""
        return not self.exploded or len(self.flames) > 0