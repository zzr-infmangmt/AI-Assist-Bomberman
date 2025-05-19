import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, MAP, TILE_SIZE,resource_path
from character import Player
from map import Map
from menu import Menu
from character import Enemy
import random
from bomb import Bomb
from character_factory import CharacterFactory

class Game:
    def __init__(self):
        self.bombs = None
        self.play_again_time = None
        self.show_play_again = None
        self.selected_mode = None
        self.victory_duration = None
        self.victory_max_scale = None
        self.victory_scale = None
        self.victory_text = None
        self.victory_time = None
        self.victory = None
        self.enemies = None
        self.players = None
        self.current_map = None
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bomberman")
        self.clock = pygame.time.Clock()
        self.running = True
        self.in_menu = True
        self.menu = Menu()
        self.reset_game_state()
        self.screen_shake = 0
        self.screen_shake_offset = [0, 0]

    def reset_game_state(self):
        self.current_map = None
        self.players = []
        self.enemies = []
        self.victory = False
        self.victory_time = 0
        self.victory_text = ""
        self.victory_scale = 0.1
        self.victory_max_scale = 1.0
        self.victory_duration = 3000
        self.selected_mode = None
        self.show_play_again = False
        self.play_again_time = 0

    def shake_screen(self, intensity):
        self.screen_shake = intensity

    def update_screen_shake(self):
        if self.screen_shake > 0:
            self.screen_shake_offset = [
                random.randint(-int(self.screen_shake), int(self.screen_shake)),
                random.randint(-int(self.screen_shake), int(self.screen_shake))
            ]
            self.screen_shake -= 0.5
        else:
            self.screen_shake_offset = [0, 0]

    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()
            self.clock.tick(FPS)

            if self.in_menu:
                result = self.handle_menu()
                if result:
                    if result["mode"] == "multi_player":
                        self.start_game(
                            result["mode"],
                            result["character"],
                            result.get("character2", "creep"),
                            result.get("map_index")
                        )
                    else:
                        self.start_game(
                            result["mode"],
                            result["character"],
                            map_index=result.get("map_index")
                        )
            else:
                if self.current_map is None or self.selected_mode is None:
                    self.reset_to_menu()
                    continue

                self.handle_events()
                self.update(current_time)
                self.draw(current_time)

        pygame.quit()

    def check_victory(self):
        """检查是否满足胜利条件"""
        if self.victory:
            return

        # 检查是否所有敌人都已死亡且死亡动画播放完毕
        enemies_dead = all(not enemy.alive and
                           (not enemy.death_animation or
                            not enemy.death_animation.is_playing())
                           for enemy in self.enemies)

        # 单人模式：消灭所有敌人且玩家存活
        if self.selected_mode == "single_player" and enemies_dead and self.players and self.players[0].alive:
            self.victory = True
            self.victory_time = pygame.time.get_ticks()
            self.victory_text = "VICTORY!"
            self.victory_duration = 1000
            self.victory_scale = 0.1
            self.victory_max_scale = 1.1

        # 双人模式：只剩一个玩家存活
        elif self.selected_mode == "multi_player":
            alive_players = [p for p in self.players if p.alive]
            if len(alive_players) == 1:
                self.victory = True
                self.victory_time = pygame.time.get_ticks()
                winner = alive_players[0]
                self.victory_text = f"PLAYER {self.players.index(winner) + 1} WINS!"
                self.victory_duration = 1000
                self.victory_scale = 0.1
                self.victory_max_scale = 1.1

    def check_defeat(self):
        """检查是否失败"""
        if self.selected_mode == "single_player" and not any(p.alive for p in self.players):
            self.victory = True
            self.victory_time = pygame.time.get_ticks()
            self.victory_text = "DEFEAT!"
            self.victory_duration = 1000
            self.victory_scale = 0.1
            self.victory_max_scale = 1.1

    def handle_menu(self):
        """处理菜单逻辑"""
        # 确保菜单状态正确
        if not hasattr(self.menu, 'back_button_rect') or self.menu.back_button_rect is None:
            self.menu._init_button_rects()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None

            result = self.menu.handle_events(event)
            if result:  # 如果有返回结果
                return result

        self.menu.update()
        self.menu.draw(self.screen)
        pygame.display.flip()
        return None

    def start_game(self, mode, character_p1, character_p2=None,map_index=None):
        self.bombs = []
        self.in_menu = False
        if map_index is not None and 0 <= map_index < len(MAP):
            map_data = MAP[map_index]
        else:
            map_data = random.choice(MAP)

        self.current_map = Map(map_data)
        self.players = []
        self.enemies = []
        self.selected_mode = mode

        # 创建玩家1 (两种模式通用)
        player1 = Player(
            character_type=character_p1,
            x=64, y=64,
            controls={
                "left": pygame.K_a,
                "right": pygame.K_d,
                "up": pygame.K_w,
                "down": pygame.K_s,
                "bomb": pygame.K_SPACE
            }
        )
        player1.game = self
        self.players.append(player1)

        if mode == "single_player":
            # 单人模式专属逻辑 - 使用选择的敌人类型和数量
            for _ in range(self.menu.selected_enemy_count):
                x, y = self._find_valid_spawn_position()
                enemy = Enemy(x, y, self, self.menu.selected_enemy_type)
                self.enemies.append(enemy)

        elif mode == "multi_player":
            # 确保character_p2不是None
            if character_p2 is None:
                character_p2 = "creep"  # 设置默认值

            # 双人模式专属逻辑
            player2 = Player(
                character_type=character_p2,
                x=SCREEN_WIDTH - 128, y=SCREEN_HEIGHT - 128,
                controls={
                    "left": pygame.K_LEFT,
                    "right": pygame.K_RIGHT,
                    "up": pygame.K_UP,
                    "down": pygame.K_DOWN,
                    "bomb": pygame.K_RETURN
                }
            )
            player2.game = self
            self.players.append(player2)

            available_enemies = [t for t in CharacterFactory._characters.keys() if
                                 t not in [character_p1, character_p2]]
            if len(available_enemies) >= 2:
                enemy_types = random.sample(available_enemies, 2)
            else:
                # 如果没有足够的独特类型，允许重复
                enemy_types = random.choices(available_enemies, k=2)

            for enemy_type in enemy_types:
                x, y = self._find_valid_spawn_position([player1, player2])
                self.enemies.append(Enemy(x, y, self, enemy_type))

    def _find_valid_spawn_position(self, avoid_positions=[]):
        """独立的生成位置查找方法"""
        while True:
            x = random.randint(2, 18) * TILE_SIZE
            y = random.randint(2, 8) * TILE_SIZE
            if (self.current_map.is_tile_passable(x // TILE_SIZE, y // TILE_SIZE) and
                    all((x, y) != (p.rect.x, p.rect.y) for p in avoid_positions)):
                return x, y

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and self.victory and self.show_play_again:
                if event.key == pygame.K_RETURN:
                    self.reset_to_menu()

            for player in self.players:
                bomb_pos = player.handle_events(event)
                if bomb_pos:
                    bomb = Bomb(bomb_pos[0], bomb_pos[1], player, bomb_pos[2], self.current_map)
                    player.bombs.append(bomb)

    def update(self, current_time):
        if self.current_map is None:
            return

        keys = pygame.key.get_pressed()

        # 如果处于胜利状态，只更新胜利动画
        if self.victory:
            elapsed = current_time - self.victory_time
            if elapsed >= self.victory_duration:
                self.show_play_again = True
                return

            # 更新缩放比例
            self.victory_scale = 0.1 + (self.victory_max_scale - 0.1) * min(elapsed / self.victory_duration, 1.5)
            return

        # 更新玩家
        # 检查玩家是否被火焰击中
        # 在update方法中，修改火焰碰撞检测部分
        for player in self.players[:]:
            if not player.alive:
                continue

            # 检查玩家是否被火焰击中（只检查非自己放置的炸弹的火焰）
            for other_player in self.players + self.enemies:
                # 如果是玩家自己，跳过检查自己的炸弹火焰
                if other_player == player:
                    continue

                for bomb in other_player.bombs:
                    for flame in bomb.flames:
                        flame_rect = pygame.Rect(
                            flame['pos'][0] * TILE_SIZE,
                            flame['pos'][1] * TILE_SIZE,
                            TILE_SIZE, TILE_SIZE
                        )
                        if player.rect.colliderect(flame_rect):
                            if player.take_damage():
                                self.screen_shake = 20
                                if not player.alive:
                                    self.check_defeat()
                            break
        # 更新敌人
        # 更新敌人
        for enemy in self.enemies:
            if not enemy.alive and enemy.death_animation and enemy.death_animation.is_playing():
                enemy.draw(self.screen, self.screen_shake_offset)
            elif enemy.alive:
                enemy.draw(self.screen, self.screen_shake_offset)

            # 检查敌人是否被火焰击中（只检查非自己放置的炸弹的火焰）
            for player in self.players:
                for bomb in player.bombs:
                    # 如果是敌人自己的炸弹，跳过检查
                    if bomb.owner == enemy:
                        continue

                    for flame in bomb.flames:
                        flame_rect = pygame.Rect(
                            flame['pos'][0] * TILE_SIZE,
                            flame['pos'][1] * TILE_SIZE,
                            TILE_SIZE, TILE_SIZE
                        )
                        if enemy.rect.colliderect(flame_rect):
                            enemy.die()
                            self.screen_shake = 10
                            break

        # 更新所有实体
        for player in self.players:
            player.update(keys, self.current_map.map_data)  # 传递 map_data 而不是 Map 对象
            super(Player, player).update()
            for bomb in player.bombs[:]:
                bomb.update(current_time, self.current_map.map_data)
                if not bomb.is_active():
                    player.bombs.remove(bomb)
            if player.is_hurt and player.hurt_animation:
                player.hurt_animation.update(current_time)
                if not player.hurt_animation.is_playing():
                    player.is_hurt = False
        for enemy in self.enemies:
            for bomb in enemy.bombs[:]:
                bomb.update(current_time, self.current_map.map_data)
                if not bomb.is_active():
                    enemy.bombs.remove(bomb)
        for enemy in self.enemies[:]:
            if not enemy.alive:
                if hasattr(enemy, 'death_animation') and enemy.death_animation:
                    enemy.death_animation.update(current_time)
                    if enemy.death_animation.loop_count > 0:
                        self.enemies.remove(enemy)
                else:
                    self.enemies.remove(enemy)
        # 检查胜利条件
        self.check_victory()
        self.current_map.update(self.players)
        self.update_screen_shake()

    def draw(self, current_time):
        if self.victory:
            # 绘制黑色背景
            self.screen.fill((0, 0, 0))

            elapsed = current_time - self.victory_time
            if elapsed <= self.victory_duration:
                # 绘制胜利文本
                font = pygame.font.Font(None, 72)
                text_surface = font.render(self.victory_text, True, (255, 215, 0))  # 金色文字

                # 计算缩放后的尺寸和位置
                orig_width = text_surface.get_width()
                orig_height = text_surface.get_height()
                new_width = int(orig_width * self.victory_scale)
                new_height = int(orig_height * self.victory_scale)

                # 缩放文本
                scaled_text = pygame.transform.scale(text_surface, (new_width, new_height))
                text_rect = scaled_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(scaled_text, text_rect)

            # 如果胜利动画结束，显示"PLAY AGAIN"提示
            if self.show_play_again:
                font = pygame.font.Font(None, 36)
                prompt_text = "PRESS ENTER TO PLAY AGAIN..."
                prompt_surface = font.render(prompt_text, True, (200, 200, 200))
                prompt_rect = prompt_surface.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
                self.screen.blit(prompt_surface, prompt_rect)

            pygame.display.flip()
            return

        if self.current_map is None:
            # 如果没有地图，直接返回，避免错误
            return

        self.screen.fill((0, 0, 0))
        self.current_map.draw(self.screen, self.screen_shake_offset)

        for player in self.players:
            for bomb in player.bombs:
                bomb.draw(self.screen, self.screen_shake_offset)

        for enemy in self.enemies:
            for bomb in enemy.bombs:
                bomb.draw(self.screen, self.screen_shake_offset)

        for player in self.players:
            if player.alive:
                player.draw(self.screen, self.screen_shake_offset)

        for player in self.players:
            if not player.alive and player.death_animation and player.death_animation.is_playing():
                player.draw(self.screen, self.screen_shake_offset)

        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(self.screen, self.screen_shake_offset)
            elif enemy.death_animation and enemy.death_animation.is_playing():
                enemy.draw(self.screen, self.screen_shake_offset)
            enemy.update(self.current_map)
        for i, player in enumerate(self.players):
            if player.alive:
                # 绘制生命值图标
                heart_img = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(heart_img, (255, 0, 0), (10, 10), 10)
                for h in range(player.health):
                    self.screen.blit(heart_img, (10 + h * 25, 10 + i * 30))
        pygame.display.flip()

    def reset_to_menu(self):
        """重置游戏状态返回菜单"""
        self.in_menu = True
        self.victory = False
        self.victory_text = ""
        self.victory_scale = 0.1
        self.players = []
        self.enemies = []
        self.bombs = []
        self.current_map = None
        self.show_play_again = False
        self.menu.reset()