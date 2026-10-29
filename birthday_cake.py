"""
Galaxy Birthday Cake - Particle Animation
复刻视频效果：玻璃罩星空蛋糕 + 粒子星星 + 摇曳烛光

运行方式:
    pip install pygame
    python birthday_cake.py

操作:
    - 点击鼠标: 在点击处炸开一波彩带粒子
    - 移动鼠标: 留下小星星拖尾
    - 空格 SPACE: 吹灭 / 重新点燃蜡烛
    - B 键: 在蛋糕上方炸开庆祝粒子
    - ESC / 关闭窗口: 退出
"""

import math
import random
import sys

import pygame

# ---------------- Config ----------------
WIDTH, HEIGHT = 960, 720
FPS = 60
TITLE = "Happy Birthday!"

BG = (10, 10, 18)
WHITE = (255, 255, 255)

STAR_COLORS = [
    (255, 209, 102),  # gold
    (255, 107, 129),  # pink
    (120, 200, 255),  # sky
    (168, 130, 255),  # purple
    (120, 255, 180),  # mint
    (255, 165, 80),   # orange
    (255, 255, 255),  # white
]

CONFETTI_COLORS = STAR_COLORS + [(255, 80, 180), (80, 220, 255)]


# ---------------- Helpers ----------------
def draw_star(surface, color, cx, cy, size, alpha=255):
    """Draw a 4-point sparkle star like in the video."""
    if size < 1:
        return
    s = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
    c = size + 2
    points = [
        (c, c - size),
        (c + size * 0.22, c - size * 0.22),
        (c + size, c),
        (c + size * 0.22, c + size * 0.22),
        (c, c + size),
        (c - size * 0.22, c + size * 0.22),
        (c - size, c),
        (c - size * 0.22, c - size * 0.22),
    ]
    pygame.draw.polygon(s, (*color, alpha), points)
    surface.blit(s, (cx - c, cy - c))


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# ---------------- Particles ----------------
class FloatingStar:
    """Background floating stars / sparkles that drift around the dome."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset(init=True)

    def reset(self, init=False):
        self.x = random.uniform(60, self.w - 60)
        self.y = random.uniform(40, self.h - 40) if init else random.uniform(self.h * 0.6, self.h)
        self.size = random.uniform(3, 11)
        self.color = random.choice(STAR_COLORS)
        self.vx = random.uniform(-0.25, 0.25)
        self.vy = random.uniform(-0.45, -0.08)
        self.phase = random.uniform(0, math.tau)
        self.twinkle_speed = random.uniform(0.02, 0.06)
        self.is_star = random.random() < 0.55  # star shape vs dot

    def update(self):
        self.phase += self.twinkle_speed
        self.x += self.vx + math.sin(self.phase) * 0.18
        self.y += self.vy
        if self.y < -20 or self.x < -20 or self.x > self.w + 20:
            self.reset()

    def draw(self, surf):
        alpha = int(140 + 115 * (0.5 + 0.5 * math.sin(self.phase)))
        size = self.size * (0.75 + 0.35 * math.sin(self.phase))
        if self.is_star:
            draw_star(surf, self.color, int(self.x), int(self.y), max(2, int(size)), alpha)
        else:
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (6, 6), max(1, int(size * 0.35)))
            surf.blit(s, (self.x - 6, self.y - 6))


class FlameParticle:
    """Tiny embers rising from the candle flame."""

    def __init__(self, x, y):
        self.x = x + random.uniform(-4, 4)
        self.y = y
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-1.4, -0.6)
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.035)
        self.size = random.uniform(1.5, 3.5)
        self.color = random.choice([(255, 180, 60), (255, 120, 40), (255, 220, 120)])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(255 * self.life)
        s = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (5, 5), max(1, int(self.size * self.life)))
        surf.blit(s, (self.x - 5, self.y - 5))


class BurstParticle:
    """Confetti / sparkle burst on click or celebration."""

    def __init__(self, x, y):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.2, 6.5)
        self.x, self.y = x, y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 1.2
        self.gravity = 0.07
        self.life = 1.0
        self.decay = random.uniform(0.008, 0.02)
        self.color = random.choice(CONFETTI_COLORS)
        self.size = random.uniform(3, 9)
        self.kind = random.choice(["star", "dot", "rect"])
        self.rot = random.uniform(0, math.tau)
        self.vr = random.uniform(-0.15, 0.15)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.99
        self.rot += self.vr
        self.life -= self.decay
        return self.life > 0

    def draw(self, surf):
        if self.life <= 0:
            return
        alpha = int(255 * min(1.0, self.life * 1.4))
        if self.kind == "star":
            draw_star(surf, self.color, int(self.x), int(self.y), max(2, int(self.size * self.life)), alpha)
        elif self.kind == "dot":
            s = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (6, 6), max(1, int(self.size * 0.4)))
            surf.blit(s, (self.x - 6, self.y - 6))
        else:
            s = pygame.Surface((10, 6), pygame.SRCALPHA)
            pygame.draw.rect(s, (*self.color, alpha), (0, 0, 8, 4))
            s = pygame.transform.rotate(s, math.degrees(self.rot))
            surf.blit(s, (self.x - s.get_width() // 2, self.y - s.get_height() // 2))


class TrailStar:
    def __init__(self, x, y):
        self.x = x + random.uniform(-6, 6)
        self.y = y + random.uniform(-6, 6)
        self.life = 1.0
        self.decay = random.uniform(0.03, 0.06)
        self.size = random.uniform(4, 9)
        self.color = random.choice(STAR_COLORS)

    def update(self):
        self.life -= self.decay
        self.y -= 0.4
        return self.life > 0

    def draw(self, surf):
        draw_star(surf, self.color, int(self.x), int(self.y),
                  max(2, int(self.size * self.life)), int(220 * self.life))


# ---------------- Cake ----------------
class GalaxyCake:
    def __init__(self, cx, base_y):
        self.cx = cx
        self.base_y = base_y
        # Pre-generate galaxy dots so they don't flicker randomly each frame
        random.seed(42)
        self.galaxy_dots = []
        for _ in range(260):
            # within cake layers bounding box
            gx = random.uniform(cx - 150, cx + 150)
            gy = random.uniform(base_y - 170, base_y - 10)
            self.galaxy_dots.append((gx, gy, random.uniform(0.8, 2.2),
                                     random.choice([(255, 255, 255), (180, 200, 255), (255, 190, 230)])))
        self.sprinkles = []
        for layer_y in [base_y - 55, base_y - 105, base_y - 145]:
            for _ in range(22):
                self.sprinkles.append((
                    random.uniform(cx - 135, cx + 135),
                    random.uniform(layer_y - 12, layer_y + 12),
                    random.uniform(0, math.tau),
                    random.choice(CONFETTI_COLORS),
                ))
        random.seed()

    def draw(self, surf):
        cx, by = self.cx, self.base_y

        # Plate
        pygame.draw.ellipse(surf, (38, 32, 58), (cx - 195, by - 12, 390, 36))
        pygame.draw.ellipse(surf, (212, 175, 85), (cx - 190, by - 16, 380, 30))
        pygame.draw.ellipse(surf, (245, 205, 110), (cx - 180, by - 15, 360, 22))

        # Layers: bottom -> top (galaxy gradient by stacking colors)
        layers = [
            # (width, height, bottom_y, top_color, bottom_color)
            (300, 58, by - 8, (62, 32, 92), (28, 18, 52)),
            (260, 52, by - 62, (42, 62, 128), (52, 32, 92)),
            (210, 46, by - 110, (88, 52, 138), (42, 62, 128)),
        ]
        for w, h, bottom, c_top, c_bot in layers:
            x = cx - w // 2
            y = bottom - h
            # vertical gradient
            for i in range(h):
                t = i / max(1, h - 1)
                col = lerp_color(c_top, c_bot, t)
                pygame.draw.rect(surf, col, (x, y + i, w, 1))
            # icing drip top
            pygame.draw.ellipse(surf, (245, 210, 235), (x, y - 8, w, 20))
            pygame.draw.ellipse(surf, (255, 235, 248), (x + 6, y - 7, w - 12, 14))

        # Galaxy dots clipped roughly to cake area
        for gx, gy, r, col in self.galaxy_dots:
            if by - 165 < gy < by - 15 and cx - 148 < gx < cx + 148:
                pygame.draw.circle(surf, col, (int(gx), int(gy)), int(r))

        # Sprinkles
        for sx, sy, ang, col in self.sprinkles:
            x2 = sx + math.cos(ang) * 7
            y2 = sy + math.sin(ang) * 7
            pygame.draw.line(surf, col, (sx, sy), (x2, y2), 3)

        # Cherries / deco balls on top layer
        for dx in [-72, -36, 0, 36, 72]:
            pygame.draw.circle(surf, (255, 80, 130), (cx + dx, by - 162), 9)
            pygame.draw.circle(surf, (255, 180, 200), (cx + dx - 3, by - 165), 3)


# ---------------- Main ----------------
def get_handwritten_font(size):
    # Try pretty script fonts, fall back gracefully
    candidates = ["Segoe Script", "Bradley Hand", "Comic Sans MS", "cursive"]
    for name in candidates:
        try:
            f = pygame.font.SysFont(name, size)
            if f:
                return f
        except Exception:
            continue
    return pygame.font.Font(None, size)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font_big = get_handwritten_font(62)
    font_small = pygame.font.SysFont("Arial", 16)

    cake = GalaxyCake(WIDTH // 2, 545)
    candle_x, candle_top = WIDTH // 2, 545 - 172
    flame_on = True

    floating = [FloatingStar(WIDTH, HEIGHT) for _ in range(95)]
    bursts = []
    flames = []
    trail = []

    # Static background stars
    bg_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
                 random.uniform(0.6, 1.8), random.uniform(0, math.tau)) for _ in range(130)]

    t = 0.0
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    flame_on = not flame_on
                    if flame_on:
                        for _ in range(28):
                            bursts.append(BurstParticle(candle_x, candle_top - 28))
                elif event.key == pygame.K_b:
                    for _ in range(90):
                        bursts.append(BurstParticle(WIDTH // 2 + random.uniform(-90, 90),
                                                    350 + random.uniform(-30, 30)))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for _ in range(45):
                    bursts.append(BurstParticle(mx, my))
            elif event.type == pygame.MOUSEMOTION:
                if random.random() < 0.45:
                    mx, my = event.pos
                    trail.append(TrailStar(mx, my))

        # --- Draw background ---
        screen.fill(BG)
        for x, y, r, ph in bg_stars:
            a = int(90 + 70 * math.sin(t * 1.4 + ph))
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, max(20, a)), (3, 3), int(r))
            screen.blit(s, (x, y))

        # Floating stars behind dome
        for p in floating:
            p.update()
            p.draw(screen)

        # Cake
        cake.draw(screen)

        # --- Candle ---
        # body
        pygame.draw.rect(screen, (255, 245, 250), (candle_x - 7, candle_top, 14, 52), border_radius=4)
        for i in range(5):
            y = candle_top + 6 + i * 10
            pygame.draw.line(screen, (255, 110, 160), (candle_x - 7, y), (candle_x + 7, y + 5), 3)
        pygame.draw.rect(screen, (40, 35, 40), (candle_x - 1, candle_top - 7, 2, 8))  # wick

        # Flame
        flame_cx, flame_cy = candle_x, candle_top - 22
        if flame_on:
            if random.random() < 0.55:
                flames.append(FlameParticle(flame_cx, flame_cy))
            flicker = math.sin(t * 11) * 2.2 + math.sin(t * 23) * 1.1 + random.uniform(-0.8, 0.8)
            fh = 30 + flicker * 1.6
            fw = 15 + math.sin(t * 9) * 1.6

            # glow
            glow = pygame.Surface((130, 130), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 170, 50, 52), (65, 65), 58)
            pygame.draw.circle(glow, (255, 190, 80, 38), (65, 65), 38)
            screen.blit(glow, (flame_cx - 65, flame_cy - 58))

            # outer / inner flame (teardrop via ellipses + triangle)
            pygame.draw.ellipse(screen, (255, 120, 25), (flame_cx - fw / 2, flame_cy - fh / 2, fw, fh))
            pygame.draw.ellipse(screen, (255, 185, 45), (flame_cx - fw * 0.32, flame_cy - fh * 0.28, fw * 0.64, fh * 0.68))
            pygame.draw.ellipse(screen, (255, 245, 190), (flame_cx - fw * 0.16, flame_cy + fh * 0.02, fw * 0.32, fh * 0.36))
            pygame.draw.polygon(screen, (255, 120, 25),
                                [(flame_cx - fw * 0.32, flame_cy - fh * 0.28),
                                 (flame_cx + fw * 0.32, flame_cy - fh * 0.28),
                                 (flame_cx + flicker * 0.7, flame_cy - fh * 0.78)])

        flames = [p for p in flames if p.update()]
        for p in flames:
            p.draw(screen)

        # --- Glass dome ---
        dome = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dome_rect = pygame.Rect(WIDTH // 2 - 225, 118, 450, 442)
        pygame.draw.ellipse(dome, (170, 210, 255, 26), dome_rect)
        pygame.draw.ellipse(dome, (200, 225, 255, 95), dome_rect, width=3)
        # knob
        pygame.draw.circle(dome, (212, 175, 85, 220), (WIDTH // 2, 112), 13)
        pygame.draw.circle(dome, (255, 225, 140, 255), (WIDTH // 2, 112), 8)
        # highlights
        pygame.draw.arc(dome, (255, 255, 255, 150), (WIDTH // 2 - 195, 145, 150, 300), 0.7, 1.9, 5)
        pygame.draw.arc(dome, (255, 255, 255, 70), (WIDTH // 2 + 60, 160, 130, 260), -1.2, -0.3, 4)
        screen.blit(dome, (0, 0))

        # Bursts & trail
        bursts = [p for p in bursts if p.update()]
        for p in bursts:
            p.draw(screen)
        trail = [p for p in trail if p.update()]
        for p in trail:
            p.draw(screen)

        # --- Text ---
        txt = font_big.render("Happy birthday!", True, (255, 235, 245))
        shadow = font_big.render("Happy birthday!", True, (90, 50, 110))
        tx = WIDTH // 2 - txt.get_width() // 2
        screen.blit(shadow, (tx + 2, 594))
        screen.blit(txt, (tx, 592))

        hint = font_small.render("Click = burst   •   Space = blow / light candle   •   B = celebrate", True, (150, 150, 175))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 26))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()