import pygame
import pygame.freetype

# Initialize Pygame and FreeType
pygame.init()
pygame.freetype.init()

# Screen setup
screen = pygame.display.set_mode((400, 200))
pygame.display.set_caption("Pygame FreeType Example")

# Set up font
font = pygame.freetype.SysFont("Segoe UI Emoji", 24)  # You can use other fonts and sizes

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Emoji text
emoji_text = "😊"
text_to_display = "Hello, Pygame!"

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with white
    screen.fill(WHITE)

    # Render text and emoji
    font.render_to(screen, (50, 50), emoji_text, BLACK)
    font.render_to(screen, (100, 50), text_to_display, BLACK)

    # Change font size and render text
    font.size = 36
    font.render_to(screen, (50, 100), "Big Text", BLACK)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
