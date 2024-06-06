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

# Define a font for displaying the score
font = pygame.font.Font('font/PressStart2P-Regular.ttf', 36)


# BACKGROUND
bg = pygame.image.load('graphics/space.png').convert_alpha()
bg_layer1 = pygame.image.load('graphics/space_layer1.png').convert_alpha()
bg_layer2 = pygame.image.load('graphics/space_layer2.png').convert_alpha()
menu = pygame.image.load('graphics/menu1.jpg').convert_alpha()
bg_width = bg.get_width()

# Define game variables
scroll = 0
scroll_layer1 = 0
scroll_layer2 = 0
tiles = math.ceil(screen_width / bg_width) + 3
parallax_factor_bg = 0.03
parallax_factor_bg_layer1 = 0.05
parallax_factor_bg_layer2 = 0.07
parallax_factor_ufo = 0.5

PBAR_LEN = 450  # Length of the progress bar
PBAR_MAX = 12000  # Maximum value of the progress bar
PBAR_SPD = 1   # Speed at which the progress bar fills up
pbar_current = 0  # Current value of the progress bar
level = 1

# Action variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False
shoot = False

# Load music and sounds
background_music = 'audio/background_music.mp3'
pygame.mixer.music.set_volume(0.7)
shot_fx = pygame.mixer.Sound('audio/shoot.mp3')
shot_fx.set_volume(0.4)
hit_fx = pygame.mixer.Sound('audio/hit.mp3')
destroy_fx = pygame.mixer.Sound('audio/destroy.mp3')
destroy_fx.set_volume(1)
menu_fx = pygame.mixer.Sound('audio/menu.mp3')  # Load your menu sound effect
menu_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('audio/game_over.mp3')  # Load your menu sound effect
game_over_fx.set_volume(0.5)
fall_fx = pygame.mixer.Sound('audio/fall.mp3')  # Load your menu sound effect
fall_fx.set_volume(1)
# Load images
progress_bar_img = bullet_img = pygame.image.load('graphics/progress bar/bar.png').convert_alpha()
bullet_img = pygame.image.load('graphics/bullet/brrr.png').convert_alpha()
asteroid_img = pygame.image.load('graphics/asteroid/asteroid3/0.png').convert_alpha()
destruction_anim = [pygame.image.load(f'graphics/asteroid/asteroid3/{i}.png').convert_alpha() for i in range(6)]
life = pygame.image.load('graphics/life/life.png')
health_img = pygame.image.load('font/health.png')
scaled_image = pygame.transform.scale(health_img, (220, 51))
PGscaled_image = pygame.transform.scale(progress_bar_img, (500, 200))
PGimage_x = 1175
PGimage_y = 83.99
image_x = 215
image_y = 115
gameover_img = pygame.image.load('graphics/game_over.png')


# Button images
start_img = pygame.image.load('graphics/buttons/start.png').convert_alpha()
exit_img = pygame.image.load('graphics/buttons/exit.png').convert_alpha()
restart_img = pygame.image.load('graphics/buttons/restart.png').convert_alpha()
leave_img = pygame.image.load('graphics/buttons/leave.png').convert_alpha()


font_name = pygame.font.match_font('pixel')
def draw_text(surf, text,size, x, y):
    font = pygame.font.Font('font/PressStart2P-Regular.ttf', 36)
    text_surface = font.render(text, True, (255,255,255))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

class Ufo(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.alive = True
        self.speed = speed
        self.shoot_cooldown = 0
        self.health = 25
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
        self.speed_y = dy  # Update vertical speed

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 16
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
        scale_factor = random.uniform(0.6, 1.2)  # Random scale factor between 0.8x and 1x
        self.image = pygame.transform.scale(self.original_image,
                                            (int(self.original_image.get_width() * scale_factor),
                                             int(self.original_image.get_height() * scale_factor)))
        self.image_copy = self.image.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 4)
        self.rect.center = (x, y)
        self.speed_x = 5 * random.uniform(0.8, 1)
        self.speed_y = random.uniform(1, 2)
        self.direction = direction
        self.destruction_animation = False
        self.destruction_index = 0
        self.destruction_images = [pygame.transform.scale(img, self.rect.size) for img in destruction_anim]
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        self.rotation_at_destruction = 0

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
                    rotated_img = pygame.transform.rotate(img, self.rotation_at_destruction)
                    self.destruction_images[i] = rotated_img

    def update(self):
        if self.destruction_animation:
            # Ensure the image is immediately set to the first destruction frame
            if self.destruction_index == 0:
                self.image = self.destruction_images[0]

            self.destruction_index += 0.375
            if self.destruction_index < len(self.destruction_images):
                self.image = self.destruction_images[int(self.destruction_index)]
            else:
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
        self.radius = 0  # Set radius to zero to prevent further collisions
        self.rotation_at_destruction = self.rot  # Store the rotation at the time of destruction
        # Rotate all destruction images to match the current rotation
        self.destruction_images = [pygame.transform.rotate(img, self.rotation_at_destruction) for img in destruction_anim]
        # Immediately set the asteroid image to the first destruction frame
        self.image = self.destruction_images[0]
        # Adjust the rect to center the first destruction frame correctly
        self.rect = self.image.get_rect(center=self.rect.center)



# Create buttons
start_button = button.Button(screen_width // 2.155 - start_img.get_width() // 2,screen_height // 1.75 - start_img.get_height() // 2, start_img, 3.75)
exit_button = button.Button(screen_width // 2.155 - exit_img.get_width() // 2,screen_height // 2 + start_img.get_height() // 2 + 175, exit_img, 3.75)


# Sprite Groups
player = Ufo(500, 500, 10)
health_bar = HealthBar(215, 180, player.health, player.health)
bullet_group = pygame.sprite.Group()
asteroid_group = pygame.sprite.Group()
asteroid_spawn_delay = 400
asteroid_spawn_time = 100

# Play menu sound effect
menu_fx.play(-1)

# Define shaking variables
shake_time = 0
shake_intensity = 5

def reset_game():
    global scroll, scroll_layer1, scroll_layer2, ufo, health_bar, asteroid_group, bullet_group, start_game, game_over, fall_sound_played
    scroll = 0
    scroll_layer1 = 0
    scroll_layer2 = 0
    start_game = False
    game_over = False
    fall_sound_played = False
    ufo = Ufo(180, 220, 15)
    health_bar = HealthBar(180, 80, ufo.health, ufo.health)
    asteroid_group.empty()
    bullet_group.empty()

def game_loop():
    global start_game, game_over, scroll, scroll_layer1, scroll_layer2, tiles, fall_sound_played

scroll_y = 0
scroll_layer1_y = 0
scroll_layer2_y = 0

score = 0
score_milestone = 600
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
        max_scroll_y = 10  # Maximum upward scroll
        min_scroll_y = -33  # Maximum downward scroll
        scroll_y = max(min(scroll_y, max_scroll_y), min_scroll_y)

        max_scroll_layer1_y = 35  # Maximum upward scroll for layer 1
        min_scroll_layer1_y = -30  # Maximum downward scroll for layer 1
        scroll_layer1_y = max(min(scroll_layer1_y, max_scroll_layer1_y), min_scroll_layer1_y)

        max_scroll_layer2_y = 35  # Maximum upward scroll for layer 2
        min_scroll_layer2_y = -35  # Maximum downward scroll for layer 2
        scroll_layer2_y = max(min(scroll_layer2_y, max_scroll_layer2_y), min_scroll_layer2_y)

        # Blit background
        for i in range(0, tiles):
            screen.blit(bg, (i * bg_width + scroll, 100))
        for i in range(0, tiles):
            screen.blit(bg_layer1, (i * bg_width + scroll_layer1, 100   ))
        for i in range(0, tiles):
            screen.blit(bg_layer2, (i * bg_width + scroll_layer2, 100))

        for i in range(0, tiles):
            screen.blit(bg, (i * bg_width + scroll, 100 + scroll_y))
        for i in range(0, tiles):
            screen.blit(bg_layer1, (i * bg_width + scroll_layer1, 100 + scroll_layer1_y))
        for i in range(0, tiles):
            screen.blit(bg_layer2, (i * bg_width + scroll_layer2, 100 + scroll_layer2_y))

        scroll -= 1.5
        scroll_layer1 -= 2
        scroll_layer2 -= 4
        if abs(scroll) > bg_width:
            scroll = 0
        if abs(scroll_layer1) > bg_width:
            scroll_layer1 = 0
        if abs(scroll_layer2) > bg_width:
            scroll_layer2 = 0

        scroll_y += player.speed_y * parallax_factor_bg
        scroll_layer1_y += player.speed_y * parallax_factor_bg_layer1
        scroll_layer2_y += player.speed_y * parallax_factor_bg_layer2

        if pbar_current < PBAR_MAX:
            pbar_current += 1 * PBAR_SPD


        pbar_ratio = pbar_current / PBAR_MAX
        rect_len = PBAR_LEN * pbar_ratio


        screen.blit(scaled_image, (image_x, image_y))
        health_bar.draw(player.health)
        screen.blit(PGscaled_image, (PGimage_x, PGimage_y))

        # Update and draw the player
        player.update()
        player.draw()

        # Check for collisions between the player and asteroids
        collisions_player = pygame.sprite.spritecollide(player, asteroid_group, False, pygame.sprite.collide_circle)
        for asteroid in collisions_player:
            if not asteroid.destruction_animation:
                asteroid.start_destruction()  # Start the destruction animation
                hit_fx.play()  # Play the hit sound effect
                player.health -= 1  # Decrease player's health
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
            if not asteroid.destruction_animation:
              asteroid.start_destruction()
              score += 50 - asteroid.radius
              destroy_fx.play()

              if score // score_milestone > (score - 50) // score_milestone:
                  asteroid_spawn_delay = max(50, asteroid_spawn_delay -20)  # Decrease delay, but not below 50



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
        screen.blit(PGscaled_image, (PGimage_x, PGimage_y))
        pygame.draw.rect(screen, (0, 255, 0), (1200, 179.9, rect_len, 7))

    if not player.alive and not fall_sound_played:
       fall_fx.play()  # Play the fall sound effect
       fall_sound_played = True
       if player.alive:
           fall_sound_played = False

            # Player shooting
    if player.alive:
        if shoot:
            player.shoot()

    draw_text(screen, str(score), 75, screen_width / 2, 150)

    if not player.alive:
        game_over = True
        pygame.mixer.music.stop()


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