import random
import time
from threading import Thread
import pygame

# Initialize Pygame
pygame.init()

# Constants
BIRD_ANIMATION_CHANGE_TIME = 0.1
GAME_WIDTH = 800
GAME_HEIGHT = 500
OBJECT_MOVEMENT_SPEED = 4
BIRD_MOVEMENT_SPEED = 1
RESET_POSITION_END = -50
RESET_POSITION_START = 800
FRAME_RATE = 60
PIPE_GAP = 425
UPPER_LIMIT = 50
LOWER_LIMIT = 250
JUMP_FACTOR = 40
SCORE_POSITION = (GAME_WIDTH / 2, 20)

# Display setup
screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()

# Load assets
sky = pygame.image.load('Image/BG.png')
logo = pygame.image.load('Image/FB text.png')
pipe_down = pygame.image.load('Image/pipe-green-2.png')
pipe_up = pygame.image.load('Image/pipe-green-top-3.png')
bird_up = pygame.image.load('Image/Fup.png')
bird_mid = pygame.image.load('Image/Fmid.png')
bird_down = pygame.image.load('Image/Fdown.png')
bird_fall = pygame.image.load('Image/FB_Fall.png')

# Game state
current_bird = bird_mid
score = 0
game_is_active = True
game_over = False
bird_movement_allowed = True
show_welcome_screen = True
active_threads = []

# Bird and pipe positions
bird_position = [GAME_WIDTH // 3, GAME_HEIGHT // 2]
bird_rect = current_bird.get_rect(topleft=bird_position)
create_random_pipe_position = lambda: -random.randint(UPPER_LIMIT, LOWER_LIMIT)
active_pipes = [[i, create_random_pipe_position()] for i in range(GAME_WIDTH // 2, GAME_WIDTH + GAME_WIDTH // 2, 300)]

def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)

def handle_pipe():
    global bird_rect, game_over, game_is_active
    for pipe in active_pipes:
        screen.blit(pipe_up, pipe)
        pipe_up_rect = pipe_up.get_rect(topleft=pipe)

        lower_pipe_position = [pipe[0], pipe[1] + PIPE_GAP]
        screen.blit(pipe_down, lower_pipe_position)
        pipe_down_rect = pipe_down.get_rect(topleft=lower_pipe_position)

        if not game_over:
            pipe[0] -= OBJECT_MOVEMENT_SPEED
            if pipe[0] <= RESET_POSITION_END:
                increment_score()
                pipe[0] = RESET_POSITION_START
                pipe[1] = create_random_pipe_position()

        if bird_rect.colliderect(pipe_up_rect) or bird_rect.colliderect(pipe_down_rect):
            game_is_active = False
            end_screen()

def display_score():
    font = pygame.font.SysFont("impact", 30)
    score_surface = font.render(str(score), True, (255, 255, 255))
    screen.blit(score_surface, SCORE_POSITION)

def increment_score():
    global score
    for pipe in active_pipes:
        if not game_over and pipe[0] < bird_position[0] < pipe[0] + OBJECT_MOVEMENT_SPEED:
            score += 1

def end_screen():
    global game_over, bird_movement_allowed, game_is_active, show_welcome_screen, score
    game_over = True
    bird_movement_allowed = False

    animate_bird_fall()

    while True:
        # Draw background
        screen.blit(sky, (0, 0))
        # Draw pipes
        for pipe in active_pipes:
            # Upper pipe
            screen.blit(pipe_up, pipe)
            # Lower pipe
            lower_pipe_position = [pipe[0], pipe[1] + PIPE_GAP]
            screen.blit(pipe_down, lower_pipe_position)

        # Semi-transparent overlay
        draw_rect_alpha(screen, (0, 0, 0, 180), (150, 100, 500, 300))

        # Render texts
        font_large = pygame.font.SysFont("Times New Roman", 60, bold=True)
        font_small = pygame.font.SysFont("Times New Roman", 30)
        font_medium = pygame.font.SysFont("Times New Roman", 40)

        title_surface = font_large.render("Game Over", True, (255, 255, 255))
        score_label = font_medium.render("Your Score:", True, (255, 255, 255))
        score_value = font_large.render(str(score), True, (255, 215, 0))
        restart_message = font_small.render("Press SPACE to play again", True, (200, 200, 200))

        screen.blit(title_surface, (GAME_WIDTH // 2 - title_surface.get_width() // 2, 120))
        screen.blit(score_label, (GAME_WIDTH // 2 - score_label.get_width() // 2, 200))
        screen.blit(score_value, (GAME_WIDTH // 2 - score_value.get_width() // 2, 250))
        screen.blit(restart_message, (GAME_WIDTH // 2 - restart_message.get_width() // 2, 320))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                # Reset game state
                score = 0
                game_is_active = True
                bird_movement_allowed = True
                game_over = False
                show_welcome_screen = False
                bird_position[1] = GAME_HEIGHT // 2
                for i, pipe in enumerate(active_pipes):
                    pipe[0] = GAME_WIDTH // 2 + i * 300
                    pipe[1] = create_random_pipe_position()
                game()

        pygame.display.update()
        clock.tick(FRAME_RATE)


def animate_bird():
    global current_bird
    while game_is_active:
        current_bird = bird_up
        time.sleep(BIRD_ANIMATION_CHANGE_TIME)
        current_bird = bird_mid
        time.sleep(BIRD_ANIMATION_CHANGE_TIME)
        current_bird = bird_down
        time.sleep(BIRD_ANIMATION_CHANGE_TIME)

def animate_bird_fall():
    global current_bird

    bird_y = bird_position[1]
    velocity = -10
    gravity = 1

    # Mid-air frame
    current_bird = bird_mid
    screen.blit(sky, (0, 0))
    for pipe in active_pipes:
        screen.blit(pipe_up, pipe)
        screen.blit(pipe_down, (pipe[0], pipe[1] + PIPE_GAP))
    screen.blit(current_bird, (bird_position[0], bird_y))
    pygame.display.update()
    time.sleep(BIRD_ANIMATION_CHANGE_TIME)

    # Start falling
    current_bird = bird_fall

    while bird_y < GAME_HEIGHT:
        bird_y += velocity
        velocity += gravity

        # Draw background and pipes
        screen.blit(sky, (0, 0))
        for pipe in active_pipes:
            screen.blit(pipe_up, pipe)
            screen.blit(pipe_down, (pipe[0], pipe[1] + PIPE_GAP))

        # Draw falling bird
        screen.blit(current_bird, (bird_position[0], bird_y))
        pygame.display.update()
        clock.tick(FRAME_RATE)



def welcome_screen():
    while True:
        screen.blit(sky, (0, 0))
        screen.blit(logo, (GAME_WIDTH / 2.5, GAME_HEIGHT / 4))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return
        pygame.display.update()
        clock.tick(FRAME_RATE)


def run_in_thread(function):
    thread = Thread(target=function, daemon=True)
    active_threads.append(thread)
    thread.start()


def handle_bird():
    global bird_rect
    if bird_movement_allowed:
        screen.blit(current_bird, bird_position)
        bird_rect = current_bird.get_rect(topleft=bird_position)


def game():
    global game_over, show_welcome_screen

    if show_welcome_screen:
        welcome_screen()
        screen.blit(sky, (0, 0))
        show_welcome_screen = False

    run_in_thread(animate_bird)

    while game_is_active:
        screen.blit(sky, (0, 0))
        bird_flew = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not game_over:
                bird_position[1] -= BIRD_MOVEMENT_SPEED * JUMP_FACTOR
                bird_flew = True
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                bird_flew = False

        if not bird_flew and bird_movement_allowed:
            bird_position[1] += BIRD_MOVEMENT_SPEED

        handle_bird()
        handle_pipe()
        increment_score()
        display_score()

        pygame.display.update()
        clock.tick(FRAME_RATE)

    for thread in active_threads:
        thread.join()


if __name__ == "__main__":
    game()
