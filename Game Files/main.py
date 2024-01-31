from email.errors import ObsoleteHeaderDefect
import os
import random
import math
import pygame
import time
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 800, 500
FPS = 60
PLAYER_VEL = 4

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("Game Files", "assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size, type):
    path = join("Game Files", "assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    if type == "block":
        clip_at_x = 96
        clip_at_y = 0
    elif type == "small_block":
        clip_at_x = 192
        clip_at_y = 80
    rect = pygame.Rect(clip_at_x, clip_at_y, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Sprites", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.health = 100
        self.enable_heal = True

    def jump(self):
        if self.jump_count == 0 and self.fall_count <= 9:
            self.fall_count = 0
            self.y_vel = -self.GRAVITY * 7
        elif self.jump_count < 4:
            self.fall_count = 0
            self.y_vel = -self.GRAVITY * 6
            self.jump_count += 1
        self.animation_count = 0
        self.jump_count += 1

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        if self.y_vel < 10:
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        if self.hit:
            self.enable_heal = False
            self.hit_count += 1
            if self.health > 0:
                self.health -= 0.25
        if self.hit_count > fps * 1.7:
            self.hit = False
            self.enable_heal = True
            self.hit_count = 0
            self.temp_val = time.time()
        if self.enable_heal and self.health < 100 and time.time() > (self.temp_val + 3):
            self.health += 0.1
            self.health = round(self.health, 1)

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.y_vel *= -0.1

    def display_hp(self, win):
        heart_size = 32
        heart_padding = heart_size / 6

        path1 = join("Game Files", "assets", "Misc", "heart.png")
        path2 = join("Game Files", "assets", "Misc", "empty_heart.png")
        heart_image = pygame.image.load(path1).convert_alpha()
        heart_image = pygame.transform.scale(heart_image, (heart_size, heart_size))
        empty_heart_image = pygame.image.load(path2).convert_alpha()
        empty_heart_image = pygame.transform.scale(empty_heart_image, (heart_size, heart_size))


        for i in range(10):
            heart_x = i * (heart_size + heart_padding)
            heart_rect = pygame.Rect(heart_x + 10, 10, heart_size, heart_size)

            if i * 10 < self.health:
                win.blit(heart_image, heart_rect.topleft)
            else:
                win.blit(empty_heart_image, heart_rect.topleft)

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        if hasattr(self, 'sprite'):
            self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))

    def draw(self, win, offset_x, offset_y):
        if hasattr(self, 'sprite'):
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, size, type):
        super().__init__(x, y, size, size)
        block = get_block(size, type)
        self.image.blit(block, (0, 0))


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.scaled_image = pygame.transform.scale_by(self.image, (0.8, 1))
        self.animation_count += 1

        self.rect = self.scaled_image.get_rect(topleft=(self.rect.x, self.rect.y))


        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("Game Files", "assets", "Backgrounds", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x, offset_y):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)
    player.display_hp(window)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    player_rect = player.rect.copy()

    player_rect.y += dy

    for obj in objects:
        if player_rect.colliderect(obj.rect):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx , 0)
    player.update()
    collided_object = None

    for obj in objects:
        if player.rect.colliderect(obj.rect):
            collided_object = obj
            break

    player.move(-dx , 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL)
    collide_right = collide(player, objects, PLAYER_VEL)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [*vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire" and obj.animation_name == "on":
            player.make_hit()


def load_scene(level_id):
    if level_id == 1:
        background, bg_image = get_background("Brown.png")
        block_size = 96
        small_block = 32
        player = Player(100, HEIGHT - block_size - 200, 50, 50)
        floor = [Block(i * block_size, HEIGHT - block_size, block_size, "block") for i in range(-3, (WIDTH * 3) // block_size)]
        del floor[6], floor[6], floor[6], floor[8], floor[8]
        obstacles = [Block(block_size * 10, HEIGHT - block_size * 2, block_size, "block"), Block(block_size * 11, HEIGHT - block_size * 4, block_size, "block")]
        objects = [*floor, *obstacles]
        traps = [Fire(block_size * 7.25, HEIGHT - block_size - 64, 16, 32)]

        for trap in traps:
            objects.append(trap)
            if type(trap) == Fire:
                trap.on()

        offset_x = 0
        offset_y = 0
        return player, objects, offset_x, offset_y, background, bg_image, traps


def unload_scene(objects):
    objects.clear()


def main(window):
    clock = pygame.time.Clock()
    scroll_area_width = WIDTH // 3
    player, objects, offset_x, offset_y, background, bg_image, traps = load_scene(1)

    run = True
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    player.jump()


        player.loop(FPS)
        for trap in traps:
            trap.loop()

        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x, offset_y)

        if player.health <= 0 or player.rect.y >= 750:
            unload_scene(objects)
            player, objects, offset_x, offset_y, background, bg_image, traps = load_scene(1)


        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel



    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)