import pygame


# Initialize Pygame
pygame.init()
screen.fill((255, 255, 255))
# Set up the window
window_size = (400, 300)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Number Display')

# Set up fonts
font = pygame.font.Font(None, 74)
text = font.render('10', True, (255, 255, 255))

button_font = pygame.font.Font(None, 36)
button_text = button_font.render('Start', True, (255, 255, 255))
button_rect = button_text.get_rect(center=(200, 200))

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Fill the background
    screen.fill((0, 0, 0))

    # Draw the text
    screen.blit(text, (150, 100))

    # Update the display
    pygame.display.flip()