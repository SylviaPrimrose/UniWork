import pygame, sys
# Initialize Pygame
pygame.init()

SCREEN_WIDTH = 750
SCREEN_HEIGHT = 700



screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Barriers test")

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    #drawing code here
    screen.fill((0, 0, 0))  # Clear screen with black
        # Draw barriers
    for obstacle in game.obstacles:
        obstacle.blocks_group.draw(screen)

    pygame.display.update()
    clock.tick(60)