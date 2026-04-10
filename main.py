import pygame
import random
import asyncio
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).parent
ASSETS = BASE_DIR / "assets"

# --- Configuration ---
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
GRAVITY = 0.25
BIRD_JUMP = -4.5
PIPE_SPEED = 3
PIPE_GAP = 100
FPS = 60
GROUND_Y = 450


class Bird:
    def __init__(self, frames):
        self.frames = frames
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
        self.rotated_image = pygame.transform.rotate(self.image, -self.velocity * 3)

    def jump(self):
        self.velocity = BIRD_JUMP

    def draw(self, screen):
        rotated_rect = self.rotated_image.get_rect(center=self.rect.center)
        screen.blit(self.rotated_image, rotated_rect)


class Pipe:
    def __init__(self, x, surf, top_surf):
        self.pipe_surface = surf
        self.top_pipe_surface = top_surf
        self.gap_y = random.randint(150, 350)
        self.x = x
        self.scored = False
        self.bottom_rect = self.pipe_surface.get_rect(
            midtop=(self.x, self.gap_y + PIPE_GAP // 2)
        )
        self.top_rect = self.top_pipe_surface.get_rect(
            midbottom=(self.x, self.gap_y - PIPE_GAP // 2)
        )

    def update(self):
        self.x -= PIPE_SPEED
        self.bottom_rect.centerx = self.x
        self.top_rect.centerx = self.x

    def draw(self, screen):
        screen.blit(self.pipe_surface, self.bottom_rect)
        screen.blit(self.top_pipe_surface, self.top_rect)


def load_image(path, alpha=True):
    try:
        img = pygame.image.load(path)
        return img.convert_alpha() if alpha else img.convert()
    except Exception as e:
        print(f"Error loading {path}: {e}")
        surf = pygame.Surface((34, 24), pygame.SRCALPHA if alpha else 0)
        surf.fill((255, 0, 0))
        return surf


async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()

    score_font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 22)

    # Assets
    bg_surface = load_image(ASSETS / "background-day.png", False)
    base_surface = load_image(ASSETS / "base.png", False)
    msg_surface = load_image(ASSETS / "message.png")
    over_surface = load_image(ASSETS / "gameover.png")

    bird_frames = [
        load_image(ASSETS / "Fdown.png"),
        load_image(ASSETS / "Fmid.png"),
        load_image(ASSETS / "Fup.png"),
    ]

    p_surf = load_image(ASSETS / "pipe-green.png")
    tp_surf = load_image(ASSETS / "pipe-green-top.png")

    # Game state
    base_x = 0
    bird = Bird(bird_frames)
    pipes = []
    score = 0
    game_active = False
    game_over = False
    running = True

    # Manual timers in milliseconds
    pipe_timer = 0
    bird_anim_timer = 0
    PIPE_SPAWN_MS = 1200
    BIRD_ANIM_MS = 100

    while running:
        dt = clock.tick(FPS)
        pipe_timer += dt
        bird_anim_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if not game_active and not game_over:
                        game_active = True
                        bird.jump()
                    elif game_active:
                        bird.jump()
                    elif game_over:
                        game_active = True
                        game_over = False
                        pipes = []
                        bird = Bird(bird_frames)
                        score = 0
                        base_x = 0
                        pipe_timer = 0
                        bird_anim_timer = 0
                        bird.jump()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_active and not game_over:
                    game_active = True
                    bird.jump()
                elif game_active:
                    bird.jump()
                elif game_over:
                    game_active = True
                    game_over = False
                    pipes = []
                    bird = Bird(bird_frames)
                    score = 0
                    base_x = 0
                    pipe_timer = 0
                    bird_anim_timer = 0
                    bird.jump()

        if bird_anim_timer >= BIRD_ANIM_MS:
            if game_active:
                bird.animate()
            bird_anim_timer = 0

        if pipe_timer >= PIPE_SPAWN_MS:
            if game_active:
                pipes.append(Pipe(SCREEN_WIDTH + 50, p_surf, tp_surf))
            pipe_timer = 0

        # Draw background
        screen.blit(bg_surface, (0, 0))

        if game_active:
            base_x -= PIPE_SPEED
            if base_x <= -SCREEN_WIDTH:
                base_x = 0

            bird.apply_gravity()

            for pipe in pipes:
                pipe.update()

                if bird.rect.colliderect(pipe.bottom_rect) or bird.rect.colliderect(pipe.top_rect):
                    game_active = False
                    game_over = True

                if not pipe.scored and pipe.x < bird.rect.left:
                    score += 1
                    pipe.scored = True

            if bird.rect.top <= 0 or bird.rect.bottom >= GROUND_Y:
                game_active = False
                game_over = True

            pipes = [p for p in pipes if p.x > -60]

        for pipe in pipes:
            pipe.draw(screen)

        # Ground
        screen.blit(base_surface, (base_x, GROUND_Y))
        screen.blit(base_surface, (base_x + SCREEN_WIDTH, GROUND_Y))

        # Bird
        bird.draw(screen)

        # UI
        if not game_active and not game_over:
            screen.blit(
                msg_surface,
                (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2, 80),
            )
            start_text = small_font.render("Press Space or Click", True, (255, 255, 255))
            screen.blit(
                start_text,
                (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 160),
            )

        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            screen.blit(
                over_surface,
                (SCREEN_WIDTH // 2 - over_surface.get_width() // 2, 170),
            )

            score_surf = score_font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(
                score_surf,
                (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 240),
            )

            restart_text = small_font.render("Press Space or Click to Restart", True, (255, 255, 255))
            screen.blit(
                restart_text,
                (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 280),
            )
        else:
            score_txt = score_font.render(str(score), True, (255, 255, 255))
            screen.blit(
                score_txt,
                (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, 50),
            )

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())