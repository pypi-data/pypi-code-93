import json
import pygame
pygame.init()


# Config extraction
config = {'FULL SCREEN': True}
CONFIG_FILE = 'tortilla/config.json'
try:
    with open(CONFIG_FILE) as f:
        _config = json.load(f)
except FileNotFoundError:
    _config = {'FULL SCREEN': False}
for k, v in config.items():
    config[k] = _config[k]


FULL_SCREEN = config['FULL SCREEN']

if config['FULL SCREEN']:
    SCREEN_WIDTH = round(pygame.display.Info().current_w)
    SCREEN_HEIGHT = round(pygame.display.Info().current_h)
else:
    SCREEN_WIDTH = round(pygame.display.Info().current_w * 0.75)
    SCREEN_HEIGHT = round(pygame.display.Info().current_h * 0.75)

SCALE_FACTOR = SCREEN_WIDTH / 1920

# print(SCREEN_WIDTH, SCREEN_HEIGHT)

# SCREEN_WIDTH = pygame.display.Info().current_w
# SCREEN_HEIGHT = pygame.display.Info().current_h

# Colors
BLACK = 0, 0, 0
WHITE = 255, 255, 255
BLUE = 33, 150, 243
LIGHT_BLUE = 0, 191, 255
PURPLE = 41, 15, 53
LIGHT_PURPLE = 113, 41, 139
GREY = 204, 204, 204
MINT_CREAM = 245, 255, 250

# Fonts
# FONT_BOLD = 'sprites/fonts/OpenSans-SemiBold.ttf'

try:
    FONT_BOLD = 'tortilla/assets/fonts/DisposableDroidBB.ttf'
    FONT_REG = 'tortilla/assets/fonts/OpenSans-Regular.ttf'
    FONT_LIGHT = 'tortilla/assets/fonts/OpenSans-Light.ttf'
except FileNotFoundError:
    FONT_BOLD = 'arial'
    FONT_REG = 'arial'
    FONT_LIGHT = 'arial'

# Texts
MENU_TEXT = pygame.font.Font(FONT_LIGHT, round(110 / 1080 * SCREEN_HEIGHT))
LARGE_TEXT = pygame.font.Font(FONT_REG, round(40 / 1080 * SCREEN_HEIGHT))
MEDIUM_TEXT = pygame.font.Font(FONT_LIGHT, round(35 / 1440 * SCREEN_HEIGHT))
# SMALL_TEXT = pygame.font.Font(FONT_BOLD, int(25 / 1440 * SCREEN_HEIGHT))
SMALL_TEXT = pygame.font.Font(FONT_BOLD, round(35 / 1080 * SCREEN_HEIGHT))
HUD_TEXT = pygame.font.Font(FONT_REG, round(40 / 1440 * SCREEN_HEIGHT))
