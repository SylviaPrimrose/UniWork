# ------------------------- Things to do ------------------------- 
# Add Restart - End screen should have clear (no player ship no invaders)

import pygame
import sys
from collections import deque
import random

# ------------------------- SCREEN SETUP -------------------------
pygame.init()
font = pygame.font.SysFont(None, 30)

# setting the screen size
SCREEN_HEIGHT = 500
SCREEN_WIDTH = 500

screen = pygame.display.set_mode([SCREEN_HEIGHT, SCREEN_WIDTH])

# tracking game time and setting frames per second
clock = pygame.time.Clock()
FPS = 60

# ------------------------- PLAYER SETUP -------------------------

# setting the player class, defining its x and y positions, image, the length and height,
# creating a rectangle to use for a hit box
class Player:
    def __init__(self, x, y, img, l, h):
        self.x = x
        self.y = y
        self.img = img
        self.l = l
        self.h = h
        self.img = pygame.transform.scale(img, (l,h))
        self.rect = self.img.get_rect(topleft=(self.x, self.y))

    def update(self):
        self.rect.topleft = (self.x, self.y)
# setting the player and loading the image
player = Player((SCREEN_WIDTH/2)-(35/2), (SCREEN_HEIGHT - 100), pygame.image.load("C:/Users/Amber/Downloads/space/playerShip.png"), 40, 35)
player_Xchange = 0
# Player lives system
player_hit = False
player_lives = 3
player_i_frames = 200
Player_last_hit_time = 0

# ------------------------- BULLET SETUP -------------------------

# The bullet class, setting its x and y positions, length and height,
# crating a rectangle to use for a hit box
class Bullet:
    def __init__(self, x, y, img, l, h):
        self.x = x
        self.y = y
        self.img = img
        self.l = l
        self.h = h
        self.img = pygame.transform.scale(img, (l,h))
        self.rect = self.img.get_rect(topleft=(self.x, self.y))
# loading the bullet image
bullet_img = pygame.image.load("C:/Users/Amber/Downloads/space/Bullet.png").convert_alpha()

# to check if bullet is fired (used in game loop)
fired = False

# Using a deque to set a cooldown for bullets
bullets = deque()
milli_sec_between_shots = 400
last_shot_time = 0

# function to fire a bullet, setting new bullets into a bullet list, setting their position
# as the players center position and above the player ship.
def fire_bullet():
    global last_shot_time
    last_shot_time = pygame.time.get_ticks()

    new_bullet = Bullet(
        player.x + player.l // 2 - 2,  # x
        player.y - 10,                 # y
        bullet_img,                    # img
        5, 5                           # width, height
    )
    bullets.append(new_bullet)

# -------------------- BARRIER SYSTEM --------------------

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((3, 3))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))


grid = [
    [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


class Obstacle:
    def __init__(self, x, y):
        self.blocks_group = pygame.sprite.Group()

        for row in range(len(grid)):
            for col in range(len(grid[row])):
                if grid[row][col] == 1:
                    bx = x + col * 3
                    by = y + row * 3
                    self.blocks_group.add(Block(bx, by))

obstacles = []
obstacles.append(Obstacle(60, 350))
obstacles.append(Obstacle(200, 350))
obstacles.append(Obstacle(340, 350))
                
# ------------------------- ENEMY SETUP -------------------------

# Alien
alien1_img = pygame.image.load("C:/Users/Amber/Downloads/space/alien1.png").convert_alpha()
alien1 = pygame.transform.scale(alien1_img, (32, 32))
# Flash Red
alien1_red = alien1.copy()
alien1_red.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)

# Alien 2
alien2_img = pygame.image.load("C:/Users/Amber/Downloads/space/alien2.png").convert_alpha()
alien2 = pygame.transform.scale(alien2_img, (32, 32))
# Flash Red 
alien2_red = alien2.copy()
alien2_red.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)

# Alien 3
alien3_img = pygame.image.load("C:/Users/Amber/Downloads/space/alien3.png").convert_alpha()
alien3 = pygame.transform.scale(alien3_img, (48, 48))  # boss a bit bigger
# Flash Red 
alien3_red = alien3.copy()
alien3_red.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)

current_wave = 1
wave2_state = None
wave2_direction = 1
wave2_step_timer = 0
wave3_speed = 1.0



class Invader:
    def __init__(self, x, y, img, health=2, flash_img=None):
        self.x = x
        self.y = y

        self.base_img = img
        self.flash_img = flash_img if flash_img is not None else img
        self.img = img

        self.health = health      
        self.rect = self.img.get_rect(topleft=(self.x, self.y))
        
        self.flash_hit_time = -1
        self.flash_duration = 100

    def update(self, current_time):
        # keep rect synced to x/y
        self.rect.topleft = (self.x, self.y)

        # if  hit, go red for flash_duration
        if self.flash_hit_time != -1:
            if current_time - self.flash_hit_time > self.flash_duration:
                self.img = self.base_img
                self.flash_hit_time = -1

class InvaderBullet:
    def __init__(self, x, y, l, h, double_damage=False, color=None):
        self.x = x
        self.y = y
        self.l = l
        self.h = h

        self.double_damage = double_damage

        if color is None:
            if double_damage:
                color = (255, 255, 255)    # white
            else:
                color = (255, 0, 0)        # red

        self.color = color
        self.rect = pygame.Rect(self.x, self.y, self.l, self.h)

    def update(self):
        self.y += 5
        self.rect.topleft = (self.x, self.y)



# Grid
invaders = []
cols = 1
rows = 1

alien_width = alien1.get_width()
alien_height = alien1.get_height()

x_margin = 40   # distance from left edge
y_margin = 40   # distance from top edge

x_spacing = alien_width + 10   # horizontal space between sprites
y_spacing = alien_height + 10  # vertical space between sprites

for row in range(rows):
    for col in range(cols):
        x = x_margin + col * x_spacing
        y = y_margin + row * y_spacing
        invaders.append(Invader(x, y, alien1, health=2, flash_img=alien1_red))


def get_invaders_by_row(invaders, rows, cols):
    rows_list = []
    for r in range(rows):
        row_start = r * cols
        row_end = row_start + cols
        rows_list.append(invaders[row_start:row_end])
    return rows_list

invader_rows = get_invaders_by_row(invaders, rows, cols)

# Movement
invader_direction = 1      # 1 = moving right, -1 = moving left
invader_speed = 20.0
invader_move_down = 20

current_row = 0
row_move_delay = 300     
last_row_move_time = pygame.time.get_ticks()

# Shooting
invader_bullets = deque()
invader_shot_cooldown = 800      
last_invader_shot_time = 0


def spawn_wave_2():
    global invaders, invader_direction, wave2_state, wave2_step_timer, wave2_direction, invader_speed

    invaders = []
    cols = 1
    rows = 1

    x_margin = 80
    y_margin = 40
    wave2_state = "down"
    wave2_direction = 1
    wave2_step_timer = pygame.time.get_ticks()
    invader_speed = 30

    for r in range(rows):
        for c in range(cols):
            x = x_margin + c * (alien_width + 20)
            y = y_margin + r * (alien_height + 20)
            invaders.append(Invader(x, y, alien2, health=4, flash_img=alien2_red))


    wave2_state = "down"  # down → side → up → repeat
    wave2_direction = 1   # 1 right, -1 left
    wave2_step_timer = pygame.time.get_ticks()

    invader_speed = 30

def spawn_wave_3():
    global invaders, current_wave

    invaders = []

    alien_w = alien3.get_width()
    boss_x = SCREEN_WIDTH // 2 - alien_w // 2
    boss_y = 40  # near the top

    invaders.append(Invader(boss_x, boss_y, alien3, health=20, flash_img=alien3_red))
    current_wave = 3


# ------------------------- GAME LOOP -------------------------
running = True
while running:
    # ---- EVENTS ----
    current_time = pygame.time.get_ticks()
    # closing the game window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        # ---- INPUT ----
        # setting input keys for moving left and right, and firing bullets
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player_Xchange = -5
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player_Xchange = 5
            elif event.key == pygame.K_SPACE:
                current_time = pygame.time.get_ticks()
                # only allow firing if enough time passed
                if current_time > last_shot_time + milli_sec_between_shots:
                    fire_bullet()
            

                
            elif event.key == pygame.K_ESCAPE == pygame.WINDOWCLOSE:
                running = False
        # stopping player movement when keys are released
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a or event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player_Xchange = 0
    # updating player position while input keys are held down
    player.x += player_Xchange
    player.update()


    # ---- LIVES ----
    # setting the background colour to black
    screen.fill([0,0,0])
    # draw text for lives
    lives_surface = font.render(f"Lives: {player_lives}", True, (255, 255, 255))
    screen.blit(lives_surface, (10, 10))

    # ---- DRAW PLAYER + BULLETS ----
    # drawing the player onto the screen
    screen.blit(player.img, (player.x, player.y))
    # for each bullet in the bullet list, move the bullet up, and draw it to the screen
    for a_bullet in list(bullets):
        a_bullet.y -= 9
        a_bullet.rect.topleft = (a_bullet.x, a_bullet.y)

        if a_bullet.y <= 0:
            bullets.remove(a_bullet)
            continue

        
        # bullet hits barrier
        for obs in obstacles:
            for block in list(obs.blocks_group):
                if a_bullet.rect.colliderect(block.rect):
                    obs.blocks_group.remove(block)
                    bullets.remove(a_bullet)
                    break

        # collision with invaders
        for inv in list(invaders):
            if a_bullet.rect.colliderect(inv.rect):
                inv.health -= 1

                # Show Damage
                inv.flash_hit_time = current_time
                inv.img = inv.flash_img

                if a_bullet in bullets:
                    bullets.remove(a_bullet)

                if inv.health <= 0:
                    invaders.remove(inv)

                    # Increase Speed
                    invader_speed += 0.5

                break

        if a_bullet in bullets:
            screen.blit(a_bullet.img, a_bullet.rect)


    # ------------------------- ENEMY AI -------------------------

    # ---- random invader shooting ----
    if invaders and current_time > last_invader_shot_time + invader_shot_cooldown:
        if random.random() < 0.2:  # 30% to shoot
            shooter = random.choice(invaders)
            new_ib = InvaderBullet(
                shooter.x + alien_width // 2 - 2,
                shooter.y + alien_height,
                4,
                10
            )
            invader_bullets.append(new_ib)
            last_invader_shot_time = current_time


    for bullet in list(invader_bullets):
        bullet.update()
        if bullet.y > SCREEN_HEIGHT:
            invader_bullets.remove(bullet)
            
    if current_wave == 2 and invaders:
        if current_time > last_invader_shot_time + 500: 
            shooter = random.choice(invaders)

            if random.random() < 0.30:
                # big white double bullet
                new_bullet = InvaderBullet(
                    shooter.x + alien_width // 2 - 2,
                    shooter.y + alien_height,
                    6, 14,
                    double_damage=True,
                    color=(255, 255, 255)
                )
            else:
                # normal red bullet
                new_bullet = InvaderBullet(
                    shooter.x + alien_width // 2 - 2,
                    shooter.y + alien_height,
                    4, 10,
                    double_damage=False,
                    color=(255, 0, 0)
                )

            invader_bullets.append(new_bullet)
            last_invader_shot_time = current_time


    # ---- Wave 1 Movement ----
    if current_wave == 1 and current_time - last_row_move_time > row_move_delay and invader_rows:
        moving_row = invader_rows[current_row]

        # Move that row sideways
        for inv in moving_row:
            inv.x += invader_direction * invader_speed

        # Check if ANY invader in that row touches the screen edge
        hit_edge = any(
            inv.x <= 0 or inv.x + inv.img.get_width() >= SCREEN_WIDTH
            for inv in moving_row
        )

        if hit_edge:
            invader_direction *= -1

            for row in invader_rows:
                for inv in row:
                    inv.y += invader_move_down

        current_row = (current_row + 1) % len(invader_rows)
        last_row_move_time = current_time

    # ---- Wave 2 Movement ----
    if current_wave == 2:
        now = current_time
        wave2_delay = 200  

        if now - wave2_step_timer > wave2_delay and invaders:
            wave2_step_timer = now

            if wave2_state == "down":
                for inv in invaders:
                    inv.y += 10
                wave2_state = "side"

            elif wave2_state == "side":
                hit_edge = False
                for inv in invaders:
                    inv.x += wave2_direction * invader_speed
                    if inv.x <= 0 or inv.x + alien_width >= SCREEN_WIDTH:
                        hit_edge = True

                if hit_edge:
                    wave2_direction *= -1
                    for inv in invaders:
                        inv.y += 20  # move down 2 instead of 1
                wave2_state = "up"

            elif wave2_state == "up":
                for inv in invaders:
                    inv.y -= 10
                wave2_state = "down"
    
    # ---- Wave 3 Movement ----
    if current_wave == 3 and invaders:
        final_invader = invaders[0]  

        final_invader.y += wave3_speed

        # Stop going below the barriers
        remaining_barriers = [obs for obs in obstacles if len(obs.blocks_group) > 0]

        if remaining_barriers:
            # top of the barriers = smallest block.y from any remaining barrier
            barrier_top = min(
                block.rect.top
                for obs in remaining_barriers
                for block in obs.blocks_group
            )

            if final_invader.y + final_invader.img.get_height() >= barrier_top:
                final_invader.y = barrier_top - final_invader.img.get_height()
                # remove ONE whole barrier
                obs_to_remove = remaining_barriers[0]
                obstacles.remove(obs_to_remove)

                # reset alien back to the top
                final_invader.y = 40
        else:
            # no barriers left = Loose
            bottom_limit = SCREEN_HEIGHT - 50
            if final_invader.y + final_invader.img.get_height() >= bottom_limit:
                final_invader.y = bottom_limit - final_invader.img.get_height()



    # ---- Draw ----
    # Draw invaders
    for inv in invaders:
        inv.update(current_time)
        screen.blit(inv.img, (inv.x, inv.y))

    
    # Draw Barriers
    for obs in obstacles:
        obs.blocks_group.draw(screen)

    # Draw bullets 
    for bullet in invader_bullets:
        pygame.draw.rect(screen, bullet.color, bullet.rect)

    
    # --- Wave Transition ---
    if current_wave == 1 and len(invaders) == 0:
        current_wave = 2
        spawn_wave_2()

    elif current_wave == 2 and len(invaders) == 0:
        spawn_wave_3()

    pygame.display.flip()

    # ------------------------- ENEMY AI END -------------------------
    
    for bullet in list(invader_bullets):
        bullet.update()

    # Enemy bullet hits barrier
        for obs in obstacles:
            for block in list(obs.blocks_group):
                if bullet.rect.colliderect(block.rect):
                    obs.blocks_group.remove(block)
                    invader_bullets.remove(bullet)
                    break
    
    for inv in list(invaders):
        if inv.rect.colliderect(player.rect):
            player_lives -= 3

    # If an invader bullet hits the player, lose 1 life
    for ib in list(invader_bullets):
        if ib.rect.colliderect(player.rect) and not player_hit:
            player_hit = True        
            player_lives -= 1

            # reset player position
            player.x = (SCREEN_WIDTH / 2) - (35 / 2)
            player.update() 
            Player_last_hit_time = pygame.time.get_ticks()
            invader_bullets.remove(ib)

    if player_hit and current_time > Player_last_hit_time + player_i_frames:
        player_hit = False

    if player_lives <= 0:
            player_Xchange = 0
            game_over_surface = font.render("Game Over", True, (255, 0, 0))
            screen.blit(game_over_surface, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2))
        
    pygame.display.flip()

    clock.tick(FPS)
    # lock the player within the screen bounds
    if player.x <= 16:
        player.x = 16
    elif player.x >= 450:
        player.x = 450
    

sys.exit(0)
