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

def reset_player_for_new_wave():
    global player_lives, player_hit, player_Xchange, bullets, invader_bullets

    # Reset lives & hit state
    player_lives = 3
    player_hit = False
    player_Xchange = 0

    # Clear bullets
    bullets.clear()
    invader_bullets.clear()

    # Reset player position
    player.x = (SCREEN_WIDTH / 2) - (player.l / 2)
    player.y = SCREEN_HEIGHT - 100
    player.update()


def load_alien_frames(prefix, frame_count, size):
    frames = []
    for i in range(1, frame_count + 1):
        img = pygame.image.load(f"{prefix}{i}.png").convert_alpha()
        img = pygame.transform.scale(img, size)
        frames.append(img)
    return frames

# 4-frame animations for each alien type
alien1_frames = load_alien_frames("C:/Users/Amber/Downloads/space/alien1_", 4, (32, 32))
alien2_frames = load_alien_frames("C:/Users/Amber/Downloads/space/alien2_", 4, (32, 32))
alien3_frames = load_alien_frames("C:/Users/Amber/Downloads/space/alien3_", 4, (48, 48))  

# Red flash versions of each frame
def make_red_frames(frames):
    red_frames = []
    for frame in frames:
        red = frame.copy()
        red.fill((255, 0, 0), special_flags=pygame.BLEND_MULT)
        red_frames.append(red)
    return red_frames

alien1_frames_red = make_red_frames(alien1_frames)
alien2_frames_red = make_red_frames(alien2_frames)
alien3_frames_red = make_red_frames(alien3_frames)


current_wave = 1
wave2_state = None
wave2_direction = 1
wave2_step_timer = 0
wave3_speed = 1.0

game_state = "playing"      # "playing", "game_over", "win"
final_wave_reached = 1      # to display on lose screen

lose_try_rect = None
lose_quit_rect = None
win_restart_rect = None
win_quit_rect = None




class Invader:
    def __init__(self, x, y, frames, health=2, flash_frames=None, anim_speed=150):
        self.x = x
        self.y = y

        # Animation frames
        self.frames = frames                    # normal frames
        self.flash_frames = flash_frames or frames  # red flash frames
        self.current_frame_index = 0
        self.last_anim_time = 0
        self.anim_speed = anim_speed            

        self.img = self.frames[0]
        self.rect = self.img.get_rect(topleft=(self.x, self.y))

        self.health = health      

        # Flash damage effect
        self.flash_hit_time = -1
        self.flash_duration = 100  #

    def update(self, current_time):
        # Animate
        if current_time - self.last_anim_time > self.anim_speed:
            self.last_anim_time = current_time
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            
        flashing = (
            self.flash_hit_time != -1 and
            (current_time - self.flash_hit_time) <= self.flash_duration
        )

        frame_list = self.flash_frames if flashing else self.frames
        self.img = frame_list[self.current_frame_index]

        # Keep rect synced
        self.rect = self.img.get_rect(topleft=(self.x, self.y))

        # Stop flashing 
        if flashing is False and self.flash_hit_time != -1:
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
cols = 5
rows = 4

alien_width = alien1_frames[0].get_width()
alien_height = alien1_frames[0].get_height()

x_margin = 40   # distance from left edge
y_margin = 40   # distance from top edge

x_spacing = alien_width + 10   # horizontal space between sprites
y_spacing = alien_height + 10  # vertical space between sprites

for row in range(rows):
    for col in range(cols):
        x = x_margin + col * x_spacing
        y = y_margin + row * y_spacing
        invaders.append(
            Invader(
                x, y,
                alien1_frames,
                health=2,
                flash_frames=alien1_frames_red
            )
        )


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
    cols = 5
    rows = 4 

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
            invaders.append(
                Invader(
                    x, y,
                    alien2_frames,
                    health=4,
                    flash_frames=alien2_frames_red
                )
            )



    wave2_state = "down"  # down → side → up → repeat
    wave2_direction = 1   # 1 right, -1 left
    wave2_step_timer = pygame.time.get_ticks()

    invader_speed = 30

def spawn_wave_3():
    global invaders, current_wave

    invaders = []

    alien_w = alien3_frames[0].get_width()
    boss_x = SCREEN_WIDTH // 2 - alien_w // 2
    boss_y = 40  # near the top

    invaders.append(
        Invader(
            boss_x, boss_y,
            alien3_frames,
            health=20,
            flash_frames=alien3_frames_red
        )
    )
    current_wave = 3


def get_barrier_info():
    # Take current barrier info so it can be removed by waves
    remaining = [obs for obs in obstacles if len(obs.blocks_group) > 0]
    if not remaining:
        return None, remaining

    barrier_top = min(
        block.rect.top
        for obs in remaining
        for block in obs.blocks_group
    )
    return barrier_top, remaining

def reset_full_game():
    global player, player_Xchange, player_lives, player_hit, bullets, invader_bullets
    global obstacles, invaders, invader_rows, current_wave
    global invader_direction, invader_speed, current_row, last_row_move_time
    global wave2_state, wave2_direction, wave2_step_timer, wave3_speed

    # Reset player
    player.x = (SCREEN_WIDTH / 2) - (player.l / 2)
    player.y = SCREEN_HEIGHT - 100
    player.update()
    player_Xchange = 0
    player_lives = 3
    player_hit = False
    bullets.clear()
    invader_bullets.clear()

    # Reset barriers
    obstacles = []
    obstacles.append(Obstacle(60, 350))
    obstacles.append(Obstacle(200, 350))
    obstacles.append(Obstacle(340, 350))

    # Reset wave 1 invaders
    invaders.clear()
    cols = 6
    rows = 5

    for row in range(rows):
        for col in range(cols):
            x = x_margin + col * x_spacing
            y = y_margin + row * y_spacing
            invaders.append(
                Invader(
                    x, y,
                    alien1_frames,
                    health=2,
                    flash_frames=alien1_frames_red
                )
            )

    invader_rows = get_invaders_by_row(invaders, rows, cols)

    # Reset movement / wave stuff
    current_wave = 1
    invader_direction = 1
    invader_speed = 20.0
    current_row = 0
    last_row_move_time = pygame.time.get_ticks()

    wave2_state = None
    wave2_direction = 1
    wave2_step_timer = 0
    wave3_speed = 1.0


# ------------------------- GAME LOOP -------------------------
running = True
while running:
    current_time = pygame.time.get_ticks()

    # ---- EVENTS ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.display.quit()
            pygame.quit()
            sys.exit()

        # ESC to quit anytime
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if game_state == "playing":
            # controls only when playing
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player_Xchange = -5
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player_Xchange = 5
                elif event.key == pygame.K_SPACE:
                    current_time = pygame.time.get_ticks()
                    if current_time > last_shot_time + milli_sec_between_shots:
                        fire_bullet()

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
                    player_Xchange = 0

        elif game_state in ("game_over", "win"):
            # Clickable menu options
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if game_state == "game_over":
                    if lose_try_rect and lose_try_rect.collidepoint(mx, my):
                        reset_full_game()
                        game_state = "playing"
                    elif lose_quit_rect and lose_quit_rect.collidepoint(mx, my):
                        running = False

                elif game_state == "win":
                    if win_restart_rect and win_restart_rect.collidepoint(mx, my):
                        reset_full_game()
                        game_state = "playing"
                    elif win_quit_rect and win_quit_rect.collidepoint(mx, my):
                        running = False

    # ---------------- PLAYING STATE ----------------
    if game_state == "playing":
        # update player position
        player.x += player_Xchange
        player.update()

        # lock the player within the screen bounds
        if player.x <= 16:
            player.x = 16
        elif player.x >= 450:
            player.x = 450

        # clear screen
        screen.fill([0, 0, 0])

        # HUD
        wave_surface = font.render(f"Wave: {current_wave}/3", True, (255, 255, 255))
        screen.blit(wave_surface, (10, 10))
        lives_surface = font.render(f"Lives: {player_lives}", True, (255, 255, 255))
        screen.blit(lives_surface, (10, 30))

        # draw player
        screen.blit(player.img, (player.x, player.y))

        # ---- PLAYER BULLETS ----
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
                    inv.flash_hit_time = current_time

                    if a_bullet in bullets:
                        bullets.remove(a_bullet)

                    if inv.health <= 0:
                        invaders.remove(inv)
                        invader_speed += 0.5
                    break

            if a_bullet in bullets:
                screen.blit(a_bullet.img, a_bullet.rect)

        # ---- INVADER SHOOTING ----
        if invaders and current_time > last_invader_shot_time + invader_shot_cooldown:
            if random.random() < 0.2:
                shooter = random.choice(invaders)
                bullet_x = shooter.rect.centerx - 2
                bullet_y = shooter.rect.bottom
                new_ib = InvaderBullet(bullet_x, bullet_y, 4, 10)
                invader_bullets.append(new_ib)
                last_invader_shot_time = current_time

        for bullet in list(invader_bullets):
            bullet.update()
            if bullet.y > SCREEN_HEIGHT:
                invader_bullets.remove(bullet)

        # Extra wave 2 bullets
        if current_wave == 2 and invaders:
            if current_time > last_invader_shot_time + 500:
                shooter = random.choice(invaders)
                bullet_x = shooter.rect.centerx - 3
                bullet_y = shooter.rect.bottom

                if random.random() < 0.30:
                    new_bullet = InvaderBullet(
                        bullet_x,
                        bullet_y,
                        6, 14,
                        double_damage=True,
                        color=(255, 255, 255)
                    )
                else:
                    new_bullet = InvaderBullet(
                        bullet_x + 1,
                        bullet_y,
                        4, 10,
                        double_damage=False,
                        color=(255, 0, 0)
                    )

                invader_bullets.append(new_bullet)
                last_invader_shot_time = current_time

        # ---- WAVE 1 MOVEMENT ----
        if current_wave == 1 and current_time - last_row_move_time > row_move_delay and invader_rows:
            moving_row = invader_rows[current_row]

            for inv in moving_row:
                inv.x += invader_direction * invader_speed

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

        # ---- WAVE 2 MOVEMENT ----
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
                            inv.y += 20
                    wave2_state = "up"

                elif wave2_state == "up":
                    for inv in invaders:
                        inv.y -= 10
                    wave2_state = "down"

        # ---- WAVE 3 MOVEMENT ----
        if current_wave == 3 and invaders:
            final_invader = invaders[0]
            final_invader.y += wave3_speed

            barrier_top, remaining_barriers = get_barrier_info()

            if remaining_barriers:
                if final_invader.y + final_invader.img.get_height() >= barrier_top:
                    final_invader.y = barrier_top - final_invader.img.get_height()
                    obs_to_remove = remaining_barriers[0]
                    obstacles.remove(obs_to_remove)
                    final_invader.y = 40
            else:
                bottom_limit = SCREEN_HEIGHT - 50
                if final_invader.y + final_invader.img.get_height() >= bottom_limit:
                    final_invader.y = bottom_limit - final_invader.img.get_height()
                    final_wave_reached = current_wave
                    game_state = "game_over"

        # ---- Barrier contact destroys a barrier AND that whole row ----
        if current_wave in (1, 2) and invaders:
            barrier_top, remaining_barriers = get_barrier_info()

            if barrier_top is not None and remaining_barriers:
                for inv in list(invaders):
                    if inv.y + inv.img.get_height() >= barrier_top:
                        obs_to_remove = remaining_barriers[0]
                        obstacles.remove(obs_to_remove)

                        row_y = inv.rect.centery
                        same_row_invaders = [
                            e for e in invaders
                            if abs(e.rect.centery - row_y) < 5
                        ]

                        for e in same_row_invaders:
                            if e in invaders:
                                invaders.remove(e)
                        break

        # ---- DRAW INVADERS & BARRIERS ----
        for inv in invaders:
            inv.update(current_time)
            screen.blit(inv.img, (inv.x, inv.y))

        for obs in obstacles:
            obs.blocks_group.draw(screen)

        for bullet in invader_bullets:
            pygame.draw.rect(screen, bullet.color, bullet.rect)

        # --- Wave Transition (with win) ---
        if current_wave == 1 and len(invaders) == 0:
            reset_player_for_new_wave()
            current_wave = 2
            spawn_wave_2()

        elif current_wave == 2 and len(invaders) == 0:
            reset_player_for_new_wave()
            spawn_wave_3()

        elif current_wave == 3 and len(invaders) == 0:
            game_state = "win"

        # ------------------------- ENEMY AI END -------------------------
        # Second bullet update + collisions
        for bullet in list(invader_bullets):
            bullet.update()

            # Enemy bullet hits barrier
            for obs in obstacles:
                for block in list(obs.blocks_group):
                    if bullet.rect.colliderect(block.rect):
                        obs.blocks_group.remove(block)
                        invader_bullets.remove(bullet)
                        break

        # Invader collides with player
        for inv in list(invaders):
            if inv.rect.colliderect(player.rect):
                player_lives -= 3

        # Invader bullets hit player
        for ib in list(invader_bullets):
            if ib.rect.colliderect(player.rect) and not player_hit:
                player_hit = True
                player_lives -= 1
                player.x = (SCREEN_WIDTH / 2) - (35 / 2)
                player.update()
                Player_last_hit_time = pygame.time.get_ticks()
                invader_bullets.remove(ib)

        if player_hit and current_time > Player_last_hit_time + player_i_frames:
            player_hit = False

        # Health-based lose → go to lose screen
        if player_lives <= 0 and game_state == "playing":
            final_wave_reached = current_wave
            game_state = "game_over"

        pygame.display.flip()

    # ---------------- LOOSE SCREEN ----------------
    elif game_state == "game_over":
        screen.fill((0, 0, 0))

        title = font.render("You loose!", True, (255, 0, 0))
        wave_text = font.render(f"Wave {final_wave_reached}/3", True, (255, 255, 255))
        prompt = font.render("Try again?", True, (255, 255, 255))
        opt1 = font.render("1. Try Again", True, (255, 255, 255))
        opt2 = font.render("2. Quit", True, (255, 255, 255))

        center_x = SCREEN_WIDTH // 2
        y = SCREEN_HEIGHT // 2 - 60

        title_rect = title.get_rect(center=(center_x, y))
        wave_rect = wave_text.get_rect(center=(center_x, y + 30))
        prompt_rect = prompt.get_rect(center=(center_x, y + 60))

        lose_try_rect = opt1.get_rect(center=(center_x, y + 100))
        lose_quit_rect = opt2.get_rect(center=(center_x, y + 140))

        # actually draw everything
        screen.blit(title, title_rect)
        screen.blit(wave_text, wave_rect)
        screen.blit(prompt, prompt_rect)
        screen.blit(opt1, lose_try_rect)
        screen.blit(opt2, lose_quit_rect)

        pygame.display.flip()



    # ---------------- WIN SCREEN ----------------
    elif game_state == "win":
        screen.fill((0, 0, 0))

        title = font.render("You Win!", True, (0, 255, 0))
        line2 = font.render("Congrats on defeating the boss!", True, (255, 255, 255))
        prompt = font.render("Restart?", True, (255, 255, 255))
        opt1 = font.render("1. Restart", True, (255, 255, 255))
        opt2 = font.render("2. Quit", True, (255, 255, 255))

        center_x = SCREEN_WIDTH // 2
        y = SCREEN_HEIGHT // 2 - 60

        title_rect = title.get_rect(center=(center_x, y))
        line2_rect = line2.get_rect(center=(center_x, y + 30))
        prompt_rect = prompt.get_rect(center=(center_x, y + 60))

        win_restart_rect = opt1.get_rect(center=(center_x, y + 100))
        win_quit_rect = opt2.get_rect(center=(center_x, y + 140))

        # draw text
        screen.blit(title, title_rect)
        screen.blit(line2, line2_rect)
        screen.blit(prompt, prompt_rect)
        screen.blit(opt1, win_restart_rect)
        screen.blit(opt2, win_quit_rect)

        pygame.display.flip()



    clock.tick(FPS)

sys.exit(0)
