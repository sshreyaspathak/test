# ui.py
import pygame
from settings import FONT_NAME, WHITE, BLACK, YELLOW, ORANGE, PURPLE
from settings import TILE_SIZE

pygame.font.init()
FONT = pygame.font.Font(FONT_NAME, 18)
BIG = pygame.font.Font(FONT_NAME, 28)

def draw_text(screen, text, pos, color=WHITE, center=False, font=None):
    f = font or FONT
    surf = f.render(text, True, color)
    r = surf.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    screen.blit(surf, r)

def draw_hud(screen, player, level):
    # top-left: score and level
    draw_text(screen, f"Score: {player.score}", (8, 8))
    draw_text(screen, f"Level: {level}", (8, 30))
    # stamina bar
    bar_w = 200
    x = 8
    y = 54
    val = player.stamina / 100.0
    pygame.draw.rect(screen, (80,80,80), (x, y, bar_w, 16))
    pygame.draw.rect(screen, ORANGE, (x, y, int(bar_w*val), 16))
    draw_text(screen, "Stamina", (x + bar_w + 8, y - 2))
