import pygame
import random
import sys
import asyncio  # Add this

SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
GRAVITY = 0.25
BIRD_JUMP = -4.5
PIPE_SPEED = 3
PIPE_GAP = 100
FPS = 60

class Bird:
    def __init__(self):
        try:
            self.frames = [
                pygame.image.load('assets/Fdown.png').convert_alpha(),
                pygame.image.load('assets/Fmid.png').convert_alpha(),
                pygame.image.load('assets/Fup.png').convert_alpha()
            ]
        except:
            surf = pygame.Surface((34, 24)); surf.fill((255, 200, 0))
            self.frames = [surf, surf, surf]
            
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(50, SCREEN_HEIGHT // 2))
        self.velocity = 0
        self.rotated_image = self.image

    def animate(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.image = self.frames[self.frame_index]

    def apply_gravity(self):
        self.velocity += GRAVITY
        self.rect.centery += self.velocity
        # Adding tilt when falling or jumping
        self.rotated_image = pygame.transform.rotate(self.image, -self.velocity * 3)

    def jump(self):
        self.velocity = BIRD_JUMP

    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect)

class Pipe:
    def __init__(self, x):
        self.pipe_surface = pygame.image.load('assets/pipe-green.png').convert_alpha()
        self.top_pipe_surface = pygame.image.load('assets/pipe-green-top.png').convert_alpha()
        self.gap_y = random.randint(150, 350)
        self.x = x
        self.scored = False
        self.bottom_rect = self.pipe_surface.get_rect(midtop=(self.x, self.gap_y + PIPE_GAP // 2))
        self.top_rect = self.top_pipe_surface.get_rect(midbottom=(self.x, self.gap_y - PIPE_GAP // 2))

    def update(self):
        self.x -= PIPE_SPEED
        self.bottom_rect.centerx = self.x
        self.top_rect.centerx = self.x

    def draw(self, screen):
        screen.blit(self.pipe_surface, self.bottom_rect)
        screen.blit(self.top_pipe_surface, self.top_rect)

async def main(): 
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    score_font = pygame.font.SysFont("Impact", 32)
    restart_font = pygame.font.SysFont("Arial", 18, bold=True)

    # Assets
    bg_surface = pygame.image.load('assets/background-day.png').convert()
    base_surface = pygame.image.load('assets/base.png').convert()
    msg_surface = pygame.image.load('assets/message.png').convert_alpha()
    over_surface = pygame.image.load('assets/gameover.png').convert_alpha()
    
    base_x = 0
    bird = Bird()
    pipes = []
    
    SPAWNPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPAWNPIPE, 1200)
    BIRDFLAP = pygame.USEREVENT + 1
    pygame.time.set_timer(BIRDFLAP, 100)

    game_active = False
    game_over = False
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if not game_active and not game_over:
                        game_active = True
                    elif game_active:
                        bird.jump()
                    elif game_over:
                        # Reset Game
                        game_active = True
                        game_over = False
                        pipes = []
                        bird = Bird()
                        score = 0
                        base_x = 0

            if event.type == SPAWNPIPE and game_active:
                pipes.append(Pipe(SCREEN_WIDTH + 50))

            if event.type == BIRDFLAP and game_active:
                bird.animate()

        # DRAWING LOGIC Initial drawing of background (static)
        screen.blit(bg_surface, (0, 0))

        # Move floor and pipes if game is active
        if game_active:
            base_x -= PIPE_SPEED
            if base_x <= -SCREEN_WIDTH:
                base_x = 0
            
            bird.apply_gravity()
            for pipe in pipes:
                pipe.update()
            
            # Boundary & Collision Check
            if bird.rect.top <= 0 or bird.rect.bottom >= 450:
                game_active = False
                game_over = True
            for pipe in pipes:
                if bird.rect.colliderect(pipe.bottom_rect) or bird.rect.colliderect(pipe.top_rect):
                    game_active = False
                    game_over = True
                if not pipe.scored and pipe.x < bird.rect.left:
                    score += 1
                    pipe.scored = True
            
            pipes = [p for p in pipes if p.x > -50]

        # Draw pipes and bird
        for pipe in pipes:
            pipe.draw(screen)
        
        screen.blit(base_surface, (base_x, 450))
        screen.blit(base_surface, (base_x + SCREEN_WIDTH, 450))
        bird.draw(screen)

        # UI 
        if not game_active and not game_over:
            screen.blit(msg_surface, (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2, 50))

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Black with 150/255 transparency
            screen.blit(overlay, (0,0))
            screen.blit(over_surface, (SCREEN_WIDTH // 2 - over_surface.get_width() // 2, 180))
            res_score_surf = score_font.render(f"SCORE: {score}", True, (255, 255, 255))
            screen.blit(res_score_surf, (SCREEN_WIDTH // 2 - res_score_surf.get_width() // 2, 240))
            restart_surf = restart_font.render("PRESS SPACE OR ENTER TO RESTART", True, (255, 255, 255))
            screen.blit(restart_surf, (SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, 320))

        else:
            score_txt = score_font.render(str(score), True, (255, 255, 255))
            screen.blit(score_txt, (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, 50))

        pygame.display.update()
        clock.tick(FPS)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())