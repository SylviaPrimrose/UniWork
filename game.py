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
# ------------------------- SCREEN SETUP -------------------------

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



# Hit boxes
player.rect = pygame.Rect(player.x, player.y, player.l, player.h)
player_hitbox = player.rect


# ------------------------- SCREEN SETUP -------------------------
SCREEN_HEIGHT = 500
SCREEN_WIDTH = 500

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("Invader Test")

clock = pygame.time.Clock()
FPS = 60
                
# ------------------------- ENEMY START -------------------------

alien1_img = pygame.image.load(r"C:/Users/Amber/Downloads/space/alien1.png").convert_alpha()
alien1 = pygame.transform.scale(alien1_img, (32, 32))

class Invader:
    def __init__(self, x, y, img, health=2):
        self.x = x
        self.y = y
        self.img = img
        self.health = health      
        self.rect = self.img.get_rect(topleft=(self.x, self.y))

    def update(self):
        self.rect.topleft = (self.x, self.y)



class InvaderBullet:
    def __init__(self, x, y, l, h):
        self.x = x
        self.y = y
        self.l = l
        self.h = h
        self.rect = pygame.Rect(self.x, self.y, self.l, self.h)

    def update(self):
        self.y += 5
        self.rect.topleft = (self.x, self.y)


# Grid
invaders = []

cols = 6
rows = 6

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
        invaders.append(Invader(x, y, alien1, health=2))



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


# ------------------------- ENEMY END -------------------------

# game loop
running = True
while running:
    # ------------------------- EVENTS --------
    current_time = pygame.time.get_ticks()
    # closing the game window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.display.quit()
            pygame.quit()
            sys.exit()
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


    # setting the background colour to black
    screen.fill([0,0,0])
    # draw text for lives
    lives_surface = font.render(f"Lives: {player_lives}", True, (255, 255, 255))
    screen.blit(lives_surface, (10, 10))

    # drawing the player onto the screen
    screen.blit(player.img, (player.x, player.y))
    # for each bullet in the bullet list, move the bullet up, and draw it to the screen
    for a_bullet in list(bullets):
        a_bullet.y -= 9
        a_bullet.rect.topleft = (a_bullet.x, a_bullet.y)

        if a_bullet.y <= 0:
            bullets.remove(a_bullet)
            continue

        # collision with invaders
        for inv in list(invaders):
            if a_bullet.rect.colliderect(inv.rect):
                inv.health -= 1

                if a_bullet in bullets:
                    bullets.remove(a_bullet)

                if inv.health <= 0:
                    invaders.remove(inv)
                break

        if a_bullet in bullets:
            screen.blit(a_bullet.img, a_bullet.rect)


        
    
    # ------------------------- ENEMY START -------------------------
    # Move Row
    if current_time - last_row_move_time > row_move_delay and invader_rows:
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

    # ---- random invader shooting ----
    if invaders and current_time > last_invader_shot_time + invader_shot_cooldown:
        if random.random() < 0.3:  # 30% to shoot
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

    # Draw invaders
    for inv in invaders:
        inv.update()
        screen.blit(inv.img, (inv.x, inv.y))

    # Draw bullets 
    for bullet in invader_bullets:
        pygame.draw.rect(screen, (255, 0, 0), bullet.rect)

    pygame.display.flip()

    # ------------------------- END -------------------------

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
