import random
import time
from threading import Thread
import pygame

pygame.init()

# Constant
BIRD_ANIMATION_CHANGE_TIME = 0.1
GAME_WIDTH = 800
GAME_HEIGHT = 500
OBJECT_MOMENT_SPEED = 4
BIRD_MOMENT_SPEED = 1
RESET_POSITION_END = -50
RESET_POSITION_START = 800
FRAME_RATE = 60
PIPE_GAP = 425
UPPER_LIMIT = 50
LOWER_LIMIT = 250
Jump_Factor = 40
your_score = 0

# Display
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()
sky = pygame.image.load('Image/BG.png')
sky_END = pygame.image.load('Image/BG_END.png')
logo = pygame.image.load('Image/FB text.png')
play_button = pygame.image.load('Image/Playbotton.png')
pipe_down = pygame.image.load('Image/pipe-green-2.png')
pipe_up = pygame.image.load('Image/pipe-green-top-3.png')
bird_up = pygame.image.load('Image/Fup.png')
bird_mid = pygame.image.load('Image/Fmid.png')
bird_down = pygame.image.load('Image/Fdown.png')
gameover = pygame.image.load('Image/gameover.png')
current_bird = bird_mid

game_is_active = True
game_over = False
bird_movement_allowed = True
show_welcome_screen = True

active_threads = []
bird_position = [GAME_WIDTH // 3, GAME_HEIGHT // 2]
create_random_pipe_position = lambda: -random.randint(UPPER_LIMIT, LOWER_LIMIT)  # NOQA
active_pipes = [
    [i, create_random_pipe_position()]
    for i in range(GAME_WIDTH // 2, GAME_WIDTH + GAME_WIDTH // 2, 300)
]
bird_rect = current_bird.get_rect(topleft=bird_position)


def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)


def handle_pipe():
    global bird_rect, game_over, game_is_active
    for i in range(len(active_pipes)):
        screen.blit(pipe_up, active_pipes[i])
        pipe_up_rect = pipe_up.get_rect(topleft=active_pipes[i])
        screen.blit(pipe_down, [active_pipes[i][0], active_pipes[i][1] + PIPE_GAP])
        pipe_down_rect = pipe_down.get_rect(topleft=[active_pipes[i][0], active_pipes[i][1] + PIPE_GAP])

        if not game_over:
            active_pipes[i][0] -= OBJECT_MOMENT_SPEED
            if active_pipes[i][0] <= RESET_POSITION_END:
                active_pipes[i][0] = RESET_POSITION_START
                active_pipes[i][1] = create_random_pipe_position()
        if ((bird_rect.colliderect(pipe_up_rect))) or (bird_rect.colliderect(pipe_down_rect)):
            game_is_active = False
            end_screen()


def end_screen():
    global game_over, active_pipes, bird_movement_allowed, game_is_active, show_welcome_screen
    active_pipes = [[i, create_random_pipe_position()]
        for i in range(GAME_WIDTH // 2, GAME_WIDTH + GAME_WIDTH // 2, 300)
    ]
    game_over = True
    bird_movement_allowed = False
    while True:
        screen.blit(sky_END, (0, 0))
        screen.blit(gameover, ((GAME_WIDTH / 3.5), (GAME_HEIGHT / 6)))
        screen.blit(play_button, (((GAME_WIDTH/2.3)),(GAME_HEIGHT/2)))
        for key_event in pygame.event.get():
            if key_event.type == pygame.KEYUP and key_event.key == pygame.K_SPACE:
                game_is_active = True
                bird_movement_allowed = True
                game_over = False
                show_welcome_screen = False
                game()
        pygame.display.update()


def animate_bird():
    global current_bird

    while game_is_active:
        current_bird = bird_up
        time.sleep(BIRD_ANIMATION_CHANGE_TIME)
        current_bird = bird_mid
        time.sleep(BIRD_ANIMATION_CHANGE_TIME)
        current_bird = bird_down
        time.sleep(BIRD_ANIMATION_CHANGE_TIME)


def welcome_screen():
    display_welcome_screen = True

    while display_welcome_screen:
        screen.blit(logo, ((GAME_WIDTH/3.2), (GAME_HEIGHT / 6)))
        screen.blit(play_button, (((GAME_WIDTH/2.3)),(GAME_HEIGHT/2)))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                display_welcome_screen = False
                break

        pygame.display.update()
        clock.tick(FRAME_RATE)


def run_in_thread(function):
    function_thread = Thread(target=function, daemon=True)
    active_threads.append(function_thread)
    function_thread.start()


def handle_bird():
    global bird_rect
    if bird_movement_allowed:  # only update bird position if bird movement is allowed
        screen.blit(current_bird, bird_position)
        bird_rect = current_bird.get_rect(topleft=bird_position)

def game():
    global game_over, show_welcome_screen
    screen.blit(sky, (0, 0))
    run_in_thread(animate_bird)

    while game_is_active:
        bird_flew = False
        screen.blit(sky, (0, 0))

        for key_event in pygame.event.get():
            if key_event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if key_event.type == pygame.KEYDOWN and key_event.key == pygame.K_SPACE and not game_over:
                bird_position[1] -= BIRD_MOMENT_SPEED * Jump_Factor
                bird_flew = True
            if key_event.type == pygame.KEYUP and key_event.key == pygame.K_SPACE:
                bird_flew = False
        if show_welcome_screen is True:
            welcome_screen()
            screen.blit(sky, (0, 0))
            show_welcome_screen = False

        if not bird_flew and bird_movement_allowed:
            bird_position[1] += BIRD_MOMENT_SPEED

        handle_bird()
        handle_pipe()
        pygame.display.update()
        clock.tick(FRAME_RATE)

    for thread in active_threads:
        thread.join()


if __name__ == "__main__":
    game()
