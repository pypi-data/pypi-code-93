import pygame

pygame.init()



class sigralib():

    class wn():
        def create(WIDTH, HEIGHT, TITLE):
            global screen
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption(TITLE)
        
        def icon_set(PATH):
            pygame.display.set_icon(PATH)
            
        def resize(WIDTH, HEIGHT):
            pygame.display.set_mode((WIDTH, HEIGHT))
            
        def rename(TITLE):
            pygame.display.set_caption(TITLE) 
        
        def wnLoop():
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                
                pygame.display.flip()

        def close():
            pygame.quit()

    class text():
        def console_print(printabletext):
            print(printabletext)

        class display_text():
    
                
                def complex(Font, Size, Text, BoolAA, Color_1, Color_2, X, Y):
                    font = pygame.font.Font(Font, Size)
                    string = font.render(Text, BoolAA, Color_1, Color_2)
                    screen.blit(string, (X, Y))

                def simple(Size, Text, BoolAA):
                    font = pygame.font.Font(None, Size)
                    string = font.render(Text, BoolAA, (255, 255, 255), (0, 0, 0))
                    screen.blit(string, (800 / 2, 600 / 2))
                    
    class does_nothing:
        
        def does_nothing(maybe):
            if maybe == "SAR > Other games!!!":
                    sigralib.wn.create(1280, 720, "Super animal royale > All other Battle Royale games!!1!!11")
                    sigralib.text.display_text.simple(100, "SAR > Fortnite", True)
                    sigralib.wn.wnLoop()

    class images:
        
        def transform(imagetotransform, ScaleX, ScaleY):
            imagetotransform = pygame.transform.scale(imagetotransform, (ScaleX, ScaleY))
            
        def display(imagetodisplay, X, Y):
            screen.blit(imagetodisplay, (X, Y))
            
    class math_indev:
        def plus(interger1, interger2):
            Solution = interger1 + interger2
            print(Solution)
            
        def minus(interger1, interger2):
            Solution = interger1 - interger2
            print(Solution)
            
        def multiply(interger1, interger2):
            Solution = interger1 * interger2
            print(Solution)
            
        def divide(interger1, interger2):
            Solution = interger1 / interger2
            print(Solution)
            
            
    class mouse:
        def getpos():
            pygame.mouse.get_pos()
            
        def setpos(x, y):
            
                pygame.mouse.set_pos(x, y)
                
        def mousedown(BOOL):
            pygame.mouse.get_pressed()
                
        def mouseup(BOOL):
            pygame.mouse.set_visible(BOOL)
                
        def visible(BOOL):
            pygame.mouse.set_visible(BOOL)
                
                
    class keyboard:
        def keydown_setup():
            global keydown
            keydown = pygame.key.get_pressed()
            
    