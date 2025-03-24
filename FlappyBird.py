import pygame
import math
import random
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

pygame.init()

bird_file = "bird.tga"
plane_file = "plane.tga"
pipe_file = "pipe.tga"
tower_file = "tower.tga"
bg_file = "background_fb.bmp"
ny_file = "background_ny.bmp"

enableHitbox = pygame.K_h
toggleInvert = pygame.K_TAB
secretTextures = pygame.K_F7
keys = []

bg_xa = 0
bg_xb = 400

boomPoint = ()

screen = pygame.display.set_mode((400, 708))

pygame.display.set_icon(pygame.image.load("assets/"+bird_file))

pygame.display.set_caption("FlappyBird")

clock = pygame.time.Clock()

background_image = pygame.image.load("assets/"+bg_file).convert()
background_image = pygame.transform.scale(background_image, (400, 708))
background_image2 = None

pipe_image = pygame.image.load("assets/"+pipe_file).convert()
pipe_image = pygame.transform.scale(pipe_image, (65,400))
rotated_pipe_image = pygame.transform.flip(pipe_image, False, True)
pipe_col_width = 45

pipe_list = []
pipe_timer = 0
pipe_interval = 90
pipehb_list = []

score = 0
step_score = 1

game_over = False
running = False
max_best_length = 7

def saveScore(score):
    with open("BestScore", 'r+', encoding='utf-8') as f:
        best_score = int(f.read())
        if score > best_score:
            f.seek(0)
            f.write(str(score))

def getBest():
    try:
        with open("BestScore", 'r') as f:
            score = f.read().strip()
            if score.isdigit():
                return int(score)
            return 0
    except FileNotFoundError:
        return 0

def drawBackground():
    global bg_xa, bg_xb

    if invert:
        screen.blit(background_image2, (bg_xa, 0))
        screen.blit(background_image2, (bg_xb, 0))
    else:
        screen.blit(background_image, (bg_xa, 0))
        screen.blit(background_image, (bg_xb, 0))

    if not game_over:
        bg_xa -= 1
        bg_xb -= 1

    if bg_xa <= -400: 
        bg_xa = 400
    if bg_xb <= -400:
        bg_xb = 400

def returnBackground():
    global bg_xa, bg_xb

    bg_xa = 0
    bg_xb = 400

    background_image = pygame.image.load("assets/"+bg_file).convert()
    background_image = pygame.transform.scale(background_image, (400, 708))

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.invert = False
        self.velocity = 0
        self.gravity = 0.25
        self.image = pygame.image.load("assets/"+bird_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60,50))
        
        self.image_rotated = self.image
        self.image_scaled = self.image

        self.rect = self.image.get_rect(topleft = (self.x, self.y))
        self.collision = None

    def update(self):
        if invert:
            self.velocity += self.gravity
            self.y -= self.velocity
        else:
            self.velocity += self.gravity
            self.y += self.velocity
        self.rect.topleft = (self.x, self.y)
        angle = max(-30, min(30, self.velocity * 3)) 
        self.image_rotated = pygame.transform.rotate(self.image, -angle).convert_alpha()
        self.rect = self.image_rotated.get_rect(center=self.rect.center)

    def jump(self):
        self.velocity = -5
        
    def draw(self, screen):
        screen.blit(self.image_rotated, self.rect)
        
    def mainmenu(self):
        scale = 1 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005)
        self.image_scaled = pygame.transform.scale(self.image, (int(60 * scale), int(50 * scale)))

        self.x += 5
        self.rect.x = self.x
        if self.x > 450: 
            self.x = -75

        screen.blit(self.image_scaled, self.rect)

class Pipe:
    def __init__(self, x, y):
        global rotated_pipe_image
        self.x = x
        self.y = y
        pipe_image = pygame.image.load("assets/"+pipe_file).convert_alpha()
        pipe_image = pygame.transform.scale(pipe_image, (65,400))
        rotated_pipe_image = pygame.transform.flip(pipe_image, False, True)
        self.image = pipe_image
        self.rect = self.image.get_rect(topleft = (self.x, self.y))

    def move(self):
        self.x -= 5
        self.rect.x = self.x
    
    def draw(self, screen):
        if self.rect.y < 0:
            screen.blit(rotated_pipe_image, self.rect)
        else:
            screen.blit(self.image, self.rect)

last_pipe_passed = None

logo_image = pygame.image.load("assets/logo.png").convert_alpha()
logo_image = pygame.transform.scale(logo_image, (screen.get_width()-20,75))
y = 10
completed = False

start_image = pygame.image.load("assets/start.png").convert_alpha()
start_image = pygame.transform.scale(start_image, (screen.get_width()-10,75))
min_scale = 0.5
max_scale = 1
scale = 1
scale_direction = 1

sizing = True
hitbox = False
invert = False
pause = False

gameover = pygame.image.load("assets/gameover.tga").convert_alpha()
gameover = pygame.transform.scale(gameover, (350, 200))

main_menu_bird = Bird(-75, 300)
bird = Bird(50, 200)

while running == False:
    tick = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                running = True
                break
            elif event.key == pygame.K_ESCAPE:
                running = False
                sys.exit()
            elif event.key == toggleInvert:
                invert = True if not invert else False
                print(f"Cheat -> Invert Game ({invert})")

    screen.blit(background_image, (0, 0))
    if y < 30 and y >= 10 and completed == False:
        y+= 0.2
    if int(y) == 30:
        completed = True
    if completed:
        y-= 0.2
    if int(y) == 10:
        completed = False
    
    main_menu_bird.mainmenu()
    
    screen.blit(logo_image, (10, y))
    
    scale += 0.01 * scale_direction
    if scale > max_scale or scale < min_scale:
        scale_direction *= -1
    scaled_image = pygame.transform.scale(start_image, (int(start_image.get_width() * scale), int(start_image.get_height() * scale)))
    rect = scaled_image.get_rect(center = (200, 200))
    rect.y = 550
    screen.blit(scaled_image, rect)
    
    pygame.display.flip() 

while running:
    tick = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            saveScore()
        if event.type == pygame.KEYDOWN:
            keys.append(event.key)

            if event.key == enableHitbox:
                hitbox = True if not hitbox else False
                print(f"Cheat -> Switch hitboxes ({hitbox})")
            
            if event.key == pygame.K_p:
                pause = False if pause else True
                print(f"Cheat -> Pause Game ({pause})")

            if event.key == toggleInvert and not game_over and not pause:
                invert = True if not invert else False
                print(f"Cheat -> Invert Game ({invert})")
            
            if event.key == secretTextures and not game_over:
                bird_file = plane_file if bird_file != plane_file else "bird.tga"
                pipe_file = tower_file if pipe_file != tower_file else "pipe.tga"
                bg_file = ny_file if bg_file != ny_file else "background_fb.bmp"
                print("bg_file: "+bg_file)
                if bg_file == ny_file:
                    background_image = pygame.image.load("assets/"+bg_file).convert()
                    background_image = pygame.transform.scale(background_image, (400, 708))
                    background_image2 = pygame.transform.flip(background_image, flip_x=True, flip_y=False)
                else: 
                    background_image = pygame.image.load("assets/"+bg_file).convert()
                    background_image = pygame.transform.scale(background_image, (400, 708))
                    background_image2 = pygame.transform.flip(background_image, flip_x=True, flip_y=False)
                    
                    returnBackground()

                pipe_image = pygame.image.load("assets/"+pipe_file).convert_alpha()
                pipe_image = pygame.transform.scale(pipe_image, (65,400))
                rotated_pipe_image = pygame.transform.flip(pipe_image, False, True)

                for pipe in pipe_list:
                    
                    pipe[0].image = pipe_image
            if event.key == pygame.K_SPACE and not pause:
                if game_over:
                    score = 0
                    pipe_list.clear()
                    pipe_timer = 0
                    bird = Bird(50, 200)
                    game_over = False
                else:
                    bird.jump()
            elif event.key == pygame.K_ESCAPE:
                    running = False
                    saveScore(score)
                    sys.exit()
    if game_over:
        pause = False
        drawBackground()
        prects.clear()
        for pipe in pipe_list:
            pipe[0].draw(screen)
        bird.update()
        bird.draw(screen=screen)
        pipehb_list.clear()
        if bird_file == plane_file:
            boom = pygame.image.load("assets/boom.png").convert_alpha()
            boom = pygame.transform.scale(boom, (90,120))
            boomr = boom.get_rect(topleft = (boomPoint[0] - 10, boomPoint[1] - 10))
            screen.blit(boom, boomr)
            ts = pygame.image.load("assets/topsecret.tga").convert_alpha()
            ts = pygame.transform.scale(ts, (400, 600))
            tsr = ts.get_rect(topleft = (0, 300))
            screen.blit(ts, tsr)
        else:
            screen.blit(gameover, (25,300))

    else:
        if pause:
            continue

        pipe_timer += 1

        bird.image = pygame.image.load("assets/"+bird_file).convert_alpha()
        bird.image = pygame.transform.scale(bird.image, (60,50))
        bird.rect = bird.image.get_rect(topleft = (bird.x, bird.y)) 

        if invert:
            background_image2 = pygame.transform.flip(background_image, False, True)
            bird.image = pygame.transform.flip(bird.image, False, True)
            background_image2 = pygame.transform.flip(background_image, False, True)

        drawBackground()

        font = pygame.font.Font("assets/font/font.ttf", 40)
        
        if pipe_timer == pipe_interval:
            x = 400
            y = random.randint(350,450)

            pipe0 = Pipe(x, y)
            pipe1 = Pipe(x, y - 125 - pipe_image.get_height())

            pipe_list.append((pipe0, False))
            pipe_list.append((pipe1, True))

            pipe_timer = 0
    
        for pipe in pipe_list:
            pipe[0].move()
            pipe[0].draw(screen)

            if last_pipe_passed is None:
                last_pipe_passed = -1000
            if last_pipe_passed == -1000:
                if bird.rect.left > pipe[0].rect.right and pipe[0].rect.left > last_pipe_passed:
                    score += step_score
                    last_pipe_passed = pipe[0].rect
            elif bird.rect.left > pipe[0].rect.right and pipe[0].rect.left > last_pipe_passed.left:
                score += step_score
                last_pipe_passed = pipe[0].rect
            for rect in pipehb_list:
                if not bird.collision == None and bird.collision.colliderect(rect):
                    saveScore(score)
                    boomPoint = (bird.x, bird.y)
                    game_over = True
                elif bird.collision == None and bird.rect.colliderect(rect):
                    saveScore(score)
                    boomPoint = (bird.x, bird.y)
                    game_over = True
            pipehb_list.clear()

            if bird.rect.y > screen.get_height() or bird.rect.y < 0:
                saveScore(score)
                game_over = True

            if pipe[0].x <= -50 and not game_over:
                pipe_list.remove(pipe)
                pipe_list.remove(pipe_list[0])

        bird.draw(screen=screen)
        
        hbthickness = 2
        
        hbcolor = (255, 0, 0)

        topleft = (bird.rect.topleft[0] + 10, bird.rect.topleft[1] + 10)

        hbbrect = pygame.Rect(topleft, (bird.rect.width-5, bird.rect.height-10))

        bird.collision = hbbrect

        prects = []

        for pipe in pipe_list:                
            if pipe[1]:
                pipe_topleft = (pipe[0].rect.topleft[0] + (15/2), pipe[0].rect.topleft[1]-2)
                hbprect = pygame.Rect(pipe_topleft, (pipe[0].rect.width-15, pipe[0].rect.height))
                prects.append(hbprect)
            else:
                pipe_topleft = (pipe[0].rect.topleft[0] + (15/2), pipe[0].rect.topleft[1]+2)
                hbprect = pygame.Rect(pipe_topleft, (pipe[0].rect.width-15, pipe[0].rect.height))
                prects.append(hbprect)
            pipehb_list.extend(prects)

        if not len(prects) == 0:
            for i in prects:
                if hitbox:
                    pygame.draw.rect(screen, hbcolor, i, hbthickness)
            prects.clear()
        if hitbox:
            pygame.draw.rect(screen, hbcolor, hbbrect, hbthickness)

        bird.update()

    score_dsp = str(min(score, 9999)).zfill(4)  

    score_text = font.render(score_dsp, True, (255, 255, 255))

    best_score = getBest()
    best_scoredsp = str(min(best_score, 9999)).zfill(4)

    best_text = font.render(best_scoredsp, True, (255, 255, 255))


    best_width = best_text.get_width()

    pos_x = 400 - best_width - 10

    pos_y = 620 if invert else 10 

    if invert:
        score_text = pygame.transform.flip(score_text, True, True)
        best_text = pygame.transform.flip(best_text, True, True)

    screen.blit(score_text, (10, pos_y))
    screen.blit(best_text, (pos_x, pos_y))
    pygame.display.set_caption(f"FlappyBird ({min(int(clock.get_fps()), 60)} FPS)")
    pygame.display.update()

