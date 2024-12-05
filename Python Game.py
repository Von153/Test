import pygame
import sys
import os
import time

# Initialize Pygame
pygame.init()

# Set up screen dimensions and colors
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)  # Background color

# Set up the display with resizable option
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Presence Gauge Game")
clock = pygame.time.Clock()

# Load font
font_path = pygame.font.match_font('arial')
button_font = pygame.font.Font(font_path, 16)
instruction_font = pygame.font.Font(font_path, 16)

# Load character sprites based on presence levels
character_imgs = {
    'low': pygame.image.load('assets/character_sad.png'),
    'medium': pygame.image.load('assets/character_neutral.png'),
    'high': pygame.image.load('assets/character_happy.png')
}

# Scale character images
for key in character_imgs:
    character_imgs[key] = pygame.transform.scale(character_imgs[key], (100, 150))

# Character position
character_x, character_y = WIDTH // 2 - 50, HEIGHT // 2 - 75

# Game states
MENU = 'menu'
PLAYING = 'playing'
PAUSED = 'paused'
GAME_OVER = 'game_over'
INSTRUCTIONS = 'instructions'

game_state = MENU

# Presence Meter class with time-based decrease
class PresenceMeter:
    def __init__(self):
        self.level = 50  # Initial presence level (0-100)
        self.last_update = pygame.time.get_ticks()
        self.decrease_rate = 5  # Decrease 5 units every 5 seconds

    def increase(self, amount):
        self.level = min(100, self.level + amount)

    def decrease(self, amount):
        self.level = max(0, self.level - amount)

    def update(self):
        # Decrease presence over time
        now = pygame.time.get_ticks()
        if now - self.last_update > 5000:  # Every 5 seconds
            self.decrease(self.decrease_rate)
            self.last_update = now

    def draw(self, screen):
        # Draw gauge background and level
        pygame.draw.rect(screen, BLACK, (50, 50, 300, 30))
        pygame.draw.rect(screen, GREEN, (50, 50, self.level * 3, 30))
        # Draw presence text
        presence_text = instruction_font.render(f"Presence: {int(self.level)}%", True, BLACK)
        screen.blit(presence_text, (50, 85))

# Action buttons with hover effect and keyboard controls
class ActionButton:
    def __init__(self, x, y, text, effect, key=None):
        self.rect = pygame.Rect(x, y, 200, 50)
        self.text = text
        self.effect = effect
        self.base_color = BLACK
        self.hover_color = (50, 50, 50)
        self.current_color = self.base_color
        self.text_surf = button_font.render(text, True, WHITE)
        self.key = key  # For keyboard controls

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect)
        screen.blit(self.text_surf, (self.rect.x + 10, self.rect.y + 10))

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Set up presence meter and actions
presence_meter = PresenceMeter()
meditate_action = ActionButton(100, 400, "Meditate (+10)", 10, key=pygame.K_m)
phone_action = ActionButton(400, 400, "Check Phone (-15)", -15, key=pygame.K_p)
read_action = ActionButton(100, 470, "Read a Book (+20)", 20, key=pygame.K_r)
tv_action = ActionButton(400, 470, "Watch TV (-10)", -10, key=pygame.K_t)
actions = [meditate_action, phone_action, read_action, tv_action]

# Scoring system
start_time = None
end_time = None
high_scores = []

# Load high scores from file
def load_high_scores():
    global high_scores
    if os.path.exists('high_scores.txt'):
        with open('high_scores.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                high_scores.append(float(line.strip()))

def save_high_score(score):
    high_scores.append(score)
    high_scores.sort()
    with open('high_scores.txt', 'w') as f:
        for score in high_scores[:5]:  # Keep top 5 scores
            f.write(f"{score}\n")

# Instructions screen
def show_instructions():
    screen.fill(WHITE)
    instructions = [
        "Welcome to the Presence Gauge Game!",
        "Your goal is to keep your presence level high.",
        "Use the actions to increase or decrease your presence.",
        "Actions:",
        "M - Meditate (+10)",
        "P - Check Phone (-15)",
        "R - Read a Book (+20)",
        "T - Watch TV (-10)",
        "Press any key to start..."
    ]
    y_offset = 100
    for line in instructions:
        text_surf = instruction_font.render(line, True, BLACK)
        rect = text_surf.get_rect(center=(WIDTH // 2, y_offset))
        screen.blit(text_surf, rect)
        y_offset += 40
    pygame.display.flip()

# Menu screen
def show_menu():
    screen.fill(WHITE)
    title_surf = button_font.render("Presence Gauge Game", True, BLACK)
    rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(title_surf, rect)
    start_text = instruction_font.render("Press Enter to Start", True, BLACK)
    rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(start_text, rect)
    instr_text = instruction_font.render("Press I for Instructions", True, BLACK)
    rect = instr_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(instr_text, rect)
    pygame.display.flip()

# Game over screen
def show_game_over():
    screen.fill(WHITE)
    if presence_meter.level <= 0:
        message = "Game Over! You lost."
    else:
        message = "Congratulations! You won."
    message_surf = button_font.render(message, True, BLACK)
    rect = message_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(message_surf, rect)
    if end_time and start_time:
        total_time = end_time - start_time
        time_surf = instruction_font.render(f"Time: {total_time:.2f} seconds", True, BLACK)
        rect = time_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(time_surf, rect)
    high_scores_surf = instruction_font.render("High Scores:", True, BLACK)
    rect = high_scores_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(high_scores_surf, rect)
    y_offset = HEIGHT // 2 + 80
    for score in high_scores[:5]:
        score_surf = instruction_font.render(f"{score:.2f} seconds", True, BLACK)
        rect = score_surf.get_rect(center=(WIDTH // 2, y_offset))
        screen.blit(score_surf, rect)
        y_offset += 30
    restart_text = instruction_font.render("Press Enter to Restart or Q to Quit", True, BLACK)
    rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    screen.blit(restart_text, rect)
    pygame.display.flip()

# Main game loop
load_high_scores()
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            # Update character position
            character_x, character_y = WIDTH // 2 - 50, HEIGHT // 2 - 75
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == PLAYING:
                    game_state = PAUSED
                elif game_state == PAUSED:
                    game_state = PLAYING
            if game_state == MENU:
                if event.key == pygame.K_RETURN:
                    game_state = PLAYING
                    start_time = None
                    end_time = None
                    presence_meter = PresenceMeter()
                elif event.key == pygame.K_i:
                    game_state = INSTRUCTIONS
            elif game_state == INSTRUCTIONS:
                game_state = MENU
            elif game_state == GAME_OVER:
                if event.key == pygame.K_RETURN:
                    game_state = MENU
                elif event.key == pygame.K_q:
                    running = False
                    pygame.quit()
                    sys.exit()
            elif game_state == PLAYING:
                for action in actions:
                    if event.key == action.key:
                        if action.effect > 0:
                            presence_meter.increase(action.effect)
                        else:
                            presence_meter.decrease(-action.effect)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == PLAYING:
                for action in actions:
                    if action.is_clicked(event.pos):
                        if action.effect > 0:
                            presence_meter.increase(action.effect)
                        else:
                            presence_meter.decrease(-action.effect)

    if game_state == MENU:
        show_menu()
    elif game_state == INSTRUCTIONS:
        show_instructions()
    elif game_state == PLAYING:
        if start_time is None:
            start_time = time.time()

        screen.fill(LIGHT_BLUE)  # Fill background with solid color

        # Update presence meter
        presence_meter.update()

        # Draw character based on presence level
        if presence_meter.level <= 33:
            character_img = character_imgs['low']
        elif presence_meter.level <= 66:
            character_img = character_imgs['medium']
        else:
            character_img = character_imgs['high']
        screen.blit(character_img, (character_x, character_y))

        # Draw presence meter
        presence_meter.draw(screen)

        # Draw action buttons and check for hover
        mouse_pos = pygame.mouse.get_pos()
        for action in actions:
            if action.is_hovered(mouse_pos):
                action.current_color = action.hover_color
            else:
                action.current_color = action.base_color
            action.draw(screen)

        # Check for game over conditions
        if presence_meter.level <= 0 or presence_meter.level >= 100:
            end_time = time.time()
            total_time = end_time - start_time
            save_high_score(total_time)
            game_state = GAME_OVER

        # Update display
        pygame.display.flip()
        clock.tick(30)  # Run at 30 frames per second

    elif game_state == PAUSED:
        screen.fill(WHITE)
        pause_text = button_font.render("Game Paused", True, BLACK)
        rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(pause_text, rect)
        resume_text = instruction_font.render("Press ESC to Resume", True, BLACK)
        rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(resume_text, rect)
        pygame.display.flip()

    elif game_state == GAME_OVER:
        show_game_over()

pygame.quit()
