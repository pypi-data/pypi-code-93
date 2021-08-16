#2021.6.18开始制作(cwx)
#python的AI效果库
import pygame,sys,time,random
#代码雨
def rain(screen):
    scene=1
    FONT_PX = 15
    font = pygame.font.SysFont("123.ttf", 25)
    bg_suface = pygame.Surface((800, 720), flags=pygame.SRCALPHA)
    bg_suface.fill(pygame.Color(0, 0, 0, 28))
    screen.fill((0, 0, 0))
    letter = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c',
              'v', 'b', 'n', 'm',0,1,2,3,4,5,6,7,8,9]
    texts = [
    font.render(str(letter[i]), True, (0, 255, 0)) for i in range(36)
    ]
    # 按屏幕的宽带计算可以在画板上放几列坐标并生成一个列表
    column = int(800 / FONT_PX)
    drops = [0 for i in range(column)]
    flag = False
    while scene == 1:
        # 从队列中获取事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # if event.key == pygame.K_q:
                #     flag = True
                scene = 2
                break
        if scene == 2:
            break
        # if scene==2 and flag == True:
        #     pygame.quit()
        #     sys.exit()
        #     break
        # if scene==2 and flag == False:
        #     break

        # 将暂停一段给定的毫秒数
        pygame.time.delay(30)

        # 重新编辑图像第二个参数是坐上角坐标
        screen.blit(bg_suface, (0, 0))
        for i in range(len(drops)):
            text = random.choice(texts)

            # 重新编辑每个坐标点的图像
            screen.blit(text, (i * FONT_PX, drops[i] * FONT_PX))

            drops[i] += 1
            if drops[i] * 10 > 720 or random.random() > 0.95:
                drops[i] = 0
        pygame.display.flip()
#退出事件
def q():
    for event in pygame.event.get():
        if event == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
#动态字 已渲染文本 模式 屏幕
def wtext(text,num,screen):
    if num == 1:#x减少y减少
        x=random.randint(600,900)
        y=random.randint(400,600)
        for i in range(1000):
            q()
            x-=0.1
            y-=0.1
            screen.blit(text,(x,y))
            pygame.display.update()
            screen.fill((0,0,0))
            time.sleep(0.001)
    if num == 2:#x增加y减少
        x=random.randint(100,700)
        y=random.randint(400,600)
        for i in range(1000):
            q()
            x+=0.1
            y-=0.1
            screen.blit(text,(x,y))
            pygame.display.update()
            screen.fill((0,0,0))
            time.sleep(0.001)
    if num == 3:#x增加y增加
        x=random.randint(100,700)
        y=random.randint(100,500)
        for i in range(1000):
            q()
            x+=0.1
            y+=0.1
            screen.blit(text,(x,y))
            pygame.display.update()
            screen.fill((0,0,0))
            time.sleep(0.001)
    if num == 4:#x减少y增加
        x=random.randint(600,900)
        y=random.randint(100,500)
        for i in range(1000):
            q()
            x-=0.1
            y+=0.1
            screen.blit(text,(x,y))
            pygame.display.update()
            screen.fill((0,0,0))
            time.sleep(0.001)
    if num == 5:#乱转，特别推荐！！！！！！！！
        for i in range(1000):
            q()
            x=random.randint(0,1000)
            y=random.randint(0,600)
            screen.blit(text,(x,y))
            pygame.display.update()
            screen.fill((0,0,0))
            time.sleep(0.001)