import pygame

FONT_PATH = 'src/pygrain/Vogue.ttf'


def show_text(screen, text, x, y, font_colour=(0, 0, 0),
              font_bg=(255, 255, 255), font_size=10, center=True):
    # initialises font for displaying text
    try:
        for line in text.split('\n'):
            basic_font = pygame.font.Font(FONT_PATH, font_size)
            text = basic_font.render(text, True, font_colour, font_bg)
            text_rect = text.get_rect()
            if center:
                text_rect.center = x, y
            else:
                text_rect.x, text_rect.y = x, y
            screen.blit(text, text_rect)  # Shows text on self.screen
    finally:
        pass


def get_text_size(text, font_colour=(0, 0, 0), font_bg=(255, 255, 255),
                  font_size=10):
    # initialises font for displaying text
    try:
        for line in text.split('\n'):
            basic_font = pygame.font.Font(FONT_PATH, font_size)
            text = basic_font.render(text, True, font_colour, font_bg)
            rect = text.get_rect()
            return rect.width, rect.height
    finally:
        pass

def show_image(screen, path, x, y):
    image = pygame.image.load(path).convert()
    screen.blit(image, (x, y))
