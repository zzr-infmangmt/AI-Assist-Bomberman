import pygame
from enum import Enum, auto
from constants import resource_path



class Direction(Enum):
    FRONT = auto()
    BACK = auto()
    SIDE = auto()


class Animation:
    def __init__(self, images, interval=100, repeat=0, flip_x=False, flip_y=False):
        self.frames = self._prepare_frames(images, flip_x, flip_y)
        self.interval = interval
        self.repeat = repeat
        self.current_frame = 0
        self.last_update = 0
        self.loop_count = 0

    def is_playing(self):
        """检查动画是否正在播放"""
        return self.loop_count < self.repeat if self.repeat > 0 else True

    def _prepare_frames(self, images, flip_x, flip_y):
        frames = []
        if isinstance(images, pygame.Surface):
            return self.load_spritesheet_frames(images)

        for img in images:
            if isinstance(img, str):
                try:
                    # 修改这里，使用resource_path处理路径
                    img_path = resource_path(img)
                    img = pygame.image.load(img_path).convert_alpha()
                except pygame.error as e:
                    print(f"Error loading image {img}: {e}")
                    continue
            if flip_x or flip_y:
                img = pygame.transform.flip(img, flip_x, flip_y)
            frames.append(img)
        return frames

    def load_spritesheet_frames(self, spritesheet, cols=5, rows=1):
        """Load frames from a spritesheet."""
        frames = []
        frame_width = spritesheet.get_width() // cols
        frame_height = spritesheet.get_height() // rows

        for row in range(rows):
            for col in range(cols):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(spritesheet, (0, 0),
                           (col * frame_width, row * frame_height, frame_width, frame_height))
                frames.append(frame)

        return frames

    def load_frames(self, images, flip_x, flip_y):
        """加载并处理动画帧"""
        for img in images:
            # 如果传入的是字符串路径
            if isinstance(img, str):
                try:
                    # 修改这里，使用resource_path处理路径
                    img_path = resource_path(img)
                    img = pygame.image.load(img_path).convert_alpha()
                except pygame.error as e:
                    print(f"Error loading image {img}: {e}")
                    continue

            # 应用翻转
            if flip_x or flip_y:
                img = pygame.transform.flip(img, flip_x, flip_y)

            self.frames.append(img)

    def update(self, current_time):
        """Update animation frame based on time"""
        if current_time - self.last_update > self.interval:
            self.last_update = current_time
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            if self.current_frame == 0:
                self.loop_count += 1
                if 0 < self.repeat <= self.loop_count:
                    return False  # Animation completed
        return True  # Animation still running

    def get_current_frame(self):
        """Get current frame surface"""
        return self.frames[self.current_frame]


class AnimationController:
    def __init__(self):
        self.is_playing = None
        self.animations = {}
        self.current_anim = None
        self.current_name = ""

    def add(self, name, animation):
        """Add a named animation"""
        self.animations[name] = animation

    def play(self, name):
        """Start playing a named animation"""
        if name in self.animations and name != self.current_name:
            self.current_name = name
            self.current_anim = self.animations[name]
            self.current_anim.current_frame = 0
            self.current_anim.last_update = pygame.time.get_ticks()
            self.current_anim.loop_count = 0
            self.is_playing = True

    def update(self, current_time):
        """Update current animation"""
        if self.current_anim and self.is_playing:
            return self.current_anim.update(current_time)
        return True

    def get_current_frame(self):
        """Get current frame of current animation"""
        if self.current_anim:
            return self.current_anim.get_current_frame()
        return None