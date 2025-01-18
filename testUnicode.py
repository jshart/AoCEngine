import pygame
import random
import time

# List of some random emoji characters
emojis = ["😀", "😂", "🥰", "😎", "🤔", "😅", "🙌", "👏", "👍", "🤝", "🎉", "✨", "❤️", "🌟", "🔥", "🍀"]

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 500, 500
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Animated Emoji Grid')

# Define colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Load the emoji font
emoji_font_path = "C:/Windows/Fonts/seguiemj.ttf"  # Replace with the path to your emoji font file
font_size = 20
#font = pygame.font.Font(emoji_font_path, font_size)
font = pygame.font.SysFont('Segoe UI Emoji', font_size)

# Generate a 50x50 array of random emojis
def generate_random_emojis(size=25):
    return [[random.choice(emojis) for _ in range(size)] for _ in range(size)]

emoji_grid = generate_random_emojis()
cell_size = 20

def draw_emoji_grid(window, emoji_grid, highlight_pos=None):
    window.fill(WHITE)  # Clear screen with white background
    for i, row in enumerate(emoji_grid):
        for j, emoji in enumerate(row):
            x, y = j * cell_size, i * cell_size
            color = RED if highlight_pos == (i, j) else BLACK
            print("Rendering:",emoji)
            text_surface = font.render(emoji, True, color)
            window.blit(text_surface, (x, y))

# Main loop
running = True
animate = False
current_pos = (0, 0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                animate = not animate  # Toggle animation
            elif event.key == pygame.K_q:
                running = False  # Quit on 'q' key press

    if animate:
        draw_emoji_grid(window, emoji_grid, highlight_pos=current_pos)
        pygame.display.flip()
        pygame.time.delay(50)  # Delay for animation effect
        
        # Update position for the next character
        i, j = current_pos
        j += 1
        if j >= len(emoji_grid[i]):
            j = 0
            i += 1
            if i >= len(emoji_grid):
                i = 0
        current_pos = (i, j)
    else:
        draw_emoji_grid(window, emoji_grid)
        pygame.display.flip()

pygame.quit()
