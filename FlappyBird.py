import pygame
import random
import numpy
import sys

pygame.init()

# Establecer tamaño de la ventana
screen = pygame.display.set_mode((400, 708))
#screen = pygame.display.set_mode((400, 800))

pygame.display.set_caption("Flappy Bird 2.0")

clock = pygame.time.Clock()

# Cargar imagen de fondo
background_image = pygame.image.load("assets/background.png")
background_image = pygame.transform.scale(background_image, (400, 708))

# Cargar imagen de tubos
pipe_image = pygame.image.load("assets/pipe.png")
pipe_image = pygame.transform.scale(pipe_image, (50,400))
rotated_pipe_image = pygame.transform.rotate(pipe_image, 180)

# Ajustes de pipes
pipe_list = []
pipe_timer = 0
pipe_interval = 120

# Puntaje & Game_Over
score = 0
game_over = False
running = False

# Clase pajaro
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.gravity = 0.15
        self.image = pygame.image.load("assets/bird.png")
        self.image = pygame.transform.scale(self.image, (50,50))
        self.rect = self.image.get_rect(topleft = (self.x, self.y))

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.topleft = (self.x, self.y)

    def jump(self):
        self.velocity = -5

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# Clase tubo      
class Pipe:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pipe_image
        self.rect = self.image.get_rect(topleft = (x, y))
    def move(self):
        self.x -= 5
        self.rect.x = self.x
    
    def draw(self, screen):
        #print(self.x, self.y)
        #print(self.pipe_rect)
        #print("_________________")
        if self.rect.y < 0:
            screen.blit(rotated_pipe_image, self.rect)
        else:
            screen.blit(self.image, self.rect)
          
last_pipe_passed = None

logo_image = pygame.image.load("assets/logo.png")
logo_image = pygame.transform.scale(logo_image, (screen.get_width()-20,75))
y = 10
completed = False

start_image = pygame.image.load("assets/start.png")
start_image = pygame.transform.scale(start_image, (screen.get_width()-10,75))
min_scale = 0.5
max_scale = 1
scale = 1
scale_direction = 1
# True = Agrandando | False = Achicando
sizing = True

# <----------->
#    #BUCLES
# <----------->

while running == False:
    clock.tick(80)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                running = True
                break
    screen.blit(background_image, (0, 0))
    if y < 30 and y >= 10 and completed == False:
        y+= 0.2
    if int(y) == 30:
        completed = True
    if completed:
        y-= 0.2
    if int(y) == 10:
        completed = False
        
    
    screen.blit(logo_image, (10, y))
    
    scale += 0.01 * scale_direction
    if scale > max_scale or scale < min_scale:
        scale_direction *= -1
    scaled_image = pygame.transform.scale(start_image, (int(start_image.get_width() * scale), int(start_image.get_height() * scale)))
    rect = scaled_image.get_rect(center = (200, 200))
    rect.y = 550
    screen.blit(scaled_image, rect)
    
    pygame.display.flip() 

bird = Bird(50, 200)

while running == True:
    clock.tick(80)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump()
    pipe_timer += 1
    screen.blit(background_image, (0, 0))
    screen.blit(bird.image, bird.rect)
    font = pygame.font.Font("assets/font/font.ttf", 40)
    score_text = font.render(str(score), True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    if pipe_timer == pipe_interval:
        #pipe_list.append(Pipe(400, random.randint(350,400), pipe_image))
        #pipe_list.append(Pipe(400, random.randint(350,400) -550 - pipe_image.get_height(), rotated_pipe_image))
        #pipe_timer = 0
        x = 400
        y = random.randint(350,450)
        pipe_list.append(Pipe(x, y))
        pipe_list.append(Pipe(x, y - random.randint(100,175) - pipe_image.get_height()))
        pipe_timer = 0
    
    for pipe in pipe_list:
        pipe.move()
        pipe.draw(screen)
        if last_pipe_passed is None:
            last_pipe_passed = -1000
        if last_pipe_passed == -1000:
            if bird.rect.right > pipe.rect.left and pipe.rect.left > last_pipe_passed:
                score += 1
                last_pipe_passed = pipe.rect
        elif bird.rect.right > pipe.rect.left and pipe.rect.left > last_pipe_passed.left:
            score += 1
            last_pipe_passed = pipe.rect
        if pipe.x <= -50:
            pipe_list.remove(pipe)
    bird.update()
    pygame.display.update()