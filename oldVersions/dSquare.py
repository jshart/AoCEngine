import pygame
import random

# Constants
SIZE = 513  # 2^n + 1
RANGE = 100  # Initial random range for height values

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SIZE, SIZE))
pygame.display.set_caption("Diamond-Square Algorithm Terrain")

def diamond_square(arr, step_size, scale):
    half_step = step_size // 2
    
    # Diamond step
    for y in range(half_step, SIZE, step_size):
        for x in range(half_step, SIZE, step_size):
            avg = (arr[x - half_step][y - half_step] + arr[x - half_step][y + half_step] +
                   arr[x + half_step][y - half_step] + arr[x + half_step][y + half_step]) / 4.0
            arr[x][y] = avg + random.uniform(-scale, scale)
    
    # Square step
    for y in range(0, SIZE, half_step):
        for x in range((y + half_step) % step_size, SIZE, step_size):
            avg = (arr[(x - half_step) % SIZE][y] + arr[(x + half_step) % SIZE][y] +
                   arr[x][(y - half_step) % SIZE] + arr[x][(y + half_step) % SIZE]) / 4.0
            arr[x][y] = avg + random.uniform(-scale, scale)

def generate_terrain():
    terrain = [[0] * SIZE for _ in range(SIZE)]
    
    # Initialize corners
    terrain[0][0] = terrain[0][SIZE - 1] = terrain[SIZE - 1][0] = terrain[SIZE - 1][SIZE - 1] = random.uniform(0, RANGE)
    
    step_size = SIZE - 1
    scale = RANGE
    
    while step_size > 1:
        diamond_square(terrain, step_size, scale)
        step_size //= 2
        scale /= 2

    return terrain

terrain = generate_terrain()

# Run the game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Draw the terrain
    for y in range(SIZE):
        for x in range(SIZE):
            color = int(terrain[x][y])
            color = max(0, min(255, color))
            #print(color)
            if color<50:
                pygame.draw.rect(screen, (0, 0, 255-color), (x, y, 1, 1))
            else:
                pygame.draw.rect(screen, (0, 255-color,0), (x, y, 1, 1))


    pygame.display.flip()

pygame.quit()
