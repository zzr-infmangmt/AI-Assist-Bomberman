from animations import Animation, AnimationController, Direction
import glob
from character_factory import CharacterFactory  # 现在这个导入是安全的
import random
import pygame
from constants import TILE_SIZE,TILE_EMPTY,resource_path
import math
from bomb import Bomb
class Character:
    def __init__(self, name, base_path, speed=4, max_bombs=4, bomb_range=2):
        self.name = name
        self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        self.speed = speed
        self.is_flipped = False
        self.direction = Direction.FRONT
        self.bombs = []
        self.max_bombs = max_bombs
        self.bomb_range = bomb_range
        self.bomb_cooldown = 300
        self.last_bomb_time = 0
        self.anim_controller = AnimationController()
        self.max_health = 5  # 最大生命值
        self.health = self.max_health  # 当前生命值
        self.alive = True
        self.death_animation = None
        self.hit_cooldown = 0  # 受伤冷却时间
        self.load_animations(base_path)
        self.load_death_animation(base_path)
        self.image = self.anim_controller.animations["idle_front"].frames[0]
        self.hurt_animation = None
        self.load_hurt_animation(base_path)
        self.is_hurt = False

    def take_damage(self):
        """受到伤害"""
        if self.hit_cooldown <= 0:
            self.health -= 1
            self.hit_cooldown = 90  # 重置冷却时间（假设60FPS，即1秒冷却）
            self.is_hurt = True  # 添加这一行
            if self.hurt_animation:
                self.hurt_animation.current_frame = 0
                self.hurt_animation.loop_count = 0
                self.hurt_animation.last_update = pygame.time.get_ticks()
            if self.health <= 0:
                self.die()
            return True  # 表示成功受到伤害
        return False  # 表示当前处于无敌状态

    def load_death_animation(self, base_path):
        try:
            death_frames = sorted(glob.glob(resource_path(f"{base_path.rstrip('/')}/Death/*.png")))
            if not death_frames:
                print(f"警告：未找到死亡动画资源！路径: {base_path}/Death/")
            else:
                self.death_animation = Animation(death_frames, interval=200, repeat=0)
        except Exception as e:
            print(f"加载死亡动画失败: {e}")
        finally:
            pass

    def load_hurt_animation(self, base_path):
        try:
            hurt_frames = sorted(glob.glob(resource_path(f"{base_path.rstrip('/')}/Hurt/*.png")))
            if not hurt_frames:
                print(f"❌ 受伤动画资源未找到！路径: {base_path}/Hurt/")
            else:
                self.hurt_animation = Animation(hurt_frames, interval=100, repeat=2)
        except Exception as e:
            print(f"❌ 加载受伤动画失败: {e}")
    def die(self):
        """角色死亡"""
        self.alive = False
        if self.death_animation:
            self.death_animation.current_frame = 0
            self.death_animation.loop_count = 0
            self.death_animation.last_update = pygame.time.get_ticks()

    def is_dying(self):
        """检查是否正在播放死亡动画"""
        return (not self.alive and
                hasattr(self, 'death_animation') and
                self.death_animation and
                self.death_animation.loop_count == 0)  # 只播放一次

    def load_animations(self, base_path):
        base_path = resource_path(base_path.rstrip('/') + '/')
        animations = {
            "idle_front": f"{base_path}Front/*.png",
            "idle_back": f"{base_path}Back/*.png",
            "idle_side": f"{base_path}Side/*.png",
            "walk_front": f"{base_path}Front/*.png",
            "walk_back": f"{base_path}Back/*.png",
            "walk_left": (f"{base_path}Side/*.png", True, False),
            "walk_right": (f"{base_path}Side/*.png", False, False)
        }

        for name, params in animations.items():
            if isinstance(params, str):
                self._load_animation_set(name, resource_path(params))
            else:
                self._load_animation_set(name, resource_path(params[0]), params[1], params[2])

    def _load_animation_set(self, anim_name, pattern, flip_x=False, flip_y=False):
        try:
            files = sorted(glob.glob(pattern))
            if not files:
                print(f"❌ 动画资源未找到: {pattern}")
                # 创建默认帧避免崩溃
                default_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                default_surface.fill((255, 0, 255))  # 品红色便于识别缺失资源
                self.anim_controller.add(anim_name, Animation([default_surface]))
                return

            print(f"✅ 加载动画 {anim_name}: {len(files)}帧")  # 调试用
            self.anim_controller.add(anim_name, Animation(files, interval=100, flip_x=flip_x, flip_y=flip_y))
        except Exception as e:
            print(f"❌ 加载动画 {anim_name} 失败: {e}")
            # 创建默认帧避免崩溃
            default_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            default_surface.fill((255, 0, 255))
            self.anim_controller.add(anim_name, Animation([default_surface]))

    def update_animation(self, moving):
        """更新角色动画状态"""
        if moving:
            if self.direction == Direction.FRONT:
                self.anim_controller.play("walk_front")
            elif self.direction == Direction.BACK:
                self.anim_controller.play("walk_back")
            elif self.direction == Direction.SIDE:
                self.anim_controller.play("walk_left" if self.is_flipped else "walk_right")
        else:
            if self.direction == Direction.FRONT:
                self.anim_controller.play("idle_front")
            elif self.direction == Direction.BACK:
                self.anim_controller.play("idle_back")
            elif self.direction == Direction.SIDE:
                self.anim_controller.play("idle_side")

        self.anim_controller.update(pygame.time.get_ticks())
        self.image = self.anim_controller.get_current_frame()

    def can_move(self, rect, game_map):
        """检查角色是否可以移动到指定位置"""
        # 计算角色中心点
        center_x = rect.centerx // TILE_SIZE
        center_y = rect.centery // TILE_SIZE

        # 计算角色占据的格子范围(使用比例)
        margin = 0.1  # 碰撞边缘缓冲区
        left = (rect.left + rect.width * margin) // TILE_SIZE
        right = (rect.right - rect.width * margin) // TILE_SIZE
        top = (rect.top + rect.height * margin) // TILE_SIZE
        bottom = (rect.bottom - rect.height * margin) // TILE_SIZE

        # 检查相关格子是否可通行
        check_points = [
            (center_x, center_y),  # 中心点
            (left, top),  # 左上
            (right, top),  # 右上
            (left, bottom),  # 左下
            (right, bottom),  # 右下
        ]

        # 处理 game_map 是 Map 对象或 map_data 列表的情况
        map_data = game_map.map_data if hasattr(game_map, 'map_data') else game_map

        for x, y in check_points:
            # 边界检查
            if not (0 <= y < len(map_data) and 0 <= x < len(map_data[0])):
                return False
            # 碰撞检查
            if map_data[int(y)][int(x)] != TILE_EMPTY:
                return False

        return True

    def place_bomb(self):
        """放置炸弹"""
        current_time = pygame.time.get_ticks()
        if len(self.bombs) < self.max_bombs and current_time - self.last_bomb_time > self.bomb_cooldown:
            bomb_x = (self.rect.centerx // TILE_SIZE) * TILE_SIZE
            bomb_y = (self.rect.centery // TILE_SIZE) * TILE_SIZE

            # 检查该位置是否已经有炸弹
            for bomb in self.bombs:
                if bomb.rect.x == bomb_x and bomb.rect.y == bomb_y:
                    return None

            self.last_bomb_time = current_time
            return bomb_x, bomb_y, self.bomb_range  # 确保返回三个值的元组
        return None

    def draw(self, screen, offset=(0, 0)):
        if not self.alive:
            if self.death_animation and self.death_animation.is_playing():
                # 获取当前死亡帧
                death_frame = self.death_animation.get_current_frame()

                # 创建发光效果
                glow_surface = pygame.Surface(death_frame.get_size(), pygame.SRCALPHA)
                glow_surface.blit(death_frame, (0, 0))
                glow_surface.fill((255, 100, 0, 80), special_flags=pygame.BLEND_ADD)

                # 放大效果
                scaled_size = (
                    int(death_frame.get_width() * 1.3 * (1 + 0.2 * math.sin(pygame.time.get_ticks() / 100))),
                    int(death_frame.get_height() * 1.3 * (1 + 0.2 * math.sin(pygame.time.get_ticks() / 100)))
                )
                scaled_frame = pygame.transform.scale(death_frame, scaled_size)

                # 绘制位置（考虑屏幕震动偏移）
                draw_pos = (
                    self.rect.x - (scaled_size[0] - self.rect.w) // 2 + offset[0],
                    self.rect.y - (scaled_size[1] - self.rect.h) // 2 + offset[1]
                )

                # 绘制效果
                screen.blit(scaled_frame, draw_pos)
                screen.blit(glow_surface, (self.rect.x + offset[0], self.rect.y + offset[1]))
                return

        # 正常绘制活着的角色
        if self.is_hurt and self.hurt_animation:
            hurt_frame = self.hurt_animation.get_current_frame()
            screen.blit(hurt_frame, (self.rect.x + offset[0], self.rect.y + offset[1]))
        else:
            # 正常绘制角色
            screen.blit(self.image, (self.rect.x + offset[0], self.rect.y + offset[1]))

    def update(self, *args):
        """更新角色状态"""
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        # 更新受伤动画（如果正在播放）
        if self.is_hurt and self.hurt_animation:
            self.hurt_animation.update(pygame.time.get_ticks())
            if not self.hurt_animation.is_playing():
                self.is_hurt = False  # 动画播放完毕
        if not self.alive and self.death_animation:
            self.death_animation.update(pygame.time.get_ticks())
            if not self.death_animation.is_playing():
                # 死亡动画播放完毕
                pass

    def _draw_death_particles(self, screen):
        if not hasattr(self, 'death_particles'):
            # Create particles when death starts
            self.death_particles = []
            for _ in range(15):  # Number of particles
                self.death_particles.append({
                    'pos': [self.rect.centerx, self.rect.centery],
                    'vel': [random.uniform(-3, 3), random.uniform(-3, 3)],
                    'color': (random.randint(200, 255), random.randint(0, 100), 0),
                    'size': random.randint(2, 6),
                    'life': random.randint(20, 40)
                })

        # Update and draw particles
        for p in self.death_particles[:]:
            pygame.draw.circle(screen, p['color'],
                               (int(p['pos'][0]), int(p['pos'][1])),
                               p['size'])
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['life'] -= 1
            if p['life'] <= 0:
                self.death_particles.remove(p)
class Enemy(Character):
    """基础AI敌人，随机移动"""

    def __init__(self, x, y, game,enemy_type="bomberman"):
        # 使用CharacterFactory的creep配置
        config = CharacterFactory._characters[enemy_type]
        super().__init__(
            name=config["name"],
            base_path=config["base_path"],
            speed=config["speed"],
            max_bombs=2,
            bomb_range=config["bomb_range"]
        )
        self.rect.x = x
        self.rect.y = y
        self.move_timer = 0
        self.bomb_timer = 0  # 炸弹放置计时器
        self.current_direction = (0, 0)
        self.game = game
        self.enemy_type = enemy_type
    def update(self, game_map):
        """每帧更新移动和炸弹放置"""
        if not self.alive:
            if self.death_animation:
                self.death_animation.update(pygame.time.get_ticks())
            return

        # 更新移动
        self.move_timer -= 1
        if self.move_timer <= 0:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            self.current_direction = random.choice(directions)
            self.move_timer = 60

        dx, dy = self.current_direction
        new_rect = self.rect.move(dx * self.speed, dy * self.speed)
        if self.can_move(new_rect, game_map):
            self.rect = new_rect

        # 随机放置炸弹
        self.bomb_timer -= 1
        if self.bomb_timer <= 0 and len(self.bombs) < self.max_bombs:
            if random.random() < 0.005:  # 0.5%的几率放置炸弹
                bomb_pos = self.place_bomb()
                if bomb_pos:
                    bomb = Bomb(bomb_pos[0], bomb_pos[1], self, bomb_pos[2], self.game.current_map)
                    self.bombs.append(bomb)
                    self.game.bombs.append(bomb)  # 确保添加到全局炸弹列表
                    self.bomb_timer = random.randint(30, 90)

        # 更新动画
        self.update_animation(moving=(dx != 0 or dy != 0))

        # 更新炸弹状态
        current_time = pygame.time.get_ticks()
        self.bombs = [bomb for bomb in self.bombs if bomb.is_active()]
        for bomb in self.bombs:
            bomb.update(current_time, game_map.map_data if hasattr(game_map, 'map_data') else game_map)

class Player(Character):
    def __init__(self, character_type, x, y, controls):
        config = CharacterFactory._characters[character_type]
        super().__init__(
            name=config["name"],
            base_path=config["base_path"],
            speed=config["speed"],
            max_bombs=config["max_bombs"],
            bomb_range=config["bomb_range"]
        )
        self.rect.update(x, y, TILE_SIZE, TILE_SIZE)
        self.controls = controls

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == self.controls["bomb"]:
            return self.place_bomb()
        return None

    def update(self, keys, game_map):
        super().update()
        dx, dy = 0, 0
        moving = False

        # 使用位运算优化方向判断
        if keys[self.controls["left"]]:
            dx -= self.speed
            self.direction = Direction.SIDE
            self.is_flipped = True
            moving = True
        if keys[self.controls["right"]]:
            dx += self.speed
            self.direction = Direction.SIDE
            self.is_flipped = False
            moving = True
        if keys[self.controls["up"]]:
            dy -= self.speed
            self.direction = Direction.BACK
            moving = True
        if keys[self.controls["down"]]:
            dy += self.speed
            self.direction = Direction.FRONT
            moving = True

        self.update_animation(moving)

        # 合并移动检测
        if dx != 0 or dy != 0:
            new_rect = self.rect.copy()
            if dx != 0 and self.can_move(new_rect.move(dx, 0), game_map):
                self.rect.x += dx
            if dy != 0 and self.can_move(new_rect.move(0, dy), game_map):
                self.rect.y += dy

        # 使用列表推导式优化炸弹更新
        current_time = pygame.time.get_ticks()
        self.bombs = [bomb for bomb in self.bombs if bomb.is_active()]
        for bomb in self.bombs:
            bomb.update(current_time, game_map)