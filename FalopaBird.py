#   """
#    ________          __                                _______   __                  __ 
#   |        \        |  \                              |       \ |  \                |  \. 
#   | $$$$$$$$______  | $$  ______    ______    ______  | $$$$$$$\ \$$  ______    ____| $$
#   | $$__   |      \ | $$ /      \  /      \  |      \ | $$__/ $$|  \ /      \  /      $$
#   | $$  \   \$$$$$$\| $$|  $$$$$$\|  $$$$$$\  \$$$$$$\| $$    $$| $$|  $$$$$$\|  $$$$$$$
#   | $$$$$  /      $$| $$| $$  | $$| $$  | $$ /      $$| $$$$$$$\| $$| $$   \$$| $$  | $$
#   | $$    |  $$$$$$$| $$| $$__/ $$| $$__/ $$|  $$$$$$$| $$__/ $$| $$| $$      | $$__| $$
#   | $$     \$$    $$| $$ \$$    $$| $$    $$ \$$    $$| $$    $$| $$| $$       \$$    $$
#    \$$      \$$$$$$$ \$$  \$$$$$$ | $$$$$$$   \$$$$$$$ \$$$$$$$  \$$ \$$        \$$$$$$$
#                                   | $$                                                  
#                                   | $$                                                  
#                                    \$$                    
#   """

import pygame
import math
import random
import sys
import os
import re
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def loadSettings(file):
    json_lines = []
    
    with open(file, 'r', encoding='UTF8') as f:
        for line in f:
            clean_line = re.sub(r'//.*', '', line).strip()
            if clean_line: 
                json_lines.append(clean_line)

    json_content = "\n".join(json_lines)

    return json.loads(json_content)

config = loadSettings("data/settings.json")['config']

defSett = {'step': 1, 'perPipe': 1, 'gravity': 0.25, 'velocity': -5, 'animBird': True, 'pipePer': 90, 'pipeSpeed': 5, 'backgAnim': False, 'bird': 'bird.tga', 'pipe': 'pipe.tga', 'plane': 'plane.tga', 'tower': 'tower.tga', 'logo': 'logo.png', 'backgrounds': ['background_fb.bmp', 'background_ny.bmp']}

sett = {}

for i in config:
    sett[i.split('.')[1]] = config.get(i)

pygame.init()

def getSett(name):
    return defSett[name] if sett.get(name) is None else sett.get(name)

bird_file = getSett("bird")
plane_file = getSett("plane")
pipe_file = getSett("pipe")
tower_file = getSett("tower")
bg_file = getSett("backgrounds")[0]
ny_file = getSett("backgrounds")[1]

if not os.path.exists("data/settings.json"):
    print("ERROR: No se encontró 'data/settings.json'")
    sys.exit(1)

for file in [bird_file, plane_file, pipe_file, tower_file, bg_file, ny_file]:
    if not os.path.exists("assets/" + file):
        print(f"ERROR: No se encontró 'assets/{file}'")
        sys.exit(1)

boomPoint = ()

screen = pygame.display.set_mode((400, 708))

pygame.display.set_icon(pygame.image.load("assets/"+bird_file))

pygame.display.set_caption("FlappyBird")

clock = pygame.time.Clock()

pipe_image = pygame.image.load("assets/"+pipe_file).convert()
pipe_image = pygame.transform.scale(pipe_image, (65,400))
rotated_pipe_image = pygame.transform.flip(pipe_image, False, True)
pipe_col_width = 45

pipe_list = []
pipe_timer = 0
pipe_interval = getSett("pipePer")
pipehb_list = []
pipe_passed = 0
pipe_score = getSett("perPipe")

score = 0
step_score = getSett("step")

game_over = False
running = False
max_best_length = 7

def saveScore(score):
    with open("data/BestScore", 'r+', encoding='utf-8') as f:
        best_score = int(f.read())
        if score > best_score:
            f.seek(0)
            f.write(str(score))

def getBest():
    try:
        with open("data/BestScore", 'r') as f:
            score = f.read().strip()
            if score.isdigit():
                return int(score)
            return 0
    except FileNotFoundError:
        return 0

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.invert = False
        self.velocity = 0
        self.gravity = getSett("gravity")
        self.image = pygame.image.load("assets/"+bird_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60,50))
        
        self.image_rotated = self.image
        self.image_scaled = self.image

        self.rect = self.image.get_rect(topleft = (self.x, self.y))
        self.collision = None

    def update(self):
        global game_over
        global boomPoint
        if self.rect.y > screen.get_height() or self.rect.y < 0:
            boomPoint = (bird.x, bird.y)
            saveScore(score)
            game_over = True
        if invert:
            self.velocity += self.gravity
            self.y -= self.velocity
        else:
            self.velocity += self.gravity
            self.y += self.velocity
        self.rect.topleft = (self.x, self.y)
        angle = max(-30, min(30, self.velocity * 3)) 
        if getSett("animBird"):
            self.image_rotated = pygame.transform.rotate(self.image, -angle).convert_alpha()
        self.rect = self.image_rotated.get_rect(center=self.rect.center)

    def jump(self):
        self.velocity = getSett("velocity")
        
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
        self.x -= getSett("pipeSpeed")
        self.rect.x = self.x
    
    def draw(self, screen):
        if self.rect.y < 0:
            screen.blit(rotated_pipe_image, self.rect)
        else:
            screen.blit(self.image, self.rect)

last_pipe_passed = None

logo_image = pygame.image.load("assets/"+getSett("logo")).convert_alpha()
logo_image = pygame.transform.scale(logo_image, (screen.get_width()-20,75))
y = 10
completed = False

start_image = pygame.image.load("assets/start.png").convert_alpha()
start_image = pygame.transform.scale(start_image, (screen.get_width()-10,75))
min_scale = 0.5
max_scale = 1
scale = 1
logo_scale = 1
scale_direction = 1
logo_direction = 1

sizing = True
hitbox = False
invert = False
pause = False

gameover = pygame.image.load("assets/gameover.tga").convert_alpha()
gameover = pygame.transform.scale(gameover, (350, 200))
gameover2 = pygame.transform.flip(gameover, False, True)


main_menu_bird = Bird(-75, 300)
bird = Bird(50, 200)

class BackgroundHandler():
    def __init__(self):
        default = pygame.image.load("assets/"+bg_file).convert()
        default = pygame.transform.scale(default, (400, 708))
        inverted = None

        self.bg_xa = 0
        self.bg_xb = 400

        self.background = {
            "default": default,
            "inverted": inverted
        }

    def draw(self):
        screen.blit(self.background["default"], (0, 0))

    def drawBackground(self):
        global invert, game_over
        default = self.background["default"]
        inverted = self.background["inverted"]

        if invert:
            screen.blit(inverted, (self.bg_xa, 0))
            screen.blit(inverted, (self.bg_xb, 0))
        else:
            screen.blit(default, (self.bg_xa, 0))
            screen.blit(default, (self.bg_xb, 0))

        if not game_over and getSett("backgAnim"):
            self.bg_xa -= 1
            self.bg_xb -= 1

        if self.bg_xa <= -400: 
            self.bg_xa = 400
        if self.bg_xb <= -400:
            self.bg_xb = 400

    def returnBackground(self):
        self.bg_xa = 0
        self.bg_xb = 400

        new_background = pygame.image.load("assets/"+bg_file).convert()
        new_background = pygame.transform.scale(new_background, (400, 708))

        self.background["default"] = new_background

background = BackgroundHandler()

class EventHandler():
    def __init__(self):
        global running

        self.jumpKey = pygame.K_SPACE
        self.jumpBtn = pygame.BUTTON_LEFT
        self.invertKey = pygame.K_TAB
        self.hitboxKey = pygame.K_h
        self.pauseKey = pygame.K_p
        self.specialKey1 = pygame.K_F7
        self.menuKey = pygame.K_m

    def handleMenu(self):
        global running
        global invert

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == self.jumpKey:
                    running = True
                    break
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    sys.exit()
                elif event.key == self.invertKey:
                    invert = True if not invert else False
                    print(f"Cheat -> Invert Game ({invert})")

    def handleIngame(self):
        global invert, hitbox
        global pause
        global game_over
        global pipe_timer
        global bird
        global bird_file
        global running
        global score
        global background_image, background_image2
        global rotated_pipe_image
        global pipe_file, bg_file

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                saveScore(score)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == self.hitboxKey:
                    hitbox = True if not hitbox else False
                    print(f"Cheat -> Switch hitboxes ({hitbox})")
                
                if event.key == self.pauseKey:
                    pause = False if pause else True
                    print(f"Cheat -> Pause Game ({pause})")

                if event.key == self.invertKey and not game_over and not pause:
                    invert = True if not invert else False
                    print(f"Cheat -> Invert Game ({invert})")
                
                if event.key == self.menuKey and game_over:
                    print(f"Flappy -> Back to main menu")
                    mainMenu()

                if event.key == self.specialKey1 and not game_over:
                    bird_file = plane_file if bird_file != plane_file else "bird.tga"
                    pipe_file = tower_file if pipe_file != tower_file else "pipe.tga"
                    bg_file = ny_file if bg_file != ny_file else "background_fb.bmp"
                    print("bg_file: "+bg_file)
                    if bg_file == ny_file:
                        background_image = pygame.image.load("assets/"+bg_file).convert()
                        background_image = pygame.transform.scale(background_image, (400, 708))
                        background_image2 = pygame.transform.flip(background_image, False, True)

                        background.background["default"] = background_image
                        background.background["inverted"] = background_image2
                    else: 
                        background_image = pygame.image.load("assets/"+bg_file).convert()
                        background_image = pygame.transform.scale(background_image, (400, 708))
                        background_image2 = pygame.transform.flip(background_image, False, True)

                        background.background["default"] = background_image
                        background.background["inverted"] = background_image2
                        
                        background.returnBackground()

                    pipe_image = pygame.image.load("assets/"+pipe_file).convert_alpha()
                    pipe_image = pygame.transform.scale(pipe_image, (65,400))
                    rotated_pipe_image = pygame.transform.flip(pipe_image, False, True)

                    for pipe in pipe_list:
                        
                        pipe[0].image = pipe_image
                if event.key == self.jumpKey and not pause:
                    if game_over:
                        score = 0
                        pipe_list.clear()
                        prects.clear()
                        pipehb_list.clear()
                        pipe_timer = 0
                        bird = Bird(50, 200)
                        game_over = False
                    else:
                        bird.jump()
                elif event.key == pygame.K_ESCAPE:
                        running = False
                        saveScore(score)
                        sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == self.jumpBtn:
                    if game_over:
                        score = 0
                        pipe_list.clear()
                        prects.clear()
                        pipehb_list.clear()
                        pipe_timer = 0
                        bird = Bird(50, 200)
                        game_over = False
                    else:
                        bird.jump()

def logoAnimation():
    global completed, y
    global logo_scale, logo_direction

    if y < 30 and y >= 10 and completed == False:
        y+= 0.2
    if int(y) == 30:
        completed = True
    if completed:
        y-= 0.2
    if int(y) == 10:
        completed = False

    logo_scale += (1 / 1000) * scale_direction

    if logo_scale > max_scale or logo_scale < 0.95:
        logo_direction *= -1
    scaled_image = pygame.transform.scale(logo_image, (int(logo_image.get_width() * logo_scale), int(logo_image.get_height() * logo_scale)))
    
    rect = scaled_image.get_rect(center = (200, y + 45))

    screen.blit(scaled_image, rect)

def startIndicator():
    global scale, scale_direction

    scale += 0.01 * scale_direction
    if scale > max_scale or scale < min_scale:
        scale_direction *= -1
    scaled_image = pygame.transform.scale(start_image, (int(start_image.get_width() * scale), int(start_image.get_height() * scale)))
    rect = scaled_image.get_rect(center = (200, 200))
    rect.y = 550
    screen.blit(scaled_image, rect)

def gameOver():
    global pause

    pause = False
    background.drawBackground()
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
        if invert:
            screen.blit(gameover2, (25,300))
        else:
            screen.blit(gameover, (25,300))

def pipeSpawn():
    global pipe_timer

    x = 400
    y = random.randint(350,450)

    pipe0 = Pipe(x, y)
    pipe1 = Pipe(x, y - 125 - pipe_image.get_height())

    pipe_list.append((pipe0, False))
    pipe_list.append((pipe1, True))

    pipe_timer = 0

def checkPipes():
    global boomPoint
    global last_pipe_passed
    global score
    global game_over
    global pipe_passed

    for pipe in pipe_list:
        pipe[0].move()
        pipe[0].draw(screen)

        if last_pipe_passed is None:
            last_pipe_passed = -1000
        if last_pipe_passed == -1000:
            if bird.rect.left > pipe[0].rect.right and pipe[0].rect.left > last_pipe_passed:
                pipe_passed += 1
                if pipe_passed == pipe_score:
                    score += step_score
                    pipe_passed = 0
                last_pipe_passed = pipe[0].rect
        elif bird.rect.left > pipe[0].rect.right and pipe[0].rect.left > last_pipe_passed.left:
            pipe_passed += 1
            if pipe_passed == pipe_score:
                    score += step_score
                    pipe_passed = 0
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

        if pipe[0].x <= -50 and not game_over:
            pipe_list.remove(pipe)
            pipe_list.remove(pipe_list[0])

def drawCollisions():
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

def drawScore():
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

event = EventHandler()

def mainMenu():
    global tick
    global running
    global pause
    global game_over
    global score
    global pipe_timer
    global bird

    if running:
        score = 0
        pipe_list.clear()
        prects.clear()
        pipehb_list.clear()
        pipe_timer = 0
        bird = Bird(50, 200)
        game_over = False
        running = False

    while not running:
        tick = clock.tick(60)
        
        event.handleMenu()

        background.draw()
        
        logoAnimation()

        main_menu_bird.mainmenu()
        
        startIndicator()
        
        pygame.display.flip() 

mainMenu()

while running:
    tick = clock.tick(60)

    event.handleIngame()

    if game_over:
        gameOver()
    else:
        if pause:
            continue

        pipe_timer += 1

        bird.image = pygame.image.load("assets/"+bird_file).convert_alpha()
        bird.image = pygame.transform.scale(bird.image, (60,50))
        bird.rect = bird.image.get_rect(topleft = (bird.x, bird.y)) 

        if invert:
            background_image2 = pygame.transform.flip(background.background["default"], False, True)
            bird.image = pygame.transform.flip(bird.image, False, True)

            background.background["inverted"] = background_image2

        background.drawBackground()

        font = pygame.font.Font("assets/font/font.ttf", 40)
        
        if pipe_timer == pipe_interval:
            pipeSpawn()
    
        checkPipes()

        bird.draw(screen=screen)
        
        hbthickness = 2
        
        hbcolor = (255, 0, 0)

        topleft = (bird.rect.topleft[0] + 10, bird.rect.topleft[1] + 10)

        hbbrect = pygame.Rect(topleft, (bird.rect.width-5, bird.rect.height-10))

        bird.collision = hbbrect

        prects = []

        drawCollisions()

    drawScore()

    pygame.display.set_caption(f"FlappyBird ({min(int(clock.get_fps()), 60)} FPS)")
    pygame.display.update()
