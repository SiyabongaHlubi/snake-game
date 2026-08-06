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

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 20          # Size of each grid cell in pixels
TILES_PER_ROW = SCREEN_WIDTH // GRID_SIZE
TILES_PER_COL = SCREEN_HEIGHT // GRID_SIZE

# High score file path
HIGH_SCORE_FILE = "snake_high_scores.json"

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (200, 50, 50)
GRAY = (100, 100, 100)
BLUE = (50, 100, 200)

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

# --- Sound Generation ---
def generate_beep(frequency, duration, volume=0.5):
    """Generate a simple beep sound using pygame.sndarray."""
    import numpy as np
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(frequency * t * 2 * np.pi) * volume
    # Convert to 16-bit signed integers
    audio = (wave * 32767).astype(np.int16)
    # Make stereo
    audio = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(audio)

try:
    eat_sound = generate_beep(440, 0.1, 0.3)  # A4 note for eating
    game_over_sound = generate_beep(220, 0.5, 0.4)  # A3 note for game over
    move_sound = generate_beep(330, 0.05, 0.1)  # E4 note for movement (subtle)
    sound_available = True
except ImportError:
    # If numpy is not available, create placeholder sounds
    eat_sound = None
    game_over_sound = None
    move_sound = None
    sound_available = False

# --- Fonts ---
font_title = pygame.font.SysFont("arial", 36, bold=True)
font_score = pygame.font.SysFont("arial", 20)
font_small = pygame.font.SysFont("arial", 16)

# --- Difficulty Settings ---
DIFFICULTIES = {
    "Easy":   {"fps": 8,  "grid_size": 20},
    "Normal": {"fps": 12, "grid_size": 20},
    "Hard":   {"fps": 18, "grid_size": 20},
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
<<<<<<< Updated upstream
        self.state = "menu"  # menu, playing, game_over, settings, paused
        self.menu_selected_difficulty_index = 1  # Default to Normal (0=Easy, 1=Normal, 2=Hard)
        self.menu_selected_main_index = 0  # Main menu selection (0=Start, 1=Settings, 2=Quit)
        self.background_color = BLACK
        self.difficulty = "Normal"  # Initialize difficulty
        
        # Settings
        self.snake_color = SNAKE_COLORS["Green"]
        self.sound_enabled = True
        self.show_grid = True
        self.colorblind_mode = False
        self.menu_selected_setting_index = 0  # For settings navigation

    def reset(self):
        """Reset the snake, food, and score."""
        # Background color is already set in settings, no need to change it
        
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
=======
        self.state = "menu"  # menu, playing, game_over

    def reset(self):
        """Reset the snake, food, and score."""
        self.difficulty = "Normal"  # Default difficulty
>>>>>>> Stashed changes

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN and not self.game_over:
                if self.direction["y"] == 0 and event.key in (pygame.K_UP, pygame.K_w):
                    self.next_direction = {"x": 0, "y": -1}

                elif self.direction["y"] == 0 and event.key in (pygame.K_DOWN, pygame.K_s):
                    self.next_direction = {"x": 0, "y": 1}

<<<<<<< Updated upstream
                elif self.state == "playing":
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        self.state = "menu"  # Return to menu instead of quitting
                    elif event.key == pygame.K_p:
                        self.state = "paused"  # Pause game
                    elif not self.game_over:
                        # Game controls
                        if self.direction["y"] == 0 and event.key in (pygame.K_UP, pygame.K_w):
                            self.next_direction = {"x": 0, "y": -1}
                        elif self.direction["y"] == 0 and event.key in (pygame.K_DOWN, pygame.K_s):
                            self.next_direction = {"x": 0, "y": 1}
                        elif self.direction["x"] == 0 and event.key in (pygame.K_LEFT, pygame.K_a):
                            self.next_direction = {"x": -1, "y": 0}
                        elif self.direction["x"] == 0 and event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.next_direction = {"x": 1, "y": 0}

                elif self.state == "paused":
                    if event.key == pygame.K_p:
                        self.state = "playing"  # Resume game
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"  # Return to menu
        
        return True  # Continue running
=======
                elif self.direction["x"] == 0 and event.key in (pygame.K_LEFT, pygame.K_a):
                    self.next_direction = {"x": -1, "y": 0}

                elif self.direction["x"] == 0 and event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.next_direction = {"x": 1, "y": 0}
>>>>>>> Stashed changes

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        # Apply the next direction
        self.direction = self.next_direction
        
        # Play subtle movement sound occasionally (every 5 moves)
        if not hasattr(self, 'move_counter'):
            self.move_counter = 0
        self.move_counter += 1
        if self.move_counter % 5 == 0 and self.sound_enabled and sound_available and move_sound:
            move_sound.play()

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
<<<<<<< Updated upstream
            self.high_scoresmanager.update_score(self.difficulty, self.score)
            if self.sound_enabled and sound_available and game_over_sound:
                game_over_sound.play()
=======
>>>>>>> Stashed changes
            return

        # Check self collision
        if any(segment["x"] == new_head["x"] and segment["y"] == new_head["y"]
               for segment in self.snake):
            self.game_over = True
<<<<<<< Updated upstream
            self.high_scoresmanager.update_score(self.difficulty, self.score)
            if self.sound_enabled and sound_available and game_over_sound:
                game_over_sound.play()
=======
>>>>>>> Stashed changes
            return

        # Add new head to snake
        self.snake.insert(0, new_head)

        # Check if food is eaten
        if self.food and new_head["x"] == self.food["x"] and new_head["y"] == self.food["y"]:
            self.score += 10
            if self.sound_enabled and sound_available and eat_sound:
                eat_sound.play()
            self.spawn_food()
        else:
            # Remove tail if not eating food
            self.snake.pop()

    def draw_menu(self):
        """Draw the main menu."""
        screen.fill(BLACK)

        # Draw title
        title = font_title.render("🐍 Snake Game", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 4))

<<<<<<< Updated upstream
        # Draw current selection info
        current_diff = list(DIFFICULTIES.keys())[self.menu_selected_difficulty_index]
        selection_text = font_score.render(f"Difficulty: {current_diff}", True, (100, 200, 150))
        screen.blit(selection_text, (SCREEN_WIDTH // 2 - selection_text.get_width() // 2, SCREEN_HEIGHT // 6 + 60))

        # Draw main menu options
        button_height = 50
        start_y = SCREEN_HEIGHT // 3
        menu_options = ["Start Game", "Settings", "Quit"]

        for i, option in enumerate(menu_options):
            x = SCREEN_WIDTH // 2 - 150
            y = start_y + i * (button_height + 15)

            # Button background
            if i == self.menu_selected_main_index:
                pygame.draw.rect(screen, (100, 200, 150), (x, y, 300, button_height))
            else:
                pygame.draw.rect(screen, BLUE, (x, y, 300, button_height))

            # Button text
            option_text = font_score.render(option, True, WHITE)
            screen.blit(option_text, (x + 10, y + 5))

        # Instructions
        inst_text = font_small.render("Arrow Keys: Select • Enter: Choose • Q/ESC: Quit", True, GRAY)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, SCREEN_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(30)

    def draw_settings(self):
        """Draw the settings menu."""
        screen.fill(BLACK)

        # Draw title
        title = font_title.render("Settings", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 8))

        # Get current values for display
        current_diff = self.difficulty
        current_bg = [k for k, v in BACKGROUNDS.items() if v == self.background_color][0]
        
        snake_color_name = "Green"
        color_palette = COLORBLIND_COLORS if self.colorblind_mode else SNAKE_COLORS
        for name, color in color_palette.items():
            if color == self.snake_color:
                snake_color_name = name
                break

        # Draw settings options
        button_height = 45
        start_y = SCREEN_HEIGHT // 8 + 80
        settings_options = [
            f"Difficulty: {current_diff}",
            f"Background: {current_bg}",
            f"Snake Color: {snake_color_name}",
            f"Sound: {'On' if self.sound_enabled else 'Off'}",
            f"Grid: {'On' if self.show_grid else 'Off'}",
            f"Colorblind Mode: {'On' if self.colorblind_mode else 'Off'}",
        ]

        for i, option in enumerate(settings_options):
            x = SCREEN_WIDTH // 2 - 200
            y = start_y + i * (button_height + 10)

            # Button background
            if i == self.menu_selected_setting_index:
                pygame.draw.rect(screen, (100, 200, 150), (x, y, 400, button_height))
            else:
                pygame.draw.rect(screen, BLUE, (x, y, 400, button_height))

            # Button text
            option_text = font_score.render(option, True, WHITE)
            screen.blit(option_text, (x + 10, y + 5))

        # Instructions
        inst_text = font_small.render("Arrow Keys: Select • Enter: Toggle • ESC: Back", True, GRAY)
=======
        # Draw difficulty selection
        diff_text = font_score.render("Select Difficulty:", True, WHITE)
        screen.blit(diff_text, (SCREEN_WIDTH // 2 - diff_text.get_width() // 2, SCREEN_HEIGHT // 4 + 30))

        # Draw difficulty buttons
        button_height = 50
        start_y = SCREEN_HEIGHT // 4 + 90

        for i, (difficulty, settings) in enumerate(DIFFICULTIES.items()):
            x = SCREEN_WIDTH // 2 - 160
            y = start_y + i * (button_height + 15)

            # Button background
            pygame.draw.rect(screen, BLUE, (x, y, 320, button_height))

            # Button text
            diff_text = font_score.render(difficulty + "  (FPS: {})".format(settings["fps"]), True, WHITE)
            screen.blit(diff_text, (x + 10, y + 5))

        # Instructions
        inst_text = font_small.render("Arrow Keys or WASD to move • R to restart", True, GRAY)
>>>>>>> Stashed changes
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, SCREEN_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(30)

    def draw(self):
        """Render the game."""
        # Clear screen with black background
        screen.fill(BLACK)

        # Draw grid (optional, subtle)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

        # Draw food
        if self.food:
            fx = self.food["x"] * GRID_SIZE + GRID_SIZE // 2
            fy = self.food["y"] * GRID_SIZE + GRID_SIZE // 2
            pygame.draw.circle(screen, RED, (fx, fy), GRID_SIZE // 2 - 1)

        # Draw snake
        for i, segment in enumerate(self.snake):
            x = segment["x"] * GRID_SIZE + GRID_SIZE // 2
            y = segment["y"] * GRID_SIZE + GRID_SIZE // 2

            if i == 0:
                # Head is green, body is darker green
                color = GREEN if i == 0 else DARK_GREEN
            else:
                color = DARK_GREEN

            pygame.draw.rect(screen, color, (x - GRID_SIZE // 2 + 1,
                                            y - GRID_SIZE // 2 + 1,
                                            GRID_SIZE - 2,
                                            GRID_SIZE - 2))

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

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            game_over_text = font_title.render("Game Over!", True, RED)
            score_text = font_score.render(f"Final Score: {self.score}", True, WHITE)
            restart_text = font_score.render("Press R to Restart", True, WHITE)

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

        while True:
            if self.state == "menu":
                # Show menu and wait for player to start
                self.draw_menu()

            elif self.state == "playing":
                self.handle_input()
                self.update()
                self.draw()

                # Check for game over
                if self.game_over:
                    self.state = "game_over"

            elif self.state == "game_over":
                # Show game over screen and wait for restart
                self.draw()

<<<<<<< Updated upstream
            elif self.state == "settings":
                # Show settings menu
                if not self.handle_input():
                    break
                self.draw_settings()

            elif self.state == "paused":
                # Show pause screen
                if not self.handle_input():
                    break
                self.draw_paused()
=======
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.reset()
                        self.state = "playing"
>>>>>>> Stashed changes

        pygame.quit()


# --- Run the Game ---
if __name__ == "__main__":
    game = SnakeGame()
    game.running = True

    # Initialize high score manager
    game.high_scoresmanager = HighScoreManager(HIGH_SCORE_FILE)

    # Start the game
    game.run()
