def start_game():
    import os
    import platform
    import sys
    import pygame
    from pygame import K_F4, K_RALT, K_LALT, QUIT, KEYDOWN, K_a, K_LEFT, K_RIGHT, K_UP, K_DOWN, K_ESCAPE, K_v, K_SPACE
    from tortilla.controller import Controller
    from tortilla.actions_capturer import ActionsCapturer
    from tortilla.constants import FULL_SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT

    # Initialization
    if platform.system() == 'Windows':
        from ctypes import windll
        windll.user32.SetProcessDPIAware()
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # center display
    pygame.init()
    clock = pygame.time.Clock()

    # FULL_SCREEN = False

    # Screen
    if FULL_SCREEN:
        SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Preparation
    actions_capturer = ActionsCapturer()
    controller = Controller(SCREEN)

    # Main loop
    while True:
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            alt_f4 = (event.type == KEYDOWN and (event.key == K_F4
                                                 and (pressed_keys[K_LALT] or pressed_keys[K_RALT])))
            if event.type == QUIT or alt_f4:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_a:
                    actions_capturer.key_a = True
                elif event.key == K_LEFT:
                    actions_capturer.key_left = True
                elif event.key == K_RIGHT:
                    actions_capturer.key_right = True
                elif event.key == K_UP:
                    actions_capturer.key_up = True
                elif event.key == K_DOWN:
                    actions_capturer.key_down = True
                elif event.key == K_ESCAPE:
                    actions_capturer.key_escape = True
                elif event.key == K_v:
                    actions_capturer.key_v = True
                elif event.key == K_SPACE:
                    actions_capturer.key_space = True

        if controller.update_model(actions_capturer) == 'quit':
            sys.exit()
        controller.update_view()

        actions_capturer.to_default()

        pygame.display.update()
        clock.tick(30)
        # print(str(clock.get_fps()))


if __name__ == '__main__':
    start_game()
