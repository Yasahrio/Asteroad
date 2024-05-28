import pygame
from pygame import mixer
import math
import random
import button

# Initialize Pygame
mixer.init()
pygame.init()
clock = pygame.time.Clock()

# OVERALL DISPLAY
# Screen Resolution
screen_width = 1920
screen_height = 1080

# Create game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Alien Shooter')

# Define game variables
start_game = False

# BACKGROUND
bg = pygame.image.load('graphics/background_space.png').convert_alpha()
menu = pygame.image.load('graphics/menu.png')
bg_width = bg.get_width()
# Define game variables
scroll = 0
tiles = math.ceil(screen_width / bg_width) + 1
# Action variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False
shoot = False
# Load music and sounds
background_music = 'audio/background_music.mp3'
shot_fx = pygame.mixer.Sound('audio/shoot.mp3')
shot_fx.set_volume(0.6)
hit_fx = pygame.mixer.Sound('audio/hit.mp3')
destroy_fx = pygame.mixer.Sound('audio/destroy.mp3')
destroy_fx.set_volume(0.5)
menu_fx = pygame.mixer.Sound('audio/menu.mp3')  # Load your menu sound effect
menu_fx.set_volume(0.5)

# Load images
bullet_img = pygame.image.load('graphics/bullet/brrr.png').convert_alpha()
asteroid_img = pygame.image.load('graphics/asteroid/asteroid1/0.png').convert_alpha()
destruction_anim = []
for i in range(4):
    img = pygame.image.load(f'graphics/asteroid/asteroid1/{i}.png').convert_alpha()
    destruction_anim.append(img)

progress_bar_empty = pygame.image.load('graphics/progress bar/bar.png').convert_alpha()
progress_bar_fill =pygame.image.load('graphics/progress bar/icon.png').convert_alpha()

# Button images
start_img = pygame.image.load('graphics/buttons/start.png').convert_alpha()
exit_img = pygame.image.load('graphics/buttons/exit.png').convert_alpha()

#progressbar variables
total_time = 186 #3 minutes and 6 seconds
start_time = None

class Ufo(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.speed = speed
        self.shoot_cooldown = 0
        self.health = 5
        self.max_health = self.health
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        for i in range(4):
            img = pygame.image.load(f'graphics/ufo/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (180, 180))
            self.animation_list.append(img)
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.radius = 60
        self.rect.center = (x, y)
        self.direction = 1

    def update(self):
        self.update_animation()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 2

    def move(self, moving_left, moving_right, moving_up, moving_down):
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
            self.direction = 1
        if moving_right:
            dx = self.speed
            self.direction = 1
        if moving_up:
            dy = -self.speed
            self.direction = 1
        if moving_down:
            dy = self.speed
            self.direction = 1

        player_movement_left = screen_width // 10.65
        player_movement_right = screen_width - (screen_width // 10.65)
        player_movement_top = screen_height // 11.30
        player_movement_bottom = screen_height - (screen_height // 17)

        boundary_x = self.rect.x + dx
        boundary_y = self.rect.y + dy

        if boundary_x < player_movement_left:
            boundary_x = player_movement_left
        if boundary_x > player_movement_right - self.rect.width:
            boundary_x = player_movement_right - self.rect.width
        if boundary_y < player_movement_top:
            boundary_y = player_movement_top
        if boundary_y > player_movement_bottom - self.rect.height:
            boundary_y = player_movement_bottom - self.rect.height

        self.rect.x = boundary_x
        self.rect.y = boundary_y

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0]), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            shot_fx.play()

    def update_animation(self):
        ANIMATION_COOLDOWN = 70
        self.image = self.animation_list[int(self.frame_index)]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

    def draw(self):
        screen.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 50
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.radius = 15
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = asteroid_img
        scale_factor = random.uniform(0.3, 0.5)  # Random scale factor between 0.5x and 1x
        self.image = pygame.transform.scale(self.original_image,
                                            (int(self.original_image.get_width() * scale_factor),
                                             int(self.original_image.get_height() * scale_factor)))
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 4)

        self.rect.center = (x, y)
        self.speed_x = 5 * random.randint(1, 2)
        self.speed_y = random.randint(1, 2)
        self.direction = direction
        self.destruction_animation = False
        self.destruction_index = 0
        self.destruction_images = [pygame.transform.scale(img, self.rect.size) for img in destruction_anim]

    def update(self):
        if self.destruction_animation:
            self.image = self.destruction_images[int(self.destruction_index)]
            self.destruction_index += 0.5
            if self.destruction_index >= len(self.destruction_images):
                destroy_fx.play()
                self.kill()
        else:
            self.rect.x -= self.speed_x
            self.rect.y += (self.direction * self.speed_y)
            if self.rect.right < 0 or self.rect.left > screen_width or self.rect.bottom < 0 or self.rect.top > screen_height:
                self.kill()


# Create buttons
start_button = button.Button(screen_width // 2 - start_img.get_width() // 2, screen_height // 2 - start_img.get_height() // 2, start_img, 4)
exit_button = button.Button(screen_width // 2 - exit_img.get_width() // 2, screen_height // 2 + start_img.get_height() // 2 + 150, exit_img, 4)

# Sprite Groups
bullet_group = pygame.sprite.Group()
asteroid_group = pygame.sprite.Group()
player = Ufo(500, 500, 10)
asteroid_spawn_delay = 500
asteroid_spawn_time = 100

# Play menu sound effect
menu_fx.play(-1)

def draw_progress_bar(screen, x, y, width, height, progress):
    # Draw the empty progress bar
    screen.blit(progress_bar_empty, (x, y))

    # Calculate the width of the filled portion
    filled_width = int(progress * width)

    # Draw the filled portion
    screen.blit(progress_bar_fill, (x, y), (0, 0, filled_width, height))

run = True
# Inside the game loop
while run:
    clock.tick(60)

    if not start_game:
        # Draw menu
        screen.blit(menu, (0, 0))
        # Add buttons
        if start_button.draw(screen):
            start_game = True
            player.health = player.max_health  # Reset health when the game starts
            menu_fx.stop()
            pygame.mixer.music.load(background_music)
            pygame.mixer.music.set_volume(0.9)
            pygame.mixer.music.play(-1)
        if exit_button.draw(screen):
            run = False
    else:
        # Blit background
        for i in range(tiles):
            screen.blit(bg, (i * bg_width + scroll, 0))
        scroll -= 5
        if abs(scroll) > bg_width:
            scroll = 0

        # Update and draw the player
        player.update()

        # Check for collisions between the player and asteroids
        collisions_player = pygame.sprite.spritecollide(player, asteroid_group, True, pygame.sprite.collide_circle)

        # If there is a collision, play the hit sound effect and decrease player's health
        if collisions_player:
            hit_fx.play()
            player.health -= 1


        player.draw()

        # Update asteroids
        asteroid_spawn_time += clock.get_time()
        if asteroid_spawn_time >= asteroid_spawn_delay:
            asteroid_spawn_time = 5
            asteroid_direction = random.choice([1, 0, - 1])
            asteroid_x = screen_width + 0
            asteroid_y = random.randint(0,1020)
            ast = Asteroid(asteroid_x, asteroid_y, asteroid_direction)
            asteroid_group.add(ast)

        asteroid_group.update()
        bullet_group.update()

        # Check for collisions between bullets and asteroids
        collisions_asteroids = pygame.sprite.groupcollide(asteroid_group, bullet_group, False, True, pygame.sprite.collide_circle)

        for asteroid in collisions_asteroids:
            asteroid.destruction_animation = True

        # Draw asteroids and bullets
        asteroid_group.draw(screen)
        bullet_group.draw(screen)

        # Update the progress bar
        if start_time is not None:
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
            progress = elapsed_time / total_time
            if progress > 1:
                progress = 1
                # Game ends when progress is complete, add your game end logic here

            # Draw the progress bar at the top center of the screen
            draw_progress_bar(screen, (screen_width - progress_bar_empty.get_width()) // 100, 1000,
                              progress_bar_empty.get_width(), progress_bar_empty.get_height(), progress)

    # Player shooting
    if player.alive:
        if shoot:
            player.shoot()



    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_UP:
                moving_up = True
            if event.key == pygame.K_DOWN:
                moving_down = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_UP:
                moving_up = False
            if event.key == pygame.K_DOWN:
                moving_down = False
            if event.key == pygame.K_SPACE:
                shoot = False

    # Move the player
    player.move(moving_left, moving_right, moving_up, moving_down)

    # Update the display
    pygame.display.update()

pygame.quit()
