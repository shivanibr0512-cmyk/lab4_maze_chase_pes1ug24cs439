
import pygame
from game.maze import CELL

SPEED = 2


class Player:
    def __init__(self, r, c):
        self.r, self.c = r, c
        cx, cy = c * CELL + CELL // 2, r * CELL + CELL // 2
        self.rect = pygame.Rect(cx - 10, cy - 10, 20, 20)
        self.color = (60, 120, 220)

    def move(self, keys, walls, rows, cols):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = SPEED

        nr = self.rect.move(dx, 0)
        if self._valid(nr, walls, rows, cols):
            self.rect = nr

        nr = self.rect.move(0, dy)
        if self._valid(nr, walls, rows, cols):
            self.rect = nr

    
    
    
    def _valid(self, rect, walls, rows, cols):
        # Keep the player inside the maze boundaries.
        if (
            rect.left < 0
            or rect.top < 0
            or rect.right > cols * CELL
            or rect.bottom > rows * CELL
        ):
            return False

        # Check collisions with the maze walls.
        for r in range(rows):
            for c in range(cols):
                x, y = c * CELL, r * CELL
                wall = walls[r][c]

                wall_rects = []

                if wall[0]:
                    wall_rects.append(pygame.Rect(x, y, CELL, 3))
                if wall[1]:
                    wall_rects.append(
                        pygame.Rect(x, y + CELL - 3, CELL, 3)
                    )
                if wall[2]:
                    wall_rects.append(
                        pygame.Rect(x + CELL - 3, y, 3, CELL)
                    )
                if wall[3]:
                    wall_rects.append(pygame.Rect(x, y, 3, CELL))

                for wall_rect in wall_rects:
                    if rect.colliderect(wall_rect):
                        return False

        return True


    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)


class Enemy:
    def __init__(self, r, c):
        self.r, self.c = r, c
        cx, cy = c * CELL + CELL // 2, r * CELL + CELL // 2
        self.rect = pygame.Rect(cx - 12, cy - 12, 24, 24)
        self.color = (220, 60, 60)
        self.timer = 0
        self.move_interval = 20
        self.frozen = False

    def update(self, walls, player, rows, cols):
        if self.frozen:
            return

        from game.maze import bfs

        self.timer += 1
        if self.timer >= self.move_interval:
            self.timer = 0
            pr = player.rect.centery // CELL
            pc = player.rect.centerx // CELL

            step = bfs(
                walls, (self.r, self.c), (pr, pc), rows, cols
            )

            if step:
                dr, dc = step
                self.r += dr
                self.c += dc

                cx = self.c * CELL + CELL // 2
                cy = self.r * CELL + CELL // 2
                self.rect.center = (cx, cy)

    def draw(self, screen):
        color = (100, 180, 255) if self.frozen else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)

        for ex in [self.rect.x + 4, self.rect.x + 14]:
            pygame.draw.circle(
                screen, (255, 255, 255),
                (ex, self.rect.y + 8), 4
            )
            pygame.draw.circle(
                screen, (0, 0, 0),
                (ex + 1, self.rect.y + 8), 2
            )

        if self.frozen:
            pygame.draw.circle(
                screen, (255, 255, 0), self.rect.center, 16, 2
            )
