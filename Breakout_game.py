import pygame
import random
import sys
import math

pygame.init()


WIDTH, HEIGHT = 600, 650
FPS = 60

# colours
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (40,  40,  40)
DKGRAY = (20,  20,  20)


ROW_COLORS = [
    (220,  50,  50),   # red
    (220, 130,  40),   # orange
    (210, 200,  40),   # yellow
    ( 80, 180,  50),   # green
    ( 50, 160, 220),   # blue
    (160,  60, 220),   # purple
]


BRICK_ROWS    = 6
BRICK_COLS    = 10
BRICK_W       = 54
BRICK_H       = 18
BRICK_PADDING = 3
BRICK_TOP     = 60          

# paddle
PADDLE_W  = 90
PADDLE_H  = 12
PADDLE_Y  = HEIGHT - 50

# ball
BALL_R    = 10
BALL_SPEED = 6              


MAX_LIVES = 3

class Brick(pygame.sprite.Sprite):
    def __init__(self, col, row):
        super().__init__()

        self.color  = ROW_COLORS[row % len(ROW_COLORS)]
        self.points = (BRICK_ROWS - row) * 10   

        self.image = pygame.Surface((BRICK_W, BRICK_H))
        self.image.fill(self.color)
        
        pygame.draw.rect(self.image, WHITE, (0, 0, BRICK_W, 3))
        pygame.draw.rect(self.image, (0, 0, 0, 60), (0, BRICK_H - 3, BRICK_W, 3))

        x = BRICK_PADDING + col * (BRICK_W + BRICK_PADDING)
        y = BRICK_TOP + row * (BRICK_H + BRICK_PADDING)
        self.rect = self.image.get_rect(topleft=(x, y))



class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((PADDLE_W, PADDLE_H), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (200, 200, 210), (0, 0, PADDLE_W, PADDLE_H), border_radius=6)
        pygame.draw.rect(self.image, WHITE, (0, 0, PADDLE_W, 4), border_radius=6)

        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, PADDLE_Y))

    def update(self):
        mx = pygame.mouse.get_pos()[0]
        self.rect.centerx = mx
        
        self.rect.left  = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)



class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((BALL_R * 2, BALL_R * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (BALL_R, BALL_R), BALL_R)
        pygame.draw.circle(self.image, (200, 200, 255), (BALL_R - 3, BALL_R - 3), 4)

        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        
        angle = random.uniform(210, 330)          
        rad   = math.radians(angle)
        self.vx = BALL_SPEED * math.cos(rad)
        self.vy = BALL_SPEED * math.sin(rad)

        
        self.fx = float(self.rect.centerx)
        self.fy = float(self.rect.centery)

    
    def update(self):
        self.fx += self.vx
        self.fy += self.vy

        
        if self.fx - BALL_R <= 0:
            self.fx = BALL_R
            self.vx = abs(self.vx)
        elif self.fx + BALL_R >= WIDTH:
            self.fx = WIDTH - BALL_R
            self.vx = -abs(self.vx)

        
        if self.fy - BALL_R <= 0:
            self.fy = BALL_R
            self.vy = abs(self.vy)

        self.rect.center = (int(self.fx), int(self.fy))

    
    def off_screen(self):
        return self.fy - BALL_R > HEIGHT


    def bounce_paddle(self, paddle_rect):

        relative = (self.fx - paddle_rect.centerx) / (paddle_rect.width / 2)
        relative = max(-1.0, min(1.0, relative))   

        # map to an exit angle between 150° and 30° (always going upward)
        angle = math.radians(150 - relative * 60)  
        speed = math.hypot(self.vx, self.vy)       

        self.vx =  speed * math.cos(angle)
        self.vy = -abs(speed * math.sin(angle))    
        self.fy = paddle_rect.top - BALL_R         

    
    def bounce_brick(self, brick_rect):
        
        overlap_x = min(self.rect.right, brick_rect.right) - max(self.rect.left, brick_rect.left)
        overlap_y = min(self.rect.bottom, brick_rect.bottom) - max(self.rect.top, brick_rect.top)

        if overlap_x < overlap_y:
            self.vx = -self.vx
        else:
            self.vy = -self.vy



def draw_text(surface, text, size, x, y, color=WHITE, center=False):
    font = pygame.font.SysFont("consolas", size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)


# ── build the brick grid ──
def make_bricks():
    group = pygame.sprite.Group()
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            group.add(Brick(col, row))
    return group


# ── main game function ──
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakout")
    clock  = pygame.time.Clock()
    pygame.mouse.set_visible(False)   

    # ── game state ──
    lives   = MAX_LIVES
    score   = 0
    state   = "waiting"   

    bricks  = make_bricks()
    paddle  = Paddle()
    ball    = Ball()

    paddle_group = pygame.sprite.GroupSingle(paddle)
    ball_group   = pygame.sprite.GroupSingle(ball)

    # ── game loop ──
    while True:
        clock.tick(FPS)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                
                if event.key == pygame.K_SPACE:
                    if state in ("waiting", "lost_life"):
                        state = "playing"
                    elif state in ("game_over", "win"):
                        
                        lives  = MAX_LIVES
                        score  = 0
                        bricks = make_bricks()
                        ball   = Ball()
                        ball_group.add(ball)
                        state  = "waiting"

        # ── update ──
        paddle_group.update()

        if state == "playing":
            ball_group.update()

        
            if pygame.sprite.spritecollide(ball, paddle_group, False):
                ball.bounce_paddle(paddle.rect)

            
            hit_bricks = pygame.sprite.spritecollide(ball, bricks, False)
            if hit_bricks:
                
                ball.bounce_brick(hit_bricks[0].rect)
                for b in hit_bricks:
                    score += b.points
                    b.kill()
                
                current_speed = math.hypot(ball.vx, ball.vy)
                if current_speed < 11:
                    ball.vx *= 1.02
                    ball.vy *= 1.02

            
            if ball.off_screen():
                lives -= 1
                if lives <= 0:
                    state = "game_over"
                else:
                    state = "lost_life"
                    ball = Ball()
                    ball_group.add(ball)

            
            if len(bricks) == 0:
                state = "win"

        
        screen.fill(DKGRAY)


        bricks.draw(screen)

        
        paddle_group.draw(screen)
        if state != "game_over":
            ball_group.draw(screen)

        # HUD: score + lives
        draw_text(screen, f"Score: {score}", 18, 10, 10)
        draw_text(screen, f"Lives: {'♥ ' * lives}", 18, WIDTH - 140, 10)

        # divider line below HUD
        pygame.draw.line(screen, GRAY, (0, 38), (WIDTH, 38), 2)

        
        if state == "waiting":
            draw_text(screen, "BREAKOUT", 42, WIDTH // 2, HEIGHT // 2 - 50, center=True)
            draw_text(screen, "Move mouse to steer paddle", 16, WIDTH // 2, HEIGHT // 2 + 10, center=True)
            draw_text(screen, "SPACE to launch", 20, WIDTH // 2, HEIGHT // 2 + 45, center=True)

        elif state == "lost_life":
            draw_text(screen, f"Lives left: {lives}", 28, WIDTH // 2, HEIGHT // 2 - 20, center=True)
            draw_text(screen, "SPACE to continue", 20, WIDTH // 2, HEIGHT // 2 + 20, center=True)

        elif state == "game_over":
            draw_text(screen, "GAME OVER", 44, WIDTH // 2, HEIGHT // 2 - 40, (220, 60, 60), center=True)
            draw_text(screen, f"Final Score: {score}", 24, WIDTH // 2, HEIGHT // 2 + 10, center=True)
            draw_text(screen, "SPACE to play again", 18, WIDTH // 2, HEIGHT // 2 + 50, center=True)

        elif state == "win":
            draw_text(screen, "YOU WIN!", 48, WIDTH // 2, HEIGHT // 2 - 40, (80, 220, 100), center=True)
            draw_text(screen, f"Final Score: {score}", 24, WIDTH // 2, HEIGHT // 2 + 10, center=True)
            draw_text(screen, "SPACE to play again", 18, WIDTH // 2, HEIGHT // 2 + 50, center=True)

        pygame.display.flip()


if __name__ == "__main__":
    main()