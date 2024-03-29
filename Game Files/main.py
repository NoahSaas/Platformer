from inspect import getblock
import os
import random
import math
import pygame
import time
from os import listdir
from os.path import isfile, join
pygame.init()

pygame.display.set_caption("Platformer")

# Defining global variables
WIDTH, HEIGHT = 800, 500
FPS = 60
PLAYER_VEL = 4
victory = False

window = pygame.display.set_mode((WIDTH, HEIGHT))


# Flips the direction of the sprite
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


# Loads and cut the sprite sheet in order to get the animaton in the proper order
    # dir1/dir2 - directories leading to the texture png
    # width/height - dimensions for the spritesheet
    # direction - the direction that the sprite is supposed to face
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


# Selects a part of the terrain image depending on the block and returns it
    # size - the width/height of the block thats being loaded
    # cut_x/cut_y - the position of the texture png where the block is being cut
def get_block(size, cut_x, cut_y):
    path = join("Game Files", "assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(cut_x, cut_y, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


# Player class that stores all the related stats and variables
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Sprites", "NinjaFrog", 32, 32, True)
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
        self.coins = 0
        self.enable_heal = True

    # Function that launches the player up        
    def jump(self):
        if self.jump_count == 0 and self.fall_count <= 9:
            self.fall_count = 0
            self.y_vel = -self.GRAVITY * 7
        elif self.jump_count < 2:
            self.fall_count = 0
            self.y_vel = -self.GRAVITY * 6
            self.jump_count += 1
        self.animation_count = 0
        self.jump_count += 1

    # Moves the player left or right
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    # Event that signals the player being hit
    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    # Function that displaces the player to the left and handles the animation correction
    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    # Function that displaces the player to the right and handles the animation correction
    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    # Main loop for the player logic
    def loop(self, fps):
        if self.y_vel < 10:
            self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        if self.hit:
            self.enable_heal = False
            self.hit_count += 1
            if self.health > 0:
                self.health -= 0.5
        if self.hit_count > fps * 1.5:
            self.hit = False
            self.enable_heal = True
            self.hit_count = 0
            self.temp_val = time.time()
        if self.enable_heal and self.health < 100 and time.time() > (self.temp_val + 3):
            self.health += 0.1
            self.health = round(self.health, 1)

        self.fall_count += 1
        self.update_sprite()

    # Event that signal that the player has landed
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    # Event that signal that the player hit their head
    def hit_head(self):
        self.y_vel *= -0.1

    # Function to display your health points in the form of hearts
    def display_hp(self, win):
        heart_size = 32
        heart_padding = heart_size // 6

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

    # Same but with coins
    def display_coins(self, win):
        coin_size = 32

        path1 = join("Game Files", "assets", "Misc", "coin_HUD.png")
        coin_image = pygame.image.load(path1).convert_alpha()
        coin_image = pygame.transform.scale(coin_image, (coin_size, coin_size))

        font = pygame.font.Font('freesansbold.ttf', 32)
        text_surface = pygame.Surface((100, 50), pygame.SRCALPHA)
        text_rect = text_surface.get_rect(topright=(WIDTH + 25, 16))
        
        text = font.render((str(self.coins) + " / 3"), True, (240, 240, 16))
        text_surface.blit(text, (0, 0))

        coin_rect = pygame.Rect(coin_size, coin_size, coin_size, coin_size)
        coin_rect.topright = (WIDTH - 86, 16)


        win.blit(text_surface, text_rect)
        win.blit(coin_image, coin_rect.topleft)

    # Collects coins and edits stats
    def collect_coin(self, coin, objects):
        objects.remove(coin)
        self.coins += 1

    # Depending on what the character is doing it updates to the correct animation
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
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    # Aligns the hitbox and the sprite
    def update(self):
        if hasattr(self, 'sprite'):
            self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))

    # Draws the sprite
    def draw(self, win, offset_x):
        if hasattr(self, 'sprite'):
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


# Parent class for future objects and classes
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    # Draw the object
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


# Block class
class Block(Object):
    def __init__(self, x, y, size, type):
        super().__init__(x, y, size, size)
        
        # Checks what block should be placed and selects the texture accordingly
        if type == "normal":
            block = get_block(size, 96, 0)
        elif type == "small":
            block = get_block(size // 6, 192, 80)
            self.rect.width = size // 6
            self.rect.height = size // 6 
        self.image.blit(block, (0, 0))


# Coin class
class Coin(Object):
    ANIMATION_DELAY = 4

    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "coin")
        self.coin = load_sprite_sheets("Items", "Coin", size, size)
        self.animation_count = 0


    # Logic loop that handles the animation of the coin
    def loop(self):
        sprites = self.coin["gold_coin"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.scaled_image = pygame.transform.scale_by(self.image, (1, 1))
        self.animation_count += 1
        self.rect = self.scaled_image.get_rect(topleft=(self.rect.x, self.rect.y))

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


#Finishline class
class Finish(Object):
    ANIMATION_DELAY = 4

    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, "finish")
        self.finish_line = load_sprite_sheets("Items", "Finish", size, size)

    # Same stuff, creates a hitbox and lines it up with the image
    def loop(self):
        sprites = self.finish_line["finish"]
        self.image = sprites[0]
        self.scaled_image = pygame.transform.scale_by(self.image, (1, 1))
        self.rect = self.scaled_image.get_rect(topleft=(self.rect.x, self.rect.y))


#Firetrap class
class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.animation_count = 0
        self.animation_name = "off"
        self.temp_val = time.time()

    # Changes the animation of the trap
    def on(self):
        self.animation_name = "on"

    # Changes the animation of the trap
    def off(self):
        self.animation_name = "off"

    # Handles the logic for the fire trap, turns the trap on/off after 2 seconds in a loop, also handles the animations.
    def loop(self):
        if time.time() > (self.temp_val + 2):
            self.temp_val = time.time()
            if self.animation_name == "off":
                self.on()
            else:
                self.off()

        
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.scaled_image = pygame.transform.scale_by(self.image, (0.8, 1))
        self.animation_count += 1
        self.rect = self.scaled_image.get_rect(topleft=(self.rect.x, self.rect.y))

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


# Loads the background texture and calculates how to split it up to cover the entire screen
    # name - the name of the backgroundtile that should be selected
def get_background(name):
    image = pygame.image.load(join("Game Files", "assets", "Backgrounds", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


# Draws all the objects and stuff on the screen
    # window - the window that the game is displayed on
    # background - the background that should be drawn
    # bg_image - the png tile of the background that should be drawn
    # player - the player character
    # objects - the objects like blocks, traps etc
    # offset_x - dictates how aggressive the camera scroll should be
def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    player.display_hp(window)
    player.display_coins(window)

    pygame.display.update()


# Handles vertical collisions by checking if the rectangles collide 
    # player - the player character
    # objects - the objects like blocks, traps etc
    # dy - the velocity that the player gains/loses
def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    player_rect = player.rect.copy()

    player_rect.y += dy

    for obj in objects:
        if player_rect.colliderect(obj.rect):
            if dy > 0 and obj.name != "coin":
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0 and obj.name != "coin":
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


# Same thing but it checks vertical collisions
    # player - the player character
    # objects - the objects like blocks, traps etc
    # dx - the velocity that the player gains/loses
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


# Movement handler, keystrokes and registers collision between players and objects.
    # player - the player character
    # objects - the objects like blocks, traps etc
def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL)
    collide_right = collide(player, objects, PLAYER_VEL)

    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    elif keys[pygame.K_a] and collide_left.name == "coin":
        player.collect_coin(collide_left, objects)
    elif keys[pygame.K_a] and collide_left.name == "finish":
        clear_level(objects)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)
    elif keys[pygame.K_d] and collide_right.name == "coin":
        player.collect_coin(collide_right, objects)
    elif keys[pygame.K_d] and collide_right.name == "finish":
        clear_level(objects)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [*vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire" and obj.animation_name == "on":
            player.make_hit()
        elif obj and obj.name == "coin":
            player.collect_coin(obj, objects)
        elif obj and obj.name == "finish" and player.coins == 3:
            clear_level(objects)


# The "level data" for level 1. Very shitty and horrible structure and absolutely the worst possible way to store level data, also a nightmare to add stuff. Should've used a 2D grid system to store level data.
    # level_id - the id of the current level
def load_scene(level_id):
    if level_id == 1:
        background, bg_image = get_background("Brown.png")
        block_size = 96
        fire_trap_size = 32
        player = Player(100, HEIGHT - block_size - 200, 50, 50)

        floor = [Block(i * block_size, HEIGHT - block_size, block_size, "normal") for i in range(-3, (WIDTH * 3) // block_size)]
        fire_roof = [Block(block_size * 5 + i * 32, HEIGHT - block_size * 3 + 64, block_size, "small") for i in range (9, 36)]
        fire_roof_pillars1 = [Block(768, i * 32 - 12, block_size, "small") for i in range(0, 9)]
        fire_roof_pillars2 = [Block(768 + block_size * 9 - 32, i * 32 - 12, block_size, "small") for i in range(0, 9)]
        fire_pit1 = [Fire(block_size * 6 + fire_trap_size * i , HEIGHT - block_size, 16, 32) for i in range(9, 18)]
        fire_pit2 = [Fire(block_size * 10 + fire_trap_size * i , HEIGHT - block_size, 16, 32) for i in range(9, 18)]
        fire_pit_floor1 = [Block(block_size * 6 + fire_trap_size * i, HEIGHT - block_size + 64, block_size, "small") for i in range(9, 18)]
        fire_pit_floor2 = [Block(block_size * 10 + fire_trap_size * i, HEIGHT - block_size + 64, block_size, "small") for i in range(9, 18)]
        parkour = [Block(block_size * 21, HEIGHT - block_size * 2, block_size, "small"), Block(block_size * 23, HEIGHT - block_size * 3, block_size, "small"), Block(block_size * 27, HEIGHT - block_size * 3, block_size, "small"), Block(block_size * 29, HEIGHT - block_size * 1.5, block_size, "small"), Block(block_size * 33, HEIGHT - block_size * 2, block_size, "small")]
        finish_line = [Block(i * block_size, HEIGHT - block_size, block_size, "normal") for i in range(35, 44)]

        del floor[8], floor[8], floor[8], floor[9], floor[9], floor[9], floor[10], floor[10], floor[10], floor[13], floor[13], floor[13], floor[13], floor[13], floor[13], 

        objects = [*floor, *fire_roof, *fire_roof_pillars1, *fire_roof_pillars2, *fire_pit_floor1, *fire_pit_floor2, *parkour, *finish_line]
        traps = [*fire_pit1, *fire_pit2]
        items = [Coin(1565, HEIGHT - (96 + 64), 16), Coin(800, HEIGHT - (96 + 64), 16), Coin(3060, HEIGHT - 175, 16), Finish(3936, HEIGHT - (96 + 96), 64)]

        for trap in traps:
            objects.append(trap)
            if type(trap) == Fire:
                trap.on()

        for item in items:
            objects.append(item)

        offset_x = 0
        return player, objects, offset_x, background, bg_image, traps


# Unloads the level
    # objects - the objects like blocks, traps etc
def unload_scene(objects):
    objects.clear()


# Marks the level as cleared 
    # objects - the objects like blocks, traps etc
def clear_level(objects):
    unload_scene(objects)
    global victory
    victory = True


# Draws the victory screen
    # window - the window that the game is displayed on
def draw_victory_screen(window):
    window.fill((255, 255, 255)) 

    victory_image_path = join("Game Files", "assets", "Backgrounds", "Victory.png")
    victory_image = pygame.image.load(victory_image_path)
    
    victory_image = pygame.transform.scale(victory_image, (WIDTH, HEIGHT))
    
    image_rect = victory_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(victory_image, image_rect)


# Main function
    # window - the window that the game is displayed on
def main(window):
    global victory
    clock = pygame.time.Clock()
    scroll_area_width = 200
    # Loads up the level 
    player, objects, offset_x, background, bg_image, traps = load_scene(1)

    run = True
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            # Check for jump inputs
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    player.jump()


        # Enables the loop logic for the objects responsible for animation and hitboxes.
        player.loop(FPS)
        for trap in traps:
            trap.loop()

        for item in objects:
            if item.name == "coin" or item.name == "finish":
                item.loop()

        
        handle_move(player, objects)
        
        draw(window, background, bg_image, player, objects, offset_x)

        # Checks if the player is out of the map or dead and resets the map
        if player.health <= 0 or player.rect.y >= 1000:
            unload_scene(objects)
            player, objects, offset_x, background, bg_image, traps = load_scene(1)

        # Camera scroll
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel


        # When you win the game run the victory screen and close the game
        if victory:
            draw_victory_screen(window)
            pygame.display.update()
            pygame.time.delay(3000)
            break

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)