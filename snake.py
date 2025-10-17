import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
BASE_FPS = 10
SPEED_INCREASE = 0.2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# Font
font = pygame.font.Font(None, 36)

# Color transition variables
color_cycle = [
    (0, 255, 0),    # Green
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 255, 0),  # Yellow
    (255, 165, 0),  # Orange
    (255, 0, 0),    # Red
]

class Snake:
    def __init__(self):
        self.reset()
        self.color_index = 0
        self.color_timer = 0
        self.color_change_interval = 10  # frames between color changes
        
    def reset(self):
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.score = 0
        self.grow_pending = 2  # Start with 3 segments
        self.speed = BASE_FPS  # Current game speed
        self.color_index = 0
        self.color_timer = 0
        
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_position = (head[0] + x, head[1] + y)
        
        # Check for collision with borders
        if (new_position[0] < 0 or new_position[0] >= GRID_WIDTH or 
            new_position[1] < 0 or new_position[1] >= GRID_HEIGHT):
            return False  # Game over
            
        # Check for collision with self
        if new_position in self.positions[1:]:
            return False  # Game over
            
        self.positions.insert(0, new_position)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.positions.pop()
            
        # Update color over time
        self.color_timer += 1
        if self.color_timer >= self.color_change_interval:
            self.color_index = (self.color_index + 1) % len(color_cycle)
            self.color_timer = 0
            
        return True  # Game continues
    
    def grow(self):
        self.grow_pending += 1
        self.score += 10
        # Increase speed after eating food
        self.speed += SPEED_INCREASE
    
    def render(self, surface):
        current_color = color_cycle[self.color_index]
        for i, pos in enumerate(self.positions):
            # Draw snake segment
            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if i == 0:  # Head
                pygame.draw.rect(surface, current_color, rect)
                pygame.draw.rect(surface, (max(0, current_color[0]-50), max(0, current_color[1]-50), max(0, current_color[2]-50)), rect, 1)
            else:  # Body
                # Make body a slightly darker version of the current color
                dark_color = (max(0, current_color[0]-50), max(0, current_color[1]-50), max(0, current_color[2]-50))
                pygame.draw.rect(surface, current_color, rect)
                pygame.draw.rect(surface, dark_color, rect, 1)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.randomize_position()
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    
    def render(self, surface):
        rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, RED, rect)
        pygame.draw.rect(surface, (150, 0, 0), rect, 1)

def main():
    snake = Snake()
    food = Food()
    
    # Game loop
    running = True
    game_over = False
    
    # Time-based scoring variables
    last_score_time = pygame.time.get_ticks()
    score_interval = 2000  # 2 seconds between score increments
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_SPACE:
                    snake.reset()
                    food.randomize_position()
                    game_over = False
                    # Reset time tracking when restarting
                    last_score_time = pygame.time.get_ticks()
                elif not game_over:
                    if event.key == pygame.K_UP and snake.direction != (0, 1):
                        snake.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                        snake.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                        snake.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                        snake.direction = (1, 0)
        
        if not game_over:
            # Update snake position
            if not snake.update():
                game_over = True
            
            # Check if snake ate food
            if snake.get_head_position() == food.position:
                snake.grow()
                food.randomize_position()
                # Make sure food doesn't appear on snake
                while food.position in snake.positions:
                    food.randomize_position()
            
            # Add time-based score increment
            current_time = pygame.time.get_ticks()
            if current_time - last_score_time >= score_interval:
                snake.score += 1
                last_score_time = current_time
        
        # Draw everything
        screen.fill(BLACK)
        
        snake.render(screen)
        food.render(screen)
        
        # Display score
        score_text = font.render(f"Score: {snake.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        if game_over:
            game_over_text = font.render("GAME OVER! Press SPACE to restart", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()
        clock.tick(snake.speed)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
