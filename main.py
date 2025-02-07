import pygame
import time
import math
from utils import blit_rotate_center, blit_text_center
pygame.font.init()


GRASS = pygame.transform.scale_by(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = pygame.transform.scale_by(pygame.image.load("imgs/track.png"), .9)

TRACK_BORDER = pygame.transform.scale_by(pygame.image.load("imgs/track-border.png"), .9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POS = (130, 250)

RED_CAR = pygame.transform.scale_by(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = pygame.transform.scale_by(pygame.image.load("imgs/green-car.png"), 0.55)
CAR_WIDTH, CAR_HEIGHT = RED_CAR.get_width(), RED_CAR.get_height()
PATH = [(173, 107), (71, 78), (71, 481), (227, 647), (317, 721), (415, 664), (417, 533), (498, 461), (594, 546), (622, 700), (740, 701), (738, 438), (665, 373), (473, 371), (410, 298), (695, 260), (737, 112), (447, 84), (310, 92), (285, 364), (196, 398), (179, 236)]

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Racing Game!")
FPS = 60

MAIN_FONT = pygame.font.SysFont("comicsans", 35)

class GameInfo:
    LEVELS = 5

    def __init__(self, level = 1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0
    
    def retry(self):
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False
    
    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()
    
    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)

class AbstractCar:

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.rotated_img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left = False, right = False):
        if left:
            self.angle += self.rotation_vel
        if right:
            self.angle -= self.rotation_vel
    
    def draw(self, win):
        self.rotated_img = blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
    
    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()
    
    def move_backwards(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        self.vertical = math.cos(radians)*self.vel
        self.horizontal = math.sin(radians)*self.vel
        self.x -= self.horizontal
        self.y -= self.vertical

    def collide(self, x, y, mask = None):
        car_mask = pygame.mask.from_surface(self.rotated_img)
        radians = math.radians(self.angle)
        topleft_x, topleft_y = self.rotated_img.get_rect(center = (self.x, self.y)).topleft
        offset = (int(topleft_x - x),int(topleft_y - y))
        if not mask:
            mask = pygame.Mask((1,1),True)
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (190, 220)

    def reduce_speed(self):
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration/2, 0)
        else:
            self.vel = min(self.vel + self.acceleration/2, 0)
        self.move()
    
    def bounce(self):
        self.vel = -self.vel
        self.move()

class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (160,220)

    def __init__(self, max_vel, rotation_vel, path = []):
        super().__init__(max_vel, rotation_vel)
        self.ultimate_vel = max_vel
        self.max_vel = max_vel/2
        self.path = path
        self.current_point = 0
    
    def draw_points(self,win):
        for point in self.path:
            pygame.draw.circle(win, 'red', point, 3)
    
    def draw_pointer(self,win):
        radians = math.radians(self.angle)
        pygame.draw.circle(win, 'blue', (self.x, self.y), 2)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        radians = math.radians(self.angle)
        x_dif = target_x - self.x
        y_dif = target_y - self.y

        if y_dif == 0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_dif/y_dif)
        
        if target_y > self.y:
            desired_radian_angle += math.pi
        
        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360
        
        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        if self.collide(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return
        self.calculate_angle()
        self.update_path_point()
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        super().move()
    
    def reset(self):
        super().reset()
        self.current_point = 0
    
    def next_level(self, level, levels):
        self.reset()
        self.max_vel = self.ultimate_vel * 0.5 * (1 + (level - 1)/(levels - 1))


def draw(win, images, player_car, computer_car, game_info):
    for img, pos in images:
        win.blit(img, pos)
    
    level_text = MAIN_FONT.render(f"Level {game_info.level}/{game_info.LEVELS}", 1, "white")
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()} s", 1, "white")
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    vel_text = MAIN_FONT.render(f"Vel {round(player_car.vel,1)} px/s", 1, "white")
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    computer_car.draw(win)
    player_car.draw(win)
    pygame.display.update()

def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left = True)
    if keys[pygame.K_d]:
        player_car.rotate(right = True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backwards()
    
    if not moved:
        player_car.reduce_speed()

def handle_collisions(player_car, computer_car, game_info):
    if player_car.collide(0, 0, TRACK_BORDER_MASK):
        player_car.bounce()
    
    computer_finish_poi_collide = computer_car.collide(*FINISH_POS, FINISH_MASK)
    if computer_finish_poi_collide:
        blit_text_center(WIN, MAIN_FONT, "You lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        player_car.reset()
        computer_car.reset()
        game_info.retry()

    player_finish_poi_collide = player_car.collide(*FINISH_POS, FINISH_MASK)
    if player_finish_poi_collide:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            game_info.next_level()
            game_info.next_level()
            game_info.next_level()

            player_car.reset()
            computer_car.next_level(game_info.level, game_info.LEVELS)

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0,0)), (TRACK, (0,0)), (FINISH, FINISH_POS), (TRACK_BORDER, (0,0))]
player_car = PlayerCar(4,4)
computer_car = ComputerCar(4,4, PATH)
game_info = GameInfo()


while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, computer_car, game_info)

    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        pygame.time.wait(50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
        
            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
    
    move_player(player_car)
    computer_car.move()

    handle_collisions(player_car,computer_car, game_info)

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "You won the game!")
        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car = ComputerCar(4,4, PATH)

pygame.quit()