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
screen_width = 1920
screen_height = 1080

# Create game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Alien Shooter')

# Define game variables
start_game = False
game_over = False
fall_sound_played = False

# BACKGROUND
bg = pygame.image.load('graphics/background_space.png').convert_alpha()
menu = pygame.image.load('graphics/menu1.jpg')
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
game_over_fx = pygame.mixer.Sound('audio/game_over.mp3')  # Load your menu sound effect
game_over_fx.set_volume(0.5)
fall_fx = pygame.mixer.Sound('audio/fall.mp3')  # Load your menu sound effect
fall_fx.set_volume(1)
# Load images
bullet_img = pygame.image.load('graphics/bullet/brrr.png').convert_alpha()
asteroid_img = pygame.image.load('graphics/asteroid/asteroid1/0.png').convert_alpha()
destruction_anim = [pygame.image.load(f'graphics/asteroid/asteroid1/{i}.png').convert_alpha() for i in range(4)]
life = pygame.image.load('graphics/life/life.png')
health_img = pygame.image.load('font/health.png')
scaled_image = pygame.transform.scale(health_img, (220, 50))
image_x = 215
image_y = 115
gameover_img = pygame.image.load('graphics/game_over.png')
press_space_img = pygame.image.load('graphics/buttons/space.png')

# Button images
start_img = pygame.image.load('graphics/buttons/start.png').convert_alpha()
exit_img = pygame.image.load('graphics/buttons/exit.png').convert_alpha()
restart_img = pygame.image.load('graphics/buttons/restart.png').convert_alpha()
leave_img = pygame.image.load('graphics/buttons/leave.png').convert_alpha()

# Fade effect function
def fade(width, height, fade_in=True):
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 300):
        fade_surface.set_alpha(alpha if fade_in else 300 - alpha)
        redraw_window()
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(5)
# Function to redraw window contents
# Function to redraw window contents
def redraw_window():
    if not start_game:
        screen.blit(menu, (7, 0))
    else:
        for i in range(tiles):
            screen.blit(bg, (i * bg_width + scroll, 0))
        player.draw()
        asteroid_group.draw(screen)
        bullet_group.draw(screen)
        screen.blit(scaled_image, (image_x, image_y))
        health_bar.draw(player.health)

# Function to redraw window contents
def redraw_window():
    if not start_game:
        screen.blit(menu, (7, 0))
    else:
        for i in range(tiles):
            screen.blit(bg, (i * bg_width + scroll, 0))
        player.draw()
        asteroid_group.draw(screen)
        bullet_group.draw(screen)
        screen.blit(scaled_image, (image_x, image_y))
        health_bar.draw(player.health)
class Ufo(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.alive = True
        self.speed = speed
        self.shoot_cooldown = 0
        self.health = 5
        self.gravity = 5  # Gravity effect
        self.max_health = self.health
        self.animation_list = [
            pygame.transform.scale(pygame.image.load(f'graphics/ufo/{i}.png').convert_alpha(), (180, 180)) for i in
            range(4)]
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.radius = 60
        self.rect.center = (x, y)
        self.direction = 1

    def update(self):
        if self.health <= 0:
           self.alive = False
        else:
            self.update_animation()
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 2
        if not self.alive:
            self.rect.y += self.gravity  # Apply gravity when the UFO is not alive
            if self.rect.top > screen_height:
                self.kill()  # Remove UFO when it goes off-screen


    def move(self, moving_left, moving_right, moving_up, moving_down):
        if not self.alive:
            return  # Do not move if not alive
        dx = 0
        dy = 0
        if moving_left:
            dx = -self.speed
        if moving_right:
            dx = self.speed
        if moving_up:
            dy = -self.speed
        if moving_down:
            dy = self.speed
        if not self.alive:
            return  # Do not move if not alive

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


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 255, 255), (self.x - 2, self.y - 2, 502, 12))
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, 500, 10))
        pygame.draw.rect(screen, (0, 255, 0), (self.x, self.y, 500 * ratio, 10))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
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
        super().__init__()
        self.original_image = asteroid_img
        scale_factor = random.uniform(0.3, 0.5)  # Random scale factor between 0.3x and 0.5x
        self.image = pygame.transform.scale(self.original_image,
                                            (int(self.original_image.get_width() * scale_factor),
                                             int(self.original_image.get_height() * scale_factor)))
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 4)
        self.rect.center = (x, y)
        self.speed_x = 5 * random.randint(1, 2)
        self.speed_y = random.randint(1, 2)
        self.direction = direction
        self.destruction_animation = False
        self.destruction_index = 0
        self.destruction_images = [pygame.transform.scale(img, self.rect.size) for img in destruction_anim]
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()


    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            # Rotate the asteroid image
            new_image = pygame.transform.rotate(self.image_copy, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

            # Rotate destruction images if in destruction animation
            if self.destruction_animation:
                for i, img in enumerate(self.destruction_images):
                    rotated_img = pygame.transform.rotate(img, self.rot)
                    self.destruction_images[i] = rotated_img

    def update(self):
        if self.destruction_animation:
            # Ensure the image is immediately set to the first destruction frame
            if self.destruction_index == 0:
                self.image = self.destruction_images[0]

            self.destruction_index += 0.5
            if self.destruction_index < len(self.destruction_images):
                self.image = self.destruction_images[int(self.destruction_index)]
            else:
                destroy_fx.play()
                self.kill()
        else:
            self.rotate()
            self.rect.x -= self.speed_x
            self.rect.y += (self.direction * self.speed_y)
            if self.rect.right < 0 or self.rect.left > screen_width or self.rect.bottom < 0 or self.rect.top > screen_height:
                self.kill()

    def start_destruction(self):
        self.destruction_animation = True
        self.destruction_index = 0
        # Immediately set the asteroid image to the first destruction frame
        self.image = self.destruction_images[0]
        # Adjust the rect to center the first destruction frame correctly
        self.rect = self.image.get_rect(center=self.rect.center)



# Create buttons
start_button = button.Button(screen_width // 2.155 - start_img.get_width() // 2,screen_height // 1.75 - start_img.get_height() // 2, start_img, 3.75)
exit_button = button.Button(screen_width // 2.155 - exit_img.get_width() // 2,screen_height // 2 + start_img.get_height() // 2 + 175, exit_img, 3.75)
restart_button = button.Button(screen_width // 2.155 - start_img.get_width() // 2,screen_height // 1.75 - start_img.get_height() // 2, start_img, 3.75)
leave_button = button.Button(screen_width // 2.155 - exit_img.get_width() // 2,screen_height // 2 + start_img.get_height() // 2 + 175, exit_img, 3.75)


# Sprite Groups
player = Ufo(500, 500, 10)
health_bar = HealthBar(215, 180, player.health, player.health)
bullet_group = pygame.sprite.Group()
asteroid_group = pygame.sprite.Group()
asteroid_spawn_delay = 300
asteroid_spawn_time = 100

# Play menu sound effect
menu_fx.play(-1)

# Define shaking variables
shake_time = 0
shake_intensity = 5

# Variables for fade and return to menu
fade_black = False
display_press_space = False
return_to_menu = False
press_space_timer = 0
space_pressed = False

run = True
# Inside the game loop
while run:
    clock.tick(60)

    if not start_game:

        # Draw menu
        screen.blit(menu, (7, 0))
        # Add buttons
        if start_button.draw(screen):
            start_game = True
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
        player.draw()

        # Check for collisions between the player and asteroids
        collisions_player = pygame.sprite.spritecollide(player, asteroid_group, True, pygame.sprite.collide_circle)


        # If there is a collision, play the hit sound effect and decrease player's health
        if collisions_player:
            hit_fx.play()
            player.health -= 1
            shake_time = 10  # Set shake time to create shaking effect

        # Update asteroids
        asteroid_spawn_time += clock.get_time()
        if asteroid_spawn_time >= asteroid_spawn_delay:
            asteroid_spawn_time = 5
            asteroid_direction = random.choice([1, 0, -1])
            asteroid_x = screen_width
            asteroid_y = random.randint(0, 1020)
            ast = Asteroid(asteroid_x, asteroid_y, asteroid_direction)
            asteroid_group.add(ast)

        asteroid_group.update()
        bullet_group.update()

        # Check for collisions between bullets and asteroids
        collisions_asteroids = pygame.sprite.groupcollide(asteroid_group, bullet_group, False, True,pygame.sprite.collide_circle)

        for asteroid in collisions_asteroids:
            asteroid.start_destruction()

        # Draw asteroids and bullets
        asteroid_group.draw(screen)
        bullet_group.draw(screen)

        # Apply shaking effect to the screen
        if shake_time > 0:
            screen_shake = [random.randint(-shake_intensity, shake_intensity),
                            random.randint(-shake_intensity, shake_intensity)]
            screen.blit(screen, screen_shake)
            shake_time -= 1

        # Draw health image and bar last to ensure they are on top
        screen.blit(scaled_image, (image_x, image_y))
        health_bar.draw(player.health)

    if not player.alive and not fall_sound_played:
       fall_fx.play()  # Play the fall sound effect
       fall_sound_played = True
       if player.alive:
           fall_sound_played = False

            # Player shooting
    if player.alive:
        if shoot:
            player.shoot()


    if not player.alive:
        game_over = True
        pygame.mixer.music.stop()
        game_over_fx.play()

    if game_over:
        screen.blit(gameover_img, (screen_width // 2 - gameover_img.get_width() // 2, screen_height // 2 - gameover_img.get_height() // 2))

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