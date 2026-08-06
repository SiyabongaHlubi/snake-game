"""
Basic Snake Game using Pygame
================================
A classic Snake game with arrow key controls, food spawning, score tracking,
high scores, difficulty levels, and a start menu.

Controls:
  - Arrow keys or WASD to move the snake
  - R to restart after game over

Requirements:
  pip install pygame
"""

import pygame
import random
import sys
import json
import os
import pygame.mixer

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
GRID_SIZE = 25          # Size of each grid cell in pixels
TILES_PER_ROW = SCREEN_WIDTH // GRID_SIZE
TILES_PER_COL = SCREEN_HEIGHT // GRID_SIZE

# High score file path - use absolute path for persistence
HIGH_SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snake_high_scores.json")

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 50, 50)
GRAY = (100, 100, 100)
BLUE = (50, 100, 200)
DARK_BLUE = (20, 20, 60)
PURPLE = (40, 20, 60)
DARK_GRAY = (30, 30, 30)
YELLOW = (255, 200, 0)
ORANGE = (255, 140, 0)

# --- Initialize Pygame ---
pygame.init()

# Make screen resolution adjustable
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

# --- Fonts ---
font_title = pygame.font.SysFont("arial", 36, bold=True)
font_score = pygame.font.SysFont("arial", 20)
font_small = pygame.font.SysFont("arial", 16)

# --- Difficulty Settings ---
DIFFICULTIES = {
    "Easy":   {"fps": 4,  "grid_size": 25},
    "Normal": {"fps": 7,  "grid_size": 25},
    "Hard":   {"fps": 12, "grid_size": 25},
}

# --- Background Color Options ---
BACKGROUNDS = {
    "Black": BLACK,
    "Dark Blue": DARK_BLUE,
    "Purple": PURPLE,
    "Dark Gray": DARK_GRAY,
}

# --- Snake Color Options ---
SNAKE_COLORS = {
    "Green": GREEN,
    "Blue": BLUE,
    "Red": RED,
    "Yellow": YELLOW,
    "Cyan": (0, 200, 200),
    "Magenta": (200, 0, 200),
    "Orange": ORANGE,
}

# --- Colorblind-Friendly Color Options ---
COLORBLIND_COLORS = {
    "Blue-Green": (0, 150, 150),
    "Orange-Yellow": (255, 180, 50),
    "Pink": (255, 100, 150),
    "Purple-Blue": (100, 50, 200),
}

# --- High Score Manager ---
class HighScoreManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.scores = self.load_scores()

    def load_scores(self):
        """Load high scores from file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {"Easy": 0, "Normal": 0, "Hard": 0}

    def save_scores(self):
        """Save high scores to file."""
        with open(self.filepath, "w") as f:
            json.dump(self.scores, f, indent=2)

    def update_score(self, difficulty, score):
        """Update high score if current score is higher."""
        if self.scores[difficulty] < score:
            self.scores[difficulty] = score
            self.save_scores()

# --- Game Class ---
class SnakeGame:
    def __init__(self):
        self.state = "menu"  # menu, playing, game_over, settings, paused
        self.menu_selected_difficulty_index = 1  # Default to Normal (0=Easy, 1=Normal, 2=Hard)
        self.menu_selected_background_index = 0  # Default to Black (0=Black, 1=Dark Blue, 2=Purple, 3=Dark Gray)
        self.menu_selected_main_index = 0  # Main menu selection (0=Difficulty, 1=Background, 2=Settings, 3=Quit)
        self.background_color = BLACK
        
        # Settings
        self.snake_color = SNAKE_COLORS["Green"]
        self.sound_enabled = True
        self.show_grid = True
        self.colorblind_mode = False
        self.menu_selected_setting_index = 0  # For settings navigation

    def reset(self):
        """Reset the snake, food, and score."""
        # Set background color from menu selection
        background_names = list(BACKGROUNDS.keys())
        self.background_color = BACKGROUNDS[background_names[self.menu_selected_background_index]]
        
        self.snake = [{"x": 5, "y": 5}, {"x": 4, "y": 5}, {"x": 3, "y": 5}]  # Initial snake
        self.direction = {"x": 1, "y": 0}  # Moving right
        self.next_direction = {"x": 1, "y": 0}
        self.food = None
        self.score = 0
        self.game_over = False
        self.running = True
        self.spawn_food()
    
    def screen_resize(self, width, height):
        """Handle screen resizing."""
        global screen
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        return True  # Continue running

    def spawn_food(self):
        """Spawn food at a random grid position, not on the snake."""
        while True:
            x = random.randint(0, TILES_PER_ROW - 1)
            y = random.randint(0, TILES_PER_COL - 1)

            # Make sure food doesn't spawn on the snake
            if not any(segment["x"] == x and segment["y"] == y for segment in self.snake):
                self.food = {"x": x, "y": y}
                break

    def handle_input(self):
        """Process player input."""
        global SCREEN_WIDTH, SCREEN_HEIGHT, TILES_PER_ROW, TILES_PER_COL, screen
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # Signal to exit
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                TILES_PER_ROW = SCREEN_WIDTH // GRID_SIZE
                TILES_PER_COL = SCREEN_HEIGHT // GRID_SIZE
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    # Main menu navigation
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menu_selected_main_index = (self.menu_selected_main_index - 1) % 3
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_selected_main_index = (self.menu_selected_main_index + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selected_main_index == 0:  # Start Game
                            difficulties = list(DIFFICULTIES.keys())
                            self.difficulty = difficulties[self.menu_selected_difficulty_index]
                            self.reset()
                            self.state = "playing"
                        elif self.menu_selected_main_index == 1:  # Settings
                            self.state = "settings"
                            self.menu_selected_setting_index = 0
                        elif self.menu_selected_main_index == 2:  # Quit
                            return False
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        return False  # Quit game
                
                elif self.state == "settings":
                    # Settings menu navigation
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menu_selected_setting_index = (self.menu_selected_setting_index - 1) % 6
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_selected_setting_index = (self.menu_selected_setting_index + 1) % 6
                    elif event.key == pygame.K_RETURN:
                        # Toggle the selected setting
                        if self.menu_selected_setting_index == 0:  # Difficulty
                            difficulties = list(DIFFICULTIES.keys())
                            current_index = difficulties.index(self.difficulty)
                            self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
                        elif self.menu_selected_setting_index == 1:  # Background
                            backgrounds = list(BACKGROUNDS.keys())
                            current_index = backgrounds.index([k for k, v in BACKGROUNDS.items() if v == self.background_color][0])
                            self.background_color = BACKGROUNDS[backgrounds[(current_index + 1) % len(backgrounds)]]
                        elif self.menu_selected_setting_index == 2:  # Snake Color
                            color_palette = COLORBLIND_COLORS if self.colorblind_mode else SNAKE_COLORS
                            colors = list(color_palette.values())
                            try:
                                current_index = colors.index(self.snake_color)
                            except ValueError:
                                current_index = 0
                            self.snake_color = colors[(current_index + 1) % len(colors)]
                        elif self.menu_selected_setting_index == 3:  # Sound
                            self.sound_enabled = not self.sound_enabled
                        elif self.menu_selected_setting_index == 4:  # Grid
                            self.show_grid = not self.show_grid
                        elif self.menu_selected_setting_index == 5:  # Colorblind Mode
                            self.colorblind_mode = not self.colorblind_mode
                            # Reset snake color to appropriate palette
                            if self.colorblind_mode:
                                self.snake_color = COLORBLIND_COLORS["Blue-Green"]
                            else:
                                self.snake_color = SNAKE_COLORS["Green"]
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"  # Return to main menu

                elif self.state == "game_over":
                    if event.key == pygame.K_r:
                        self.reset()
                        self.state = "playing"
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                    elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                        return False  # Quit game

                elif self.state == "playing":
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        self.state = "menu"  # Return to menu instead of quitting
                    elif event.key == pygame.K_p:
                        self.state = "paused"  # Pause game

                elif self.state == "paused":
                    if event.key == pygame.K_p:
                        self.state = "playing"  # Resume game
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"  # Return to menu

                elif self.state == "playing" and not self.game_over:
                    # Game controls
                    if self.direction["y"] == 0 and event.key in (pygame.K_UP, pygame.K_w):
                        self.next_direction = {"x": 0, "y": -1}

                    elif self.direction["y"] == 0 and event.key in (pygame.K_DOWN, pygame.K_s):
                        self.next_direction = {"x": 0, "y": 1}

                    elif self.direction["x"] == 0 and event.key in (pygame.K_LEFT, pygame.K_a):
                        self.next_direction = {"x": -1, "y": 0}

                    elif self.direction["x"] == 0 and event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.next_direction = {"x": 1, "y": 0}
        
        return True  # Continue running

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        # Apply the next direction
        self.direction = self.next_direction

        # Calculate new head position
        head = self.snake[0]
        new_head = {
            "x": head["x"] + self.direction["x"],
            "y": head["y"] + self.direction["y"],
        }

        # Check wall collision
        if (new_head["x"] < 0 or new_head["x"] >= TILES_PER_ROW or
                new_head["y"] < 0 or new_head["y"] >= TILES_PER_COL):
            self.game_over = True
            self.high_scoresmanager.update_score(self.difficulty, self.score)
            return

        # Check self collision
        if any(segment["x"] == new_head["x"] and segment["y"] == new_head["y"]
               for segment in self.snake):
            self.game_over = True
            self.high_scoresmanager.update_score(self.difficulty, self.score)
            return

        # Add new head to snake
        self.snake.insert(0, new_head)

        # Check if food is eaten
        if self.food and new_head["x"] == self.food["x"] and new_head["y"] == self.food["y"]:
            self.score += 10
            self.spawn_food()
        else:
            # Remove tail if not eating food
            self.snake.pop()

    def draw_menu(self):
        """Draw the main menu."""
        screen.fill(BLACK)

        # Draw title
        title = font_title.render("🐍 Snake Game", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 6))

        # Draw difficulty selection
        diff_color = (100, 200, 150) if self.menu_section == "difficulty" else WHITE
        diff_text = font_score.render("Select Difficulty:", True, diff_color)
        screen.blit(diff_text, (SCREEN_WIDTH // 2 - diff_text.get_width() // 2, SCREEN_HEIGHT // 6 + 50))

        # Draw difficulty buttons
        button_height = 40
        start_y = SCREEN_HEIGHT // 6 + 90

        for i, (difficulty, settings) in enumerate(DIFFICULTIES.items()):
            x = SCREEN_WIDTH // 2 - 160
            y = start_y + i * (button_height + 10)

            # Button background
            if i == self.menu_selected_difficulty_index:
                pygame.draw.rect(screen, (100, 200, 150), (x, y, 320, button_height))
            else:
                pygame.draw.rect(screen, BLUE, (x, y, 320, button_height))

            # Button text
            diff_text = font_score.render(difficulty, True, WHITE)
            screen.blit(diff_text, (x + 10, y + 5))

        # Draw background selection
        bg_color = (100, 200, 150) if self.menu_section == "background" else WHITE
        bg_text = font_score.render("Select Background:", True, bg_color)
        screen.blit(bg_text, (SCREEN_WIDTH // 2 - bg_text.get_width() // 2, start_y + 4 * (button_height + 10) + 20))

        bg_start_y = start_y + 4 * (button_height + 10) + 60
        for i, (bg_name, bg_color) in enumerate(BACKGROUNDS.items()):
            x = SCREEN_WIDTH // 2 - 160
            y = bg_start_y + i * (button_height + 10)

            # Button background with actual color preview
            if i == self.menu_selected_background_index:
                pygame.draw.rect(screen, (100, 200, 150), (x, y, 320, button_height))
                pygame.draw.rect(screen, bg_color, (x + 2, y + 2, 60, button_height - 4))
            else:
                pygame.draw.rect(screen, bg_color, (x, y, 320, button_height))
                pygame.draw.rect(screen, WHITE, (x, y, 320, button_height), 2)

            # Button text
            text_color = WHITE if i == self.menu_selected_background_index else WHITE
            bg_label = font_score.render(bg_name, True, text_color)
            screen.blit(bg_label, (x + 70, y + 5))

        # Draw settings selection
        settings_color = (100, 200, 150) if self.menu_section == "settings" else WHITE
        settings_text = font_score.render("Settings (Enter to toggle):", True, settings_color)
        screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, bg_start_y + 4 * (button_height + 10) + 20))

        settings_start_y = bg_start_y + 4 * (button_height + 10) + 60
        # Get current snake color name
        snake_color_name = "Green"
        color_palette = COLORBLIND_COLORS if self.colorblind_mode else SNAKE_COLORS
        for name, color in color_palette.items():
            if color == self.snake_color:
                snake_color_name = name
                break
        
        settings_options = [
            f"Snake Color: {snake_color_name}",
            f"Sound: {'On' if self.sound_enabled else 'Off'}",
            f"Grid: {'On' if self.show_grid else 'Off'}",
            f"Colorblind Mode: {'On' if self.colorblind_mode else 'Off'}",
        ]
        
        for i, option in enumerate(settings_options):
            x = SCREEN_WIDTH // 2 - 160
            y = settings_start_y + i * (button_height + 10)

            # Button background
            if i == self.menu_selected_setting_index:
                pygame.draw.rect(screen, (100, 200, 150), (x, y, 320, button_height))
            else:
                pygame.draw.rect(screen, BLUE, (x, y, 320, button_height))

            # Button text
            option_label = font_score.render(option, True, WHITE)
            screen.blit(option_label, (x + 10, y + 5))

        # Instructions
        inst_text = font_small.render("TAB: Switch Section • Arrow Keys: Select • Enter: Start/Toggle • Q/ESC: Quit", True, GRAY)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, SCREEN_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(30)

    def draw_paused(self):
        """Draw the pause screen."""
        # Draw the current game state with overlay
        self.draw()
        
        # Add pause overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = font_title.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 3))
        
        resume_text = font_score.render("Press P to Resume • ESC: Menu • Q: Quit", True, WHITE)
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 3 + 50))
        
        pygame.display.flip()
        clock.tick(30)

    def draw(self):
        """Render the game."""
        # Clear screen with selected background color
        screen.fill(self.background_color)

        # Draw grid (optional, subtle) - adjust color based on background and colorblind mode
        if self.show_grid:
            if self.colorblind_mode:
                grid_color = (100, 100, 100) if self.background_color == BLACK else (80, 80, 80)
            else:
                grid_color = (80, 80, 80) if self.background_color == BLACK else (60, 60, 60)
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, grid_color, (0, y), (SCREEN_WIDTH, y))

        # Draw food
        if self.food:
            fx = self.food["x"] * GRID_SIZE + GRID_SIZE // 2
            fy = self.food["y"] * GRID_SIZE + GRID_SIZE // 2
            pygame.draw.circle(screen, RED, (fx, fy), GRID_SIZE // 2 - 1)
            
            # Add pattern for colorblind accessibility
            if self.colorblind_mode:
                # Draw X pattern in food
                pygame.draw.line(screen, WHITE, (fx - 5, fy - 5), (fx + 5, fy + 5), 2)
                pygame.draw.line(screen, WHITE, (fx + 5, fy - 5), (fx - 5, fy + 5), 2)

        # Draw snake
        for i, segment in enumerate(self.snake):
            x = segment["x"] * GRID_SIZE + GRID_SIZE // 2
            y = segment["y"] * GRID_SIZE + GRID_SIZE // 2

            if i == 0:
                # Head uses selected color, body is darker version
                color = self.snake_color
            else:
                # Create darker version of snake color for body
                color = tuple(max(0, c - 50) for c in self.snake_color)

            pygame.draw.rect(screen, color, (x - GRID_SIZE // 2 + 1,
                                            y - GRID_SIZE // 2 + 1,
                                            GRID_SIZE - 2,
                                            GRID_SIZE - 2))
            
            # Add pattern for colorblind accessibility on head
            if i == 0 and self.colorblind_mode:
                # Draw eyes pattern
                eye_offset = GRID_SIZE // 4
                pygame.draw.circle(screen, WHITE, (x - eye_offset, y - eye_offset), 3)
                pygame.draw.circle(screen, WHITE, (x + eye_offset, y - eye_offset), 3)

        # Draw score
        score_text = font_score.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw difficulty indicator
        diff_text = font_small.render(f"Difficulty: {self.difficulty}", True, BLUE)
        screen.blit(diff_text, (SCREEN_WIDTH - 200, 10))

        # Draw high scores
        hs_text = font_small.render(
            f"High Scores: E:{self.high_scoresmanager.scores['Easy']} N:{self.high_scoresmanager.scores['Normal']} H:{self.high_scoresmanager.scores['Hard']}",
            True, GRAY
        )
        screen.blit(hs_text, (10, 35))

        # Draw controls info
        controls_text = font_small.render("P: Pause • ESC: Menu • Q: Quit", True, GRAY)
        screen.blit(controls_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 25))
        
        # Draw colorblind mode indicator
        if self.colorblind_mode:
            cb_text = font_small.render("♿ Colorblind Mode", True, YELLOW)
            screen.blit(cb_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 45))

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            game_over_text = font_title.render("Game Over!", True, RED)
            score_text = font_score.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = font_score.render("Press R to Restart • ESC: Menu • Q: Quit", True, WHITE)

            screen.blit(
                game_over_text,
                (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                 SCREEN_HEIGHT // 3)
            )
            screen.blit(
                score_text,
                (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                 SCREEN_HEIGHT // 3 + 40)
            )
            screen.blit(
                restart_text,
                (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                 SCREEN_HEIGHT // 3 + 80)
            )

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        self.reset()
        self.state = "menu"

        while self.running:
            if self.state == "menu":
                # Show menu and wait for player to start
                if not self.handle_input():
                    break
                self.draw_menu()

            elif self.state == "playing":
                self.handle_input()
                self.update()
                self.draw()
                
                # Apply difficulty-based frame rate
                fps = DIFFICULTIES[self.difficulty]["fps"]
                clock.tick(fps)

                # Check for game over
                if self.game_over:
                    self.state = "game_over"

            elif self.state == "game_over":
                # Show game over screen and wait for restart
                if not self.handle_input():
                    break
                self.draw()

            elif self.state == "paused":
                # Show pause screen
                if not self.handle_input():
                    break
                self.draw_paused()

        pygame.quit()


# --- Run the Game ---
if __name__ == "__main__":
    game = SnakeGame()
    game.running = True

    # Initialize high score manager
    game.high_scoresmanager = HighScoreManager(HIGH_SCORE_FILE)

    # Start the game
    game.run()