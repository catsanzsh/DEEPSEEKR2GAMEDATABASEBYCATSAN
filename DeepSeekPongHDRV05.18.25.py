import pygame
import sys
import array

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 600, 400
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60
BALL_SIZE = 10
PADDLE_SPEED = 5
BALL_BASE_SPEED = 5
AI_REACTION = 0.4  # Lower is faster, higher is slower

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Create window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong GB - Mouse vs AI")

# Initialize sound system
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

def generate_wave(frequency, duration=0.1, waveform='square'):
    sample_rate = pygame.mixer.get_init()[0]
    period = int(sample_rate / frequency)
    samples = int(sample_rate * duration)
    buf = array.array('h')
    
    for i in range(samples):
        if waveform == 'square':
            val = 32767 if (i % period) < (period // 2) else -32767
        elif waveform == 'sawtooth':
            val = int((i % period) * (32767 * 2 / period) - 32767)
        buf.append(int(val * 0.1))  # Reduce volume
    
    return pygame.mixer.Sound(buffer=buf)

# Game Boy-style sound effects
paddle_sound = generate_wave(1319, 0.08)   # E6 note
wall_sound = generate_wave(659, 0.06)      # E5 note
score_sound = generate_wave(330, 0.3)      # E4 note

# Clock for FPS control
clock = pygame.time.Clock()

# Initialize game objects
left_paddle = pygame.Rect(30, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 30 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, 
                          PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

ball_speed_x = BALL_BASE_SPEED
ball_speed_y = 0  # Start with horizontal trajectory

# Scores
left_score = 0
right_score = 0

# Font for scoring
font = pygame.font.Font(None, 74)

def reset_ball(direction):
    ball.center = (WIDTH//2, HEIGHT//2)
    return direction * BALL_BASE_SPEED, 0  # Reset to horizontal trajectory

# Game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Mouse control for left paddle
    mouse_y = pygame.mouse.get_pos()[1]
    left_paddle.centery = mouse_y
    # Keep paddle on screen
    if left_paddle.top < 0:
        left_paddle.top = 0
    elif left_paddle.bottom > HEIGHT:
        left_paddle.bottom = HEIGHT

    # AI control for right paddle
    if ball_speed_x > 0:  # Only move when ball is approaching
        # Predict ball position with simple tracking
        target_y = ball.centery + (ball_speed_y * AI_REACTION)
        # Keep prediction within screen bounds
        target_y = max(min(target_y, HEIGHT), 0)
        
        if right_paddle.centery < target_y and right_paddle.bottom < HEIGHT:
            right_paddle.y += PADDLE_SPEED
        elif right_paddle.centery > target_y and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED

    # Ball movement
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Ball collision with walls
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1
        wall_sound.play()

    # Ball collision with paddles
    paddle_hit = False
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        paddle = left_paddle if ball.colliderect(left_paddle) else right_paddle
        offset = (ball.centery - paddle.centery) / (PADDLE_HEIGHT / 2)
        ball_speed_x = -ball_speed_x * 1.1  # Speed up after paddle hit
        ball_speed_y = BALL_BASE_SPEED * offset * 1.5  # Dynamic angle based on hit position
        paddle_hit = True
        paddle_sound.play()

    # Scoring
    if ball.left <= 0:
        right_score += 1
        ball_speed_x, ball_speed_y = reset_ball(1)
        score_sound.play()
    if ball.right >= WIDTH:
        left_score += 1
        ball_speed_x, ball_speed_y = reset_ball(-1)
        score_sound.play()

    # Drawing
    screen.fill(BLACK)
    
    # Draw center line (dashed)
    for y in range(0, HEIGHT, HEIGHT//20):
        if y % 2 == 0:
            pygame.draw.rect(screen, WHITE, (WIDTH//2 - 2, y, 4, HEIGHT//40))
    
    # Draw paddles and ball
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    
    # Draw scores
    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (WIDTH//4, 20))
    screen.blit(right_text, (WIDTH*3//4 - right_text.get_width(), 20))

    # Update display
    pygame.display.flip()
    
    # Maintain 60 FPS
    clock.tick(60)
