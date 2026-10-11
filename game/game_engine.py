
import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy

COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 70
FPS = 60


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 16)
        self.big_font = pygame.font.SysFont("monospace", 38, bold=True)
        self.reset()

    
    def reset(self):
        self.walls = generate_maze(COLS, ROWS)
        self.player = Player(0, 0)

        # Three enemies at different corners
        self.enemies = [
            Enemy(ROWS - 1, COLS - 1),
            Enemy(0, COLS - 1),
            Enemy(ROWS - 1, 0),
        ]

        self.exit_rect = pygame.Rect(
            (COLS // 2) * CELL + 5,
            (ROWS // 2) * CELL + 5,
            CELL - 10,
            CELL - 10,
        )

        # Power pellet, positioned away from the exit
        pellet_row = ROWS // 2
        pellet_col = COLS // 2 - 2
        self.pellet_rect = pygame.Rect(
            pellet_col * CELL + CELL // 2 - 7,
            pellet_row * CELL + CELL // 2 - 7,
            14,
            14,
        )
        self.pellet_active = True
        self.freeze_until = 0

        # Initialize all game state whenever the game resets
        self.start_time = pygame.time.get_ticks()
        self.score = 0
        self.caught = False
        self.won = False


    

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
        return True

    def update(self):
        if self.caught or self.won:
            return

        now = pygame.time.get_ticks()
        elapsed = now - self.start_time

        # Difficulty increases every 15 seconds.
        speed_tier = elapsed // 15000
        for enemy in self.enemies:
            enemy.move_interval = max(5, 20 - 2 * speed_tier)

        # Freeze all enemies for five seconds after collecting the pellet.
        if now < self.freeze_until:
            for enemy in self.enemies:
                enemy.frozen = True
        else:
            for enemy in self.enemies:
                enemy.frozen = False

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, ROWS, COLS)

        if (
            self.pellet_active
            and self.player.rect.colliderect(self.pellet_rect)
        ):
            self.pellet_active = False
            self.freeze_until = now + 5000
            for enemy in self.enemies:
                enemy.frozen = True

        for enemy in self.enemies:
            enemy.update(self.walls, self.player, ROWS, COLS)

            if self.player.rect.colliderect(enemy.rect):
                self.caught = True

        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

        # Score one point per frame while alive.
        if not self.caught and not self.won:
            self.score += 1

    def draw(self):
        self.screen.fill((230, 220, 210))
        wall_color = (50, 40, 60)

        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL, r * CELL
                w = self.walls[r][c]

                if w[0]:
                    pygame.draw.line(
                        self.screen, wall_color, (x, y), (x + CELL, y), 3
                    )
                if w[1]:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (x, y + CELL), (x + CELL, y + CELL), 3
                    )
                if w[2]:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (x + CELL, y), (x + CELL, y + CELL), 3
                    )
                if w[3]:
                    pygame.draw.line(
                        self.screen, wall_color,
                        (x, y), (x, y + CELL), 3
                    )

        pygame.draw.rect(
            self.screen, (80, 200, 80), self.exit_rect, border_radius=4
        )
        label = self.font.render("EXIT", True, (20, 80, 20))
        self.screen.blit(
            label, (self.exit_rect.x + 2, self.exit_rect.y + 6)
        )

        if self.pellet_active:
            pygame.draw.circle(
                self.screen, (255, 220, 0), self.pellet_rect.center, 7
            )

        self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        hud_y = ROWS * CELL
        pygame.draw.rect(
            self.screen, (30, 30, 50), (0, hud_y, WIDTH, 70)
        )

        elapsed = pygame.time.get_ticks() - self.start_time
        speed_tier = elapsed // 15000 + 1

        info = self.font.render(
            f"Survived: {self.score // FPS}s  Speed tier: {speed_tier}",
            True, (240, 240, 240),
        )
        self.screen.blit(info, (8, hud_y + 8))

        if pygame.time.get_ticks() < self.freeze_until:
            frozen_text = self.font.render(
                "ENEMIES FROZEN!", True, (255, 220, 0)
            )
            self.screen.blit(frozen_text, (8, hud_y + 34))

        controls = self.font.render(
            "WASD/Arrows: Move   R: Restart",
            True, (200, 200, 200),
        )
        self.screen.blit(controls, (8, hud_y + 51))

        if self.caught:
            self._overlay("CAUGHT!", (220, 60, 60))
        elif self.won:
            self._overlay("ESCAPED!", (80, 220, 80))

        pygame.display.flip()

    def _overlay(self, text, color):
        surface = pygame.Surface(
            (WIDTH, ROWS * CELL), pygame.SRCALPHA
        )
        surface.fill((0, 0, 0, 160))
        self.screen.blit(surface, (0, 0))

        msg = self.big_font.render(text, True, color)
        score_msg = self.font.render(
            f"Final score: {self.score // FPS}s",
            True, (255, 255, 255),
        )
        sub = self.font.render(
            "Press R to Restart", True, (220, 220, 220)
        )

        center_x = WIDTH // 2
        center_y = ROWS * CELL // 2

        self.screen.blit(
            msg, (center_x - msg.get_width() // 2, center_y - 48)
        )
        self.screen.blit(
            score_msg,
            (center_x - score_msg.get_width() // 2, center_y + 2),
        )
        self.screen.blit(
            sub, (center_x - sub.get_width() // 2, center_y + 28)
        )

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
