import pygame
import noise
import random

# Constants
WIDTH, HEIGHT = 800, 800
SCALE = 200  # Increased scale for larger features
OCTAVES = 4  # Reduced octaves for less noise
PERSISTENCE = 0.3  # Lower persistence for smoother terrain
LACUNARITY = 2.0
BASE = random.randint(0, 100)  # Single base value for the whole image

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Perlin Noise Terrain")

def generate_terrain():
    terrain = [[0] * WIDTH for _ in range(HEIGHT)]
    
    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Scale coordinates to match Perlin noise
            nx = x / SCALE
            ny = y / SCALE
            # Generate Perlin noise value
            height_value = noise.pnoise2(nx, ny, octaves=OCTAVES, persistence=PERSISTENCE, lacunarity=LACUNARITY, repeatx=WIDTH, repeaty=HEIGHT, base=BASE)
            # Map noise value to 0-255 for color
            terrain[y][x] = int((height_value + 1) * 128)
    
    return terrain

terrain = generate_terrain()

# Run the game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Draw the terrain
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = terrain[y][x]
            if color<100:
                pygame.draw.rect(screen, (0, 0, color*2), (x, y, 1, 1))
            elif color<105:
                # draw beach (yellow)
                pygame.draw.rect(screen, (255, 255, 0), (x, y, 1, 1))
            elif color<180:
                pygame.draw.rect(screen, (0, 255-color,0), (x, y, 1, 1))
            else:
                pygame.draw.rect(screen, (color, color, color), (x, y, 1, 1))
            # pygame.draw.rect(screen, (color, color, color), (x, y, 1, 1))
    
    pygame.display.flip()

pygame.quit()
