import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_NAMES,resource_path
from character_factory import CharacterFactory

class Menu:
    def __init__(self):
        self.selected_map = None
        self.map_selecting = None
        self.background =  self._load_image("assets/pictures/Menu/game_back.png")
        self.title = self._load_image("assets/pictures/Menu/title_titletext.png", True)

        self.buttons = {
            "one_player": {
                "normal": self._load_image("assets/pictures/Menu/One_Player_Normal.png", True),
                "hover": self._load_image("assets/pictures/Menu/One_Player_Hover.png", True)
            },
            "two_player": {
                "normal": self._load_image("assets/pictures/Menu/Two_Players_Normal.png", True),
                "hover": self._load_image("assets/pictures/Menu/Two_Players_Hover.png", True)
            },
            "back": {
                "normal": self._load_image("assets/pictures/Menu/Back_Normal.png", True),
                "hover": self._load_image("assets/pictures/Menu/Back_Hover.png", True)
            }
        }

        self._init_button_rects()
        self.character_selection = False
        self.selected_character = "bomberman"  # 默认选择bomberman
        self.character_options = CharacterFactory.get_available_characters()
        self.character_previews = self.load_character_previews()
        self.selected_mode = None
        self.back_button_rect = None
        self.character_focus_index = 0  # 当前键盘聚焦的角色索引
        self.last_key_time = 0  # 记录最后一次按键时间（用于防抖）
        self.key_delay = 200  # 按键延迟(毫秒)
        self.current_time = 0  # 当前时间
        self.one_player_hovered = False
        self.two_player_hovered = False
        self.back_hovered = False
        self.selected_character2 = "creep"  # 默认第二个角色
        self.character_focus_index2 = 0    # 玩家2当前聚焦的角色索引
        self.single_player_selecting = False  # 单人模式选择状态
        self.multi_player_selecting = False   # 双人模式选择状态
        self.selected_character_p1 = "bomberman"  # 更明确的变量名
        self.selected_character_p2 = "creep"      # 玩家2选择
        self.character_thumb_size = (50, 50)  # Size of small previews
        self.character_large_size = (200, 200)  # Size of big preview
        self.character_thumb_margin = 10  # Margin between thumbnails
        self.focused_character = 0  # Currently focused character index
        self.focused_character_p2 = 0  # For player 2 in multiplayer

        # Load both thumbnail and large preview images
        self.character_thumbnails = {}
        self.character_large_previews = {}
        for char_type in self.character_options:
            img = self._load_image(f"assets/pictures/Menu/characters/{char_type}_preview.png", True)
            self.character_thumbnails[char_type] = pygame.transform.scale(img, self.character_thumb_size)
            self.character_large_previews[char_type] = pygame.transform.scale(img, self.character_large_size)
        self.map_thumb_size = (300, 150)  # 缩略图尺寸
        self.map_thumbnails = self._load_map_thumbnails()
        self.enemy_selection = False  # 是否在敌人选择界面
        # 从CharacterFactory获取所有角色类型，排除玩家角色"bomberman"
        self.enemy_types = [char_type for char_type in CharacterFactory.get_available_characters()
                            if char_type != "bomberman"]
        self.selected_enemy_type = self.enemy_types[0] if self.enemy_types else "bomberman"  # 默认第一个敌人类型
        self.enemy_count_options = [1, 2, 3, 4, 5, 6]  # 可选的敌人数量
        self.selected_enemy_count = 2  # 默认敌人数量
        self.selecting_enemy_type = True  # 当前是在选择敌人类型还是数量
        self.enemy_type_focus = 0  # 当前聚焦的敌人类型索引
        self.enemy_count_focus = 1  # 当前聚焦的敌人数量索引(默认选择2个)
    def _load_image(self, path, alpha=False):
        try:
            # 使用resource_path函数获取正确的路径
            full_path = resource_path(path)
            return pygame.image.load(full_path).convert_alpha() if alpha else pygame.image.load(full_path).convert()
        except pygame.error as e:
            print(f"Failed to load image: {path}. Error: {e}")
            return pygame.Surface((1, 1), pygame.SRCALPHA if alpha else 0)
    def _init_button_rects(self):
        """Initialize button rectangles and hover states"""
        # Main menu buttons
        self.one_player_btn = self.buttons["one_player"]["normal"]
        self.one_player_btn_hover = self.buttons["one_player"]["hover"]
        self.two_player_btn = self.buttons["two_player"]["normal"]
        self.two_player_btn_hover = self.buttons["two_player"]["hover"]
        self.back_btn = self.buttons["back"]["normal"]
        self.back_btn_hover = self.buttons["back"]["hover"]

        # Position buttons
        self.title_rect = self.title.get_rect(centerx=SCREEN_WIDTH // 2, top=30)
        self.one_player_rect = self.one_player_btn.get_rect(
            centerx=SCREEN_WIDTH // 2,
            centery=SCREEN_HEIGHT // 2
        )
        self.two_player_rect = self.two_player_btn.get_rect(
            centerx=SCREEN_WIDTH // 2,
            centery=SCREEN_HEIGHT // 2 + 100
        )

        # Updated Back button position - centered at bottom with some margin
        self.back_button_rect = self.back_btn.get_rect(
            centerx=SCREEN_WIDTH // 2,
            bottom=SCREEN_HEIGHT - 20  # 20 pixels from bottom
        )

        # Initialize hover states
        self.one_player_hovered = False
        self.two_player_hovered = False
        self.back_hovered = False

    def _load_map_thumbnails(self):
        """加载所有地图缩略图，并为随机地图创建动态切换效果"""
        global path
        thumbnails = {}

        # 1. 加载所有常规地图的缩略图
        for i, name in enumerate(MAP_NAMES):
            try:
                path = f"assets/pictures/Menu/maps/MAP_{i + 1}_preview.png"
                img = self._load_image(path, alpha=True)  # 使用_load_image方法
                thumbnails[name] = pygame.transform.scale(img, self.map_thumb_size)
            except Exception as e:
                print(f"Failed to load map thumbnail: {path}. Error: {e}")
                # 创建占位图像
                thumbnails[name] = pygame.Surface(self.map_thumb_size, pygame.SRCALPHA)
                thumbnails[name].fill((50, 50, 50))
                font = pygame.font.Font(None, 24)
                text = font.render(name, True, (255, 255, 255))
                thumbnails[name].blit(text, (10, 10))

        # 2. 为随机地图创建特殊缩略图
        # 存储所有地图的缩略图用于轮播
        self.random_map_thumbs = list(thumbnails.values())
        self.current_random_thumb_index = 0
        self.last_thumb_switch_time = 0
        self.thumb_switch_interval = 100  # 100ms切换一次

        # 初始随机地图缩略图
        thumbnails["RANDOM"] = self.random_map_thumbs[0]

        return thumbnails

    def load_character_previews(self):
        """加载角色预览图"""
        previews = {}
        for char_type in self.character_options:
            previews[char_type] = self._load_image(
                f"assets/pictures/Menu/characters/{char_type}_preview.png",
                alpha=True
            )
        return previews

    def _draw_single_player_selection(self, screen):
        """Improved single player character selection"""
        screen.blit(self.background, (0, 0))

        # Draw back button
        back_img = self.back_btn_hover if self.back_hovered else self.back_btn
        screen.blit(back_img, self.back_button_rect)

        # Draw title
        title = pygame.font.Font(None, 48).render("SELECT YOUR CHARACTER", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Draw thumbnails on left side
        thumb_x = 50
        thumb_y = 100

        for i, char_type in enumerate(self.character_options):
            thumb = self.character_thumbnails[char_type]
            rect = thumb.get_rect(topleft=(thumb_x, thumb_y))

            # Highlight focused character
            if i == self.focused_character:
                pygame.draw.rect(screen, (0, 255, 255), rect.inflate(10, 10), 2)

            screen.blit(thumb, rect)
            thumb_y += self.character_thumb_size[1] + self.character_thumb_margin

        # Draw large preview in center
        current_char = self.character_options[self.focused_character]
        large_preview = self.character_large_previews[current_char]
        screen.blit(large_preview, (SCREEN_WIDTH // 2 - self.character_large_size[0] // 2, 150))

        # Draw character info below preview
        info_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - 100,  # x位置
            300,  # y位置 (在大图下方)
            200, 100  # 宽度和高度
        )
        self._draw_character_info(screen, current_char, info_rect)

    def _draw_multi_player_selection(self, screen):
        """Improved two player character selection"""
        screen.blit(self.background, (0, 0))

        # Draw back button
        back_img = self.back_btn_hover if self.back_hovered else self.back_btn
        screen.blit(back_img, self.back_button_rect)

        # Draw title
        title = pygame.font.Font(None, 48).render("SELECT CHARACTERS", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Player 1 selection
        self._draw_player_selection(screen, "PLAYER 1", self.focused_character, 1)

        # Player 2 selection
        self._draw_player_selection(screen, "PLAYER 2", self.focused_character_p2, 2)

    def _draw_player_selection(self, screen, player_label, focused_index, player_num):
        """Helper method to draw player selection UI"""
        # Draw player label
        color = (0, 255, 255) if player_num == 1 else (255, 0, 0)
        label = pygame.font.Font(None, 36).render(player_label, True, color)
        screen.blit(label, (50 if player_num == 1 else SCREEN_WIDTH - 150, 100))

        # Draw thumbnails
        thumb_x = 50 if player_num == 1 else SCREEN_WIDTH - 100
        thumb_y = 150

        for i, char_type in enumerate(self.character_options):
            thumb = self.character_thumbnails[char_type]
            rect = thumb.get_rect(topleft=(thumb_x, thumb_y))

            # Highlight focused character
            if i == (self.focused_character if player_num == 1 else self.focused_character_p2):
                pygame.draw.rect(screen, color, rect.inflate(10, 10), 2)

            screen.blit(thumb, rect)
            thumb_y += self.character_thumb_size[1] + self.character_thumb_margin

        # Draw large preview in center for focused player
        if (player_num == 1 and self.focused_character == focused_index) or \
                (player_num == 2 and self.focused_character_p2 == focused_index):
            current_char = self.character_options[focused_index]
            large_preview = self.character_large_previews[current_char]
            preview_x = SCREEN_WIDTH // 4 if player_num == 1 else 3 * SCREEN_WIDTH // 4
            screen.blit(large_preview, (preview_x - self.character_large_size[0] // 2, 200))

            # Draw character info
            info_rect = pygame.Rect(
                preview_x - 100,  # x位置 (居中)
                300,  # y位置 (在大图下方)
                200, 100  # 宽度和高度
            )
            self._draw_character_info(screen, current_char, info_rect)

    def _draw_enemy_selection(self, screen):
        """绘制敌人选择界面 - 优化后的版本"""
        screen.blit(self.background, (0, 0))

        # 绘制标题
        title = pygame.font.Font(None, 48).render("ENEMY SELECTION", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # 绘制返回按钮
        back_img = self.back_btn_hover if self.back_hovered else self.back_btn
        screen.blit(back_img, self.back_button_rect)

        # 绘制选择步骤指示器
        step_text = pygame.font.Font(None, 32).render(
            "STEP 1: SELECT ENEMY TYPE" if self.selecting_enemy_type else "STEP 2: SELECT ENEMY COUNT",
            True, (200, 200, 255))
        screen.blit(step_text, (SCREEN_WIDTH // 2 - step_text.get_width() // 2, 80))

        if self.selecting_enemy_type:
            # 绘制敌人类型选择 - 使用卡片式布局
            type_title = pygame.font.Font(None, 36).render("ENEMY TYPE", True, (255, 255, 255))
            screen.blit(type_title, (SCREEN_WIDTH // 2 - type_title.get_width() // 2, 120))

            # 计算卡片布局参数
            card_width = 200
            card_height = 300
            margin = 20
            start_x = (SCREEN_WIDTH - (len(self.enemy_types) * (card_width + margin))) // 2

            for i, enemy_type in enumerate(self.enemy_types):
                # 卡片背景
                card_rect = pygame.Rect(start_x + i * (card_width + margin), 150, card_width, card_height)
                color = (50, 50, 80) if i != self.enemy_type_focus else (80, 80, 120)
                pygame.draw.rect(screen, color, card_rect, border_radius=10)
                pygame.draw.rect(screen, (0, 255, 255) if i == self.enemy_type_focus else (100, 100, 100),
                                 card_rect, 2, border_radius=10)

                # 敌人预览图
                preview = self.character_thumbnails[enemy_type]
                scaled_preview = pygame.transform.scale(preview, (150, 150))
                screen.blit(scaled_preview, (card_rect.centerx - 75, card_rect.y + 10))

                # 敌人名称
                name_text = pygame.font.Font(None, 28).render(enemy_type.upper(), True, (255, 255, 255))
                screen.blit(name_text, (card_rect.centerx - name_text.get_width() // 2, card_rect.y + 170))

                # 敌人属性
                stats = CharacterFactory._characters[enemy_type]
                attr_text = [
                    f"Speed: {stats['speed']}",
                    f"Bombs: {stats['max_bombs']}",
                    f"Range: {stats['bomb_range']}"
                ]

                for j, text in enumerate(attr_text):
                    text_surface = pygame.font.Font(None, 24).render(text, True, (200, 200, 200))
                    screen.blit(text_surface, (card_rect.centerx - text_surface.get_width() // 2,
                                               card_rect.y + 190 + j * 25+10))
        else:
            count_title = pygame.font.Font(None, 36).render("ENEMY COUNT", True, (255, 255, 255))
            screen.blit(count_title, (SCREEN_WIDTH // 2 - count_title.get_width() // 2, 120))

            # 计算按钮布局
            btn_width = 100
            btn_height = 60
            margin = 20
            total_width = len(self.enemy_count_options) * btn_width + (len(self.enemy_count_options) - 1) * margin
            start_x = (SCREEN_WIDTH - total_width) // 2

            for i, count in enumerate(self.enemy_count_options):
                # 按钮背景
                btn_rect = pygame.Rect(start_x + i * (btn_width + margin), 170, btn_width, btn_height)
                color = (80, 120, 80) if i == self.enemy_count_focus else (50, 80, 50)
                pygame.draw.rect(screen, color, btn_rect, border_radius=5)
                pygame.draw.rect(screen, (0, 255, 0) if i == self.enemy_count_focus else (100, 150, 100),
                                 btn_rect, 2, border_radius=5)

                # 数量文本
                count_text = pygame.font.Font(None, 36).render(str(count), True, (255, 255, 255))
                screen.blit(count_text, (btn_rect.centerx - count_text.get_width() // 2,
                                         btn_rect.centery - count_text.get_height() // 2))

    def _draw_character_info(self, screen, char_type, rect, player=None):
        """绘制角色信息 - 调整位置版本"""
        font = pygame.font.Font(None, 28)
        stats = CharacterFactory._characters[char_type]

        # 信息内容
        info = [
            f"Speed: {stats['speed']}",
            f"Bombs Counts: {stats['max_bombs']}",
            f"Explosion Range: {stats['bomb_range']}"
        ]

        # 计算信息框位置 (基于传入的rect调整)
        info_x = rect.centerx - 100  # 宽度200px，居中
        info_y = rect.bottom + 20  # 在图像下方20px

        # 绘制半透明背景
        info_bg = pygame.Surface((200, 100), pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 180))  # 半透明黑色背景
        screen.blit(info_bg, (info_x, info_y))

        # 绘制每条信息
        for i, text in enumerate(info):
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                centerx=rect.centerx,
                top=info_y + 10 + i * 30  # 10px顶部内边距，每行间隔30px
            )
            screen.blit(text_surface, text_rect)

    def _draw_map_selection(self, screen):
        """绘制地图选择界面"""
        screen.blit(self.background, (0, 0))

        # 绘制标题
        title = pygame.font.Font(None, 48).render("SELECT MAP", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # 绘制返回按钮
        back_img = self.back_btn_hover if self.back_hovered else self.back_btn
        screen.blit(back_img, self.back_button_rect)

        # 绘制当前选择的地图缩略图 (左侧)
        thumb_x = 50
        thumb_y = 100
        current_map_name = "RANDOM" if self.selected_map == len(MAP_NAMES) else MAP_NAMES[self.selected_map]
        screen.blit(self.map_thumbnails[current_map_name], (thumb_x, thumb_y))

        # 绘制地图列表 (右侧)
        list_x = 400
        list_y = 100
        list_item_height = 40
        font = pygame.font.Font(None, 35)

        for i, name in enumerate(MAP_NAMES):
            color = (0, 255, 255) if i == self.selected_map else (200, 200, 200)
            item = font.render(name, True, color)
            screen.blit(item, (list_x, list_y + i * list_item_height))

        # 绘制随机选项
        random_y = list_y + len(MAP_NAMES) * list_item_height + 20
        color = (0, 255, 255) if self.selected_map == len(MAP_NAMES) else (200, 200, 200)
        random_text = font.render("RANDOM MAP", True, color)
        screen.blit(random_text, (list_x, random_y))

    def handle_events(self, event):
        """处理所有菜单事件，包括主菜单、角色选择和地图选择"""
        self.current_time = pygame.time.get_ticks()

        # 公共返回按钮处理（所有界面通用）
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, 'back_button_rect') and self.back_button_rect.collidepoint(event.pos):
                self.reset()
                return None
        if hasattr(self, 'enemy_selection') and self.enemy_selection:
            if event.type == pygame.KEYDOWN and self.current_time - self.last_key_time > self.key_delay:
                self.last_key_time = self.current_time
                if event.key == pygame.K_ESCAPE:
                    if self.selecting_enemy_type:
                        self.enemy_selection = False
                        self.single_player_selecting = True
                    else:
                        self.selecting_enemy_type = True
                    return None
                elif event.key == pygame.K_RETURN:
                    if self.selecting_enemy_type:
                        self.selecting_enemy_type = False
                        self.selected_enemy_type = self.enemy_types[self.enemy_type_focus]
                    else:
                        self.selected_enemy_count = self.enemy_count_options[self.enemy_count_focus]
                        self.enemy_selection = False
                        self.map_selecting = True
                        self.selected_map = 0
                    return None
                elif event.key == pygame.K_a:
                    if self.selecting_enemy_type:
                        self.enemy_type_focus = (self.enemy_type_focus - 1) % len(self.enemy_types)
                    else:
                        self.enemy_count_focus = (self.enemy_count_focus - 1) % len(self.enemy_count_options)
                elif event.key == pygame.K_d:
                    if self.selecting_enemy_type:
                        self.enemy_type_focus = (self.enemy_type_focus + 1) % len(self.enemy_types)
                    else:
                        self.enemy_count_focus = (self.enemy_count_focus + 1) % len(self.enemy_count_options)

        # 地图选择界面事件处理
        elif hasattr(self, 'map_selecting') and self.map_selecting:
            if event.type == pygame.KEYDOWN and self.current_time - self.last_key_time > self.key_delay:
                self.last_key_time = self.current_time
                if event.key == pygame.K_w:  # 上移选择
                    self.selected_map = (self.selected_map - 1) % (len(MAP_NAMES) + 1)  # +1 for random option
                elif event.key == pygame.K_s:  # 下移选择
                    self.selected_map = (self.selected_map + 1) % (len(MAP_NAMES) + 1)
                elif event.key == pygame.K_RETURN:  # 确认选择
                    return {
                        "mode": self.selected_mode,
                        "character": self.selected_character_p1,
                        "character2": getattr(self, 'selected_character_p2', None),
                        "map_index": self.selected_map if self.selected_map < len(MAP_NAMES) else None
                    }
                elif event.key == pygame.K_ESCAPE:  # 返回角色选择
                    self.map_selecting = False
                    return None

            # 鼠标选择地图
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                list_x = 400
                list_y = 100
                list_item_height = 40

                # 检查地图列表点击
                for i in range(len(MAP_NAMES) + 1):  # +1 for random option
                    item_rect = pygame.Rect(list_x, list_y + i * list_item_height, 200, list_item_height)
                    if i == len(MAP_NAMES):  # Random option
                        item_rect = pygame.Rect(list_x, list_y + i * list_item_height + 20, 200, list_item_height)

                    if item_rect.collidepoint(event.pos):
                        self.selected_map = i
                        break

                # 检查开始按钮点击
                start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70, 200, 40)
                if start_btn.collidepoint(event.pos):
                    return {
                        "mode": self.selected_mode,
                        "character": self.selected_character_p1,
                        "character2": getattr(self, 'selected_character_p2', None),
                        "map_index": self.selected_map if self.selected_map < len(MAP_NAMES) else None
                    }

        # 主菜单界面事件
        elif not (self.single_player_selecting or self.multi_player_selecting):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.one_player_rect.collidepoint(event.pos):
                    self.single_player_selecting = True
                    self.selected_mode = "single_player"
                    return None
                elif self.two_player_rect.collidepoint(event.pos):
                    self.multi_player_selecting = True
                    self.selected_mode = "multi_player"
                    return None

            elif event.type == pygame.KEYDOWN and self.current_time - self.last_key_time > self.key_delay:
                self.last_key_time = self.current_time
                if event.key == pygame.K_DOWN:
                    self.one_player_hovered, self.two_player_hovered = False, True
                elif event.key == pygame.K_UP:
                    self.one_player_hovered, self.two_player_hovered = True, False
                elif event.key == pygame.K_RETURN:
                    if self.one_player_hovered:
                        self.single_player_selecting = True
                        self.selected_mode = "single_player"
                        return None
                    elif self.two_player_hovered:
                        self.multi_player_selecting = True
                        self.selected_mode = "multi_player"
                        return None

        # 单人角色选择界面事件
        elif self.single_player_selecting:
            if event.type == pygame.KEYDOWN and self.current_time - self.last_key_time > self.key_delay:
                self.last_key_time = self.current_time
                if event.key == pygame.K_w:
                    self.focused_character = (self.focused_character - 1) % len(self.character_options)
                    self.selected_character_p1 = self.character_options[self.focused_character]
                elif event.key == pygame.K_s:
                    self.focused_character = (self.focused_character + 1) % len(self.character_options)
                    self.selected_character_p1 = self.character_options[self.focused_character]
                elif event.key == pygame.K_RETURN:
                    self.enemy_selection = True  # 进入敌人选择界面
                    self.selecting_enemy_type = True  # 默认先选择敌人类型
                    return None
                elif event.key == pygame.K_ESCAPE:
                    self.reset()
                    return None

            # Mouse selection for thumbnails
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                thumb_x = 50
                thumb_y = 100
                for i, char_type in enumerate(self.character_options):
                    thumb_rect = pygame.Rect(thumb_x, thumb_y, *self.character_thumb_size)
                    if thumb_rect.collidepoint(event.pos):
                        self.focused_character = i
                        self.selected_character_p1 = char_type
                    thumb_y += self.character_thumb_size[1] + self.character_thumb_margin

                # Check start button (now goes to map selection)
                start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70, 200, 40)
                if start_rect.collidepoint(event.pos):
                    self.map_selecting = True
                    self.selected_map = 0
                    return None

        # 双人角色选择界面事件
        elif self.multi_player_selecting:
            if event.type == pygame.KEYDOWN and self.current_time - self.last_key_time > self.key_delay:
                self.last_key_time = self.current_time
                # Player 1 controls
                if event.key == pygame.K_w:
                    self.focused_character = (self.focused_character - 1) % len(self.character_options)
                    self.selected_character_p1 = self.character_options[self.focused_character]
                elif event.key == pygame.K_s:
                    self.focused_character = (self.focused_character + 1) % len(self.character_options)
                    self.selected_character_p1 = self.character_options[self.focused_character]
                # Player 2 controls
                elif event.key == pygame.K_UP:
                    self.focused_character_p2 = (self.focused_character_p2 - 1) % len(self.character_options)
                    self.selected_character_p2 = self.character_options[self.focused_character_p2]
                elif event.key == pygame.K_DOWN:
                    self.focused_character_p2 = (self.focused_character_p2 + 1) % len(self.character_options)
                    self.selected_character_p2 = self.character_options[self.focused_character_p2]
                elif event.key == pygame.K_RETURN:
                    self.map_selecting = True  # 进入地图选择界面
                    self.selected_map = 0  # 默认选择第一个地图
                    return None
                elif event.key == pygame.K_ESCAPE:
                    self.reset()
                    return None

            # Mouse selection for thumbnails
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Player 1 thumbnails
                thumb_x = 50
                thumb_y = 150
                for i, char_type in enumerate(self.character_options):
                    thumb_rect = pygame.Rect(thumb_x, thumb_y, *self.character_thumb_size)
                    if thumb_rect.collidepoint(event.pos):
                        self.focused_character = i
                        self.selected_character_p1 = char_type
                    thumb_y += self.character_thumb_size[1] + self.character_thumb_margin

                # Player 2 thumbnails
                thumb_x = SCREEN_WIDTH - 100
                thumb_y = 150
                for i, char_type in enumerate(self.character_options):
                    thumb_rect = pygame.Rect(thumb_x, thumb_y, *self.character_thumb_size)
                    if thumb_rect.collidepoint(event.pos):
                        self.focused_character_p2 = i
                        self.selected_character_p2 = char_type
                    thumb_y += self.character_thumb_size[1] + self.character_thumb_margin

                # Check start button (now goes to map selection)
                start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70, 200, 40)
                if start_rect.collidepoint(event.pos):
                    self.map_selecting = True
                    self.selected_map = 0
                    return None

        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()

        # 更新随机地图缩略图
        if current_time - self.last_thumb_switch_time > self.thumb_switch_interval:
            self.last_thumb_switch_time = current_time
            self.current_random_thumb_index = (self.current_random_thumb_index + 1) % len(self.random_map_thumbs)
            self.map_thumbnails["RANDOM"] = self.random_map_thumbs[self.current_random_thumb_index]

        # 更新按钮悬停状态
        if self.single_player_selecting or self.multi_player_selecting:
            self.back_hovered = self.back_button_rect.collidepoint(mouse_pos)
        else:
            self.one_player_hovered = self.one_player_rect.collidepoint(mouse_pos)
            self.two_player_hovered = self.two_player_rect.collidepoint(mouse_pos)
            self.back_hovered = self.back_button_rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """绘制菜单"""
        if hasattr(self, 'map_selecting') and self.map_selecting:
            self._draw_map_selection(screen)
        elif hasattr(self, 'enemy_selection') and self.enemy_selection:
            self._draw_enemy_selection(screen)
        elif self.single_player_selecting:
            self._draw_single_player_selection(screen)
        elif self.multi_player_selecting:
            self._draw_multi_player_selection(screen)
        else:
            # 原始主菜单绘制逻辑
            screen.blit(self.background, (0, 0))
            screen.blit(self.title, self.title_rect)
            one_player_img = self.one_player_btn_hover if self.one_player_hovered else self.one_player_btn
            two_player_img = self.two_player_btn_hover if self.two_player_hovered else self.two_player_btn
            screen.blit(one_player_img, self.one_player_rect)
            screen.blit(two_player_img, self.two_player_rect)

    def reset(self):
        """重置所有菜单状态"""
        self.single_player_selecting = False
        self.multi_player_selecting = False
        if hasattr(self, 'map_selecting'):
            self.map_selecting = False
        if hasattr(self, 'enemy_selection'):
            self.enemy_selection = False
        self.selecting_enemy_type = True
        self.selected_mode = None
        self.selected_character_p1 = "bomberman"
        self.selected_character_p2 = "creep"
        self.one_player_hovered = False
        self.two_player_hovered = False
        self.back_hovered = False