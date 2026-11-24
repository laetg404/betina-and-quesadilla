"""
Betina y Quesadilla: una aventura en el jardín
------------------------------------------
Animación hecha con pygame. Dos pugs (una negra y uno canela)
persiguen mariposas en un jardín mientras se cuenta una historia corta.

Controles:    ESPACIO = pausa    R = reiniciar    ESC = salir
"""
import math
import random
import sys

import pygame

pygame.init()
W, H = 1000, 620
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Betina y Quesadilla: una aventura en el jardín")
clock = pygame.time.Clock()
FPS = 60
T_LOOP = 56.0  # duración total de la historia (segundos)


# ----------------------------------------------------------------- utilidades
def font(size, bold=False):
    return pygame.font.SysFont("comicsansms,trebuchetms,arial,dejavusans", size, bold=bold)


F_CAP = font(26)
F_TITLE = font(58, True)
F_SUB = font(28)
F_BUB = font(20, True)


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def R(x, y, w, h):
    return pygame.Rect(int(x), int(y), max(1, int(w)), max(1, int(h)))


def wrap(text, f, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        test = (cur + " " + w).strip()
        if f.size(test)[0] <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


# ------------------------------------------------------------------- fondo
def draw_flower(surf, x, y, s, col):
    pygame.draw.line(surf, (60, 130, 60), (x, y), (x, y + int(24 * s)), max(1, int(3 * s)))
    r = int(4 * s) + 1
    for k in range(6):
        a = k * math.pi / 3
        pygame.draw.circle(surf, col, (int(x + math.cos(a) * r * 1.4), int(y + math.sin(a) * r * 1.4)), r)
    pygame.draw.circle(surf, (250, 200, 40), (int(x), int(y)), max(2, int(r * 0.95)))


def draw_tree(surf, x, base, s):
    pygame.draw.rect(surf, (118, 84, 58), (x - 14 * s, base - 150 * s, 28 * s, 150 * s))
    for dx, dy, r, col in [(-40, -170, 58, (66, 146, 78)), (40, -165, 62, (66, 146, 78)),
                           (0, -215, 68, (84, 168, 92)), (-10, -160, 60, (78, 158, 86))]:
        pygame.draw.circle(surf, col, (int(x + dx * s), int(base + dy * s)), int(r * s))


def build_background():
    bg = pygame.Surface((W, H))
    sky_h = 400
    for y in range(sky_h):
        bg.fill(mix((105, 180, 242), (225, 243, 252), y / sky_h), (0, y, W, 1))

    # sol con resplandor
    glow = pygame.Surface((300, 300), pygame.SRCALPHA)
    for r in range(150, 0, -6):
        pygame.draw.circle(glow, (255, 240, 150, int(70 * (1 - r / 150))), (150, 150), r)
    bg.blit(glow, (900 - 150, 70 - 150))
    pygame.draw.circle(bg, (255, 228, 110), (900, 70), 40)

    # colinas lejanas
    pygame.draw.ellipse(bg, (150, 205, 150), (-250, 300, 800, 220))
    pygame.draw.ellipse(bg, (132, 194, 136), (300, 285, 900, 250))
    pygame.draw.ellipse(bg, (118, 184, 120), (-100, 340, 700, 160))

    # árboles
    draw_tree(bg, 95, 400, 1.0)
    draw_tree(bg, 905, 400, 1.1)

    # césped
    for y in range(392, H):
        bg.fill(mix((120, 198, 94), (64, 140, 64), (y - 392) / (H - 392)), (0, y, W, 1))

    # cerca blanca
    for x in range(-10, W + 30, 36):
        pygame.draw.polygon(bg, (205, 198, 185), [(x - 1, 340), (x + 13, 326), (x + 27, 340), (x + 27, 406), (x - 1, 406)])
        pygame.draw.polygon(bg, (252, 249, 242), [(x + 1, 341), (x + 13, 329), (x + 25, 341), (x + 25, 404), (x + 1, 404)])
    pygame.draw.rect(bg, (238, 233, 222), (0, 356, W, 9))
    pygame.draw.rect(bg, (238, 233, 222), (0, 384, W, 9))
    pygame.draw.rect(bg, (90, 158, 78), (0, 406, W, 7))

    rnd = random.Random(11)
    # briznas de pasto
    for _ in range(1300):
        x, y = rnd.randint(0, W), rnd.randint(414, H)
        s = 0.6 + (y - 400) / 300
        col = mix((50, 130, 55), (150, 215, 105), rnd.random())
        pygame.draw.line(bg, col, (x, y), (x + rnd.randint(-3, 3), y - int(rnd.randint(5, 11) * s)), 2)

    # flores (las más lejanas primero)
    cols = [(255, 255, 255), (255, 150, 190), (255, 215, 70), (190, 140, 240), (255, 130, 100)]
    pts = sorted([(rnd.randint(10, W - 10), rnd.randint(420, H - 40)) for _ in range(60)], key=lambda p: p[1])
    for x, y in pts:
        draw_flower(bg, x, y, 0.55 + (y - 400) / 230, rnd.choice(cols))

    # matas de pasto en primer plano
    for x in range(-10, W + 20, 14):
        h = rnd.randint(14, 34)
        base = H + 2
        pygame.draw.polygon(bg, mix((40, 120, 50), (70, 160, 70), rnd.random()),
                            [(x - 6, base), (x + rnd.randint(-8, 8), base - h), (x + 6, base)])
    return bg


def draw_cloud(surf, x, y, s):
    for dx, dy, r in [(0, 0, 26), (30, -12, 32), (66, 0, 28), (34, 10, 26), (-6, 10, 20), (60, 12, 22)]:
        pygame.draw.circle(surf, (255, 255, 255), (int(x + dx * s), int(y + dy * s)), int(r * s))


# -------------------------------------------------------------- paletas pug
FAWN = dict(body=(224, 182, 128), hi=(242, 208, 160), ol=(112, 78, 46), ear=(64, 47, 40),
            mask=(46, 34, 30), muzzle=(46, 34, 30), wrinkle=(176, 130, 82), nose=(14, 10, 10),
            collar=(60, 120, 215), mask_eye=True)
BLACK = dict(body=(44, 42, 48), hi=(86, 84, 96), ol=(8, 8, 10), ear=(24, 23, 27),
             mask=(44, 42, 48), muzzle=(58, 56, 64), wrinkle=(84, 82, 94), nose=(12, 12, 14),
             collar=(214, 52, 62), mask_eye=False)

SW, SH = 350, 270      # tamaño de la superficie local del pug
CX, GROUND = 175, 235  # centro horizontal y línea del suelo (coordenadas locales)


class Pug:
    def __init__(self, pal, x, y, facing, name):
        self.pal, self.name = pal, name
        self.x, self.y, self.facing = x, y, facing
        self.vx = 0.0
        self.stride = 0.0
        self.lie = 0.0       # 0 = de pie, 1 = echado
        self.tilt = 0.0      # inclinación de la cabeza (grados)
        self.tongue = 0.0
        self.wag = 0.3
        self.panting = 0.0
        self.alert = 0.0
        self.eye = 1.0
        self.jump = 0.0
        self.blink = random.uniform(1, 3)
        self.blinking = 0.0
        self.seed = random.random() * 6
        self.cdir = 1
        self.shadow = pygame.Surface((220, 34), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow, (0, 0, 0, 80), (0, 0, 220, 34))

    # --- geometría ---
    def scale(self):
        return 0.85 + (self.y - 440) * 0.0012

    def head_center(self):
        return 252 + 10 * self.lie, 112 + 62 * self.lie

    def local_to_screen(self, lx, ly):
        s = self.scale()
        return (self.x + (lx - CX) * s * self.facing,
                self.y + (ly - GROUND) * s - self.jump * s)

    def anchor(self, kind):
        hx, hy = self.head_center()
        if kind == "nose":
            return self.local_to_screen(hx + 52, hy - 8)
        return self.local_to_screen(hx + 12, hy - 46)

    # --- dibujo ---
    def render(self, t):
        pal, L = self.pal, self.lie
        ol, body = pal["ol"], pal["body"]
        surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
        run = min(1.0, abs(self.vx) / 110)
        ph = self.stride
        panting = self.panting > 0.5
        breath = math.sin(t * (15 if panting else 2.6) + self.seed)
        body_cy = 176 + 14 * L + breath * (2.4 if panting else 0.8)
        ry = 47 - 5 * L
        hx, hy = self.head_center()
        hy += 3 * math.sin(ph * 2) * run

        def leg(x, offs, far):
            col = shade(body, 0.80) if far else body
            sw = 15 * run * math.sin(ph + offs)
            lift = 13 * run * max(0.0, math.cos(ph + offs))
            hip = (x + 4, body_cy + 18)
            fx, fy = x + sw, 224 - lift * (1 - L)
            pygame.draw.line(surf, ol, hip, (fx, fy), 28)
            pygame.draw.line(surf, col, hip, (fx, fy), 24)
            paw = R(fx - 12, fy - 4, 34, 17)
            pygame.draw.ellipse(surf, ol, paw.inflate(4, 4))
            pygame.draw.ellipse(surf, col, paw)
            for k in (8, 17):
                pygame.draw.line(surf, ol, (paw.x + k, paw.y + 8), (paw.x + k, paw.bottom - 2), 1)

        lying_front = L > 0.4
        # patas lejanas
        if not lying_front:
            leg(214, math.pi, True)
        leg(120, 0, True)

        # cuerpo + pecho
        brect = R(158 - 88, body_cy - ry, 176, 2 * ry)
        pygame.draw.ellipse(surf, ol, brect.inflate(6, 6))
        crect = R(214 - 43, body_cy - ry - 2, 86, 2 * ry + 8)
        pygame.draw.ellipse(surf, ol, crect.inflate(6, 6))
        pygame.draw.ellipse(surf, body, brect)
        pygame.draw.ellipse(surf, body, crect)
        pygame.draw.ellipse(surf, pal["hi"], R(118, body_cy - ry + 8, 70, 11))   # brillo del lomo

        # anca cuando está echado
        if L > 0.4:
            hr = R(78, body_cy - 22, 70, 56)
            pygame.draw.ellipse(surf, ol, hr.inflate(5, 5))
            pygame.draw.ellipse(surf, body, hr)

        # cola enroscada sobre el lomo
        w = self.wag
        tcx = 96 + math.sin(t * 13 + self.seed) * 3.5 * w
        tcy = body_cy - 33 + math.cos(t * 13) * 1.5 * w
        pygame.draw.circle(surf, ol, (int(tcx), int(tcy)), 19, 10)
        pygame.draw.circle(surf, body, (int(tcx), int(tcy)), 18, 7)
        pygame.draw.circle(surf, ol, (int(tcx + 3), int(tcy + 2)), 6, 2)

        # patas cercanas
        leg(100, math.pi, False)
        if not lying_front:
            leg(232, 0, False)
        else:
            for (a, b, c) in ((205, 250, True), (222, 268, False)):
                col = shade(body, 0.8) if c else body
                pygame.draw.line(surf, ol, (a, body_cy + 20), (b, 225), 26)
                pygame.draw.line(surf, col, (a, body_cy + 20), (b, 225), 22)
                paw = R(b - 6, 215, 38, 20)
                pygame.draw.ellipse(surf, ol, paw.inflate(4, 4))
                pygame.draw.ellipse(surf, col, paw)
                for k in (14, 24):
                    pygame.draw.line(surf, ol, (paw.x + k, paw.y + 9), (paw.x + k, paw.bottom - 2), 1)

        # cuello + collar
        nrect = R(hx - 22 - 38, (hy + body_cy) / 2 + 6 - (body_cy - hy + 50) / 2, 76, body_cy - hy + 50)
        pygame.draw.ellipse(surf, ol, nrect.inflate(5, 5))
        pygame.draw.ellipse(surf, body, nrect)
        pygame.draw.line(surf, shade(pal["collar"], 0.55), (hx - 46, hy + 28), (hx + 2, hy + 48), 11)
        pygame.draw.line(surf, pal["collar"], (hx - 46, hy + 28), (hx + 2, hy + 48), 8)
        pygame.draw.circle(surf, (215, 170, 40), (int(hx - 4), int(hy + 55)), 6)
        pygame.draw.circle(surf, (250, 215, 90), (int(hx - 5), int(hy + 54)), 3)

        # ---------------- cabeza (superficie aparte para poder inclinarla)
        hs = pygame.Surface((170, 150), pygame.SRCALPHA)
        cx, cy = 85, 75
        ear = pal["ear"]
        # oreja lejana
        pygame.draw.polygon(hs, ol, [(cx - 2, cy - 38), (cx + 24, cy - 56), (cx + 40, cy - 34), (cx + 20, cy - 24)])
        pygame.draw.polygon(hs, shade(ear, 0.9), [(cx + 1, cy - 38), (cx + 23, cy - 52), (cx + 35, cy - 34), (cx + 19, cy - 27)])
        # cráneo redondo
        hr = R(cx - 47, cy - 44, 94, 88)
        pygame.draw.ellipse(hs, ol, hr.inflate(5, 5))
        pygame.draw.ellipse(hs, body, hr)
        pygame.draw.ellipse(hs, pal["hi"], R(cx - 20, cy - 38, 36, 10))
        # antifaz alrededor del ojo (solo Quesadilla)
        if pal["mask_eye"]:
            pygame.draw.ellipse(hs, pal["mask"], R(cx + 3, cy - 24, 40, 34))
        # hocico chato
        mz = R(cx + 8, cy - 7, 48, 38)
        pygame.draw.ellipse(hs, ol, mz.inflate(4, 4))
        pygame.draw.ellipse(hs, pal["muzzle"], mz)
        # arrugas de la frente
        for r in (22, 29, 36):
            pygame.draw.arc(hs, pal["wrinkle"], R(cx + 20 - r, cy - 2 - r, 2 * r, 2 * r),
                            math.radians(58), math.radians(122), 3)
        # pliegue sobre la nariz
        pygame.draw.arc(hs, pal["wrinkle"], R(cx + 14, cy - 12, 46, 26), 0.25, 2.9, 3)
        # ojo grande y redondo
        ex, ey = cx + 24, cy - 6
        e = max(0.08, self.eye)
        er = R(ex - 13, ey - 13 * e, 26, 26 * e)
        pygame.draw.ellipse(hs, (236, 231, 224), er)
        if e > 0.25:
            pygame.draw.ellipse(hs, (74, 44, 28), R(ex - 10, ey - 10 * e, 20, 20 * e))
            pygame.draw.ellipse(hs, (8, 6, 6), R(ex - 7, ey - 7 * e, 14, 14 * e))
            pygame.draw.circle(hs, (255, 255, 255), (int(ex + 3), int(ey - 4 * e)), 3)
            pygame.draw.circle(hs, (255, 255, 255), (int(ex - 3), int(ey + 3 * e)), 1)
        pygame.draw.ellipse(hs, ol, er.inflate(2, 2), 2)
        # nariz
        nz = R(cx + 43, cy - 6, 19, 15)
        pygame.draw.ellipse(hs, pal["nose"], nz)
        pygame.draw.ellipse(hs, (110, 110, 120), R(cx + 47, cy - 4, 7, 3))
        # boca
        pygame.draw.lines(hs, ol, False, [(cx + 52, cy + 9), (cx + 46, cy + 21), (cx + 24, cy + 20)], 2)
        # lengua
        if self.tongue > 0.06:
            tg = self.tongue
            pygame.draw.ellipse(hs, (120, 34, 46), R(cx + 28, cy + 17, 22, 6 + 8 * tg))
            tr = R(cx + 32, cy + 20, 14, 8 + 20 * tg)
            pygame.draw.ellipse(hs, (238, 116, 138), tr)
            pygame.draw.line(hs, (200, 80, 104), (tr.centerx, tr.y + 3), (tr.centerx, tr.bottom - 5), 1)
        # oreja cercana (doblada, "rosa")
        flap = 6 * math.sin(t * 17) * run - 7 * self.alert
        pygame.draw.polygon(hs, ol, [(cx - 42, cy - 12), (cx - 24, cy - 52 + flap), (cx + 8, cy - 44 + flap * 0.6), (cx - 1, cy - 10)])
        pygame.draw.polygon(hs, ear, [(cx - 39, cy - 13), (cx - 23, cy - 48 + flap), (cx + 5, cy - 41 + flap * 0.6), (cx - 3, cy - 12)])
        pygame.draw.polygon(hs, shade(ear, 1.6), [(cx - 30, cy - 20), (cx - 22, cy - 42 + flap), (cx - 4, cy - 37 + flap * 0.6), (cx - 9, cy - 20)])

        rot = pygame.transform.rotate(hs, self.tilt)
        surf.blit(rot, rot.get_rect(center=(int(hx), int(hy))))
        if self.facing < 0:
            surf = pygame.transform.flip(surf, True, False)
        return surf

    def draw(self, screen, t):
        s = self.scale()
        # sombra
        sh_w = max(40, int(220 * s * (1 - self.jump / 90)))
        shadow = pygame.transform.smoothscale(self.shadow, (sh_w, int(sh_w * 0.15)))
        screen.blit(shadow, (self.x - sh_w // 2, self.y - 6))
        img = self.render(t)
        img = pygame.transform.smoothscale(img, (int(SW * s), int(SH * s)))
        screen.blit(img, (self.x - CX * s, self.y - GROUND * s - self.jump * s))

    def bubble_anchor(self):
        hx, hy = self.head_center()
        return self.local_to_screen(hx, hy - 62)


# ---------------------------------------------------------------- mariposas
class Butterfly:
    COLS = [((255, 186, 36), (255, 238, 130)), ((84, 146, 255), (176, 208, 255)),
            ((240, 98, 168), (255, 176, 212)), ((150, 108, 232), (206, 182, 252))]

    def __init__(self, i):
        self.i = i
        self.reset()

    def reset(self):
        self.x, self.y = W + 80, 230 + self.i * 30
        self.appear = 8 + 1.6 * self.i
        self.flap = random.random() * 6
        self.landed = False
        self.visible = False

    def draw(self, surf):
        if not self.visible:
            return
        c1, c2 = self.COLS[self.i]
        w = 0.2 + 0.8 * abs(math.cos(self.flap))
        sc = 1.25
        x = int(self.x)
        y = int(self.y + (0 if self.landed else 3 * math.sin(self.flap)))
        for side in (-1, 1):
            up = R(0, 0, 26 * w * sc, 24 * sc)
            up.center = (x + side * int(11 * w * sc), y - int(8 * sc))
            lo = R(0, 0, 19 * w * sc, 18 * sc)
            lo.center = (x + side * int(8 * w * sc), y + int(8 * sc))
            for r in (lo, up):
                pygame.draw.ellipse(surf, c1, r)
                pygame.draw.ellipse(surf, (60, 40, 40), r, 2)
            pygame.draw.ellipse(surf, c2, up.inflate(-(up.w // 2), -(up.h // 2)))
            pygame.draw.circle(surf, (255, 255, 255), lo.center, max(1, int(3 * w * sc)))
        pygame.draw.ellipse(surf, (55, 38, 32), (x - 2, y - 13, 5, 28))
        pygame.draw.circle(surf, (55, 38, 32), (x, y - 14), 3)
        pygame.draw.line(surf, (55, 38, 32), (x, y - 15), (x - 6, y - 24), 1)
        pygame.draw.line(surf, (55, 38, 32), (x, y - 15), (x + 6, y - 24), 1)


def wander(i, t, mode):
    if mode == "enter":
        cx, ax, cy, ay, f = 760, 110, 300, 45, 0.33
    elif mode == "chase":
        cx, ax, cy, ay, f = W / 2, W / 2 - 160, 330, 65, 0.5
    else:  # "tease": se alejan hacia arriba, burlonas
        cx, ax, cy, ay, f = W / 2, 260, 245, 40, 0.4
    x = cx + ax * math.sin(f * t + i * 1.9)
    y = cy + ay * math.sin(0.9 * t + i * 2.3) + 14 * math.sin(2.1 * t + i)
    return x, y


# ---------------------------------------------------------- elementos de UI
def draw_heart(surf, x, y, size, color):
    r = size * 0.28
    pygame.draw.circle(surf, color, (int(x - r), int(y - r * 0.3)), int(r) + 1)
    pygame.draw.circle(surf, color, (int(x + r), int(y - r * 0.3)), int(r) + 1)
    pygame.draw.polygon(surf, color, [(x - 2 * r + 1, y), (x + 2 * r - 1, y), (x, y + size * 0.62)])


def bubble(surf, x, y, text):
    img = F_BUB.render(text, True, (40, 40, 52))
    w, h = img.get_size()
    r = pygame.Rect(0, 0, w + 22, h + 10)
    r.midbottom = (int(x), int(y - 14))
    pygame.draw.rect(surf, (255, 255, 255), r, border_radius=14)
    pygame.draw.rect(surf, (60, 60, 74), r, 2, border_radius=14)
    pygame.draw.polygon(surf, (255, 255, 255), [(x - 7, r.bottom - 1), (x + 7, r.bottom - 1), (x, y)])
    pygame.draw.lines(surf, (60, 60, 74), False, [(x - 7, r.bottom), (x, y), (x + 7, r.bottom)], 2)
    surf.blit(img, img.get_rect(center=r.center))


def phase_of(t):
    if t < 8:
        return 0
    if t < 14:
        return 1
    if t < 32:
        return 2
    if t < 40:
        return 3
    if t < 50:
        return 4
    return 5


CAPTIONS = [
    (0.3, 7.7, "Una mañana soleada, Betina y Quesadilla, dos pugs inseparables, salieron a jugar al jardín."),
    (8.0, 13.8, "De pronto, una mariposa dorada pasó volando frente a sus narices... ¡y detrás de ella, muchas más!"),
    (14.0, 22.8, "¡Las dos corrieron tras ellas, saltando y tropezando con sus patitas cortas!"),
    (23.0, 31.7, "Pero las mariposas siempre volaban un poquito más alto de lo que sus saltos alcanzaban..."),
    (32.0, 39.7, "Uf, uf... Con la lengua de fuera y sin aliento, entendieron que nunca podrían atraparlas."),
    (40.0, 49.7, "Entonces se echaron juntas sobre el pasto, y las mariposas, curiosas, se posaron en sus naricitas."),
    (50.0, 55.2, "Así aprendieron que lo mejor no era atraparlas, sino jugar juntas. Fin."),
]


def bubble_text(i, t, ph):
    if ph == 0 and 1.0 < t < 7.0:
        return ("Betina", "Quesadilla")[i]
    if ph == 1 and t > 9.0:
        return ("¡Mira!", "¡Una mariposa!")[i]
    if ph == 2:
        cyc = t * 0.45 + i * 0.5
        if cyc % 1 < 0.3:
            return ["¡Guau!", "¡Wof wof!", "¡Ya casi!", "¡Es mía!"][(int(cyc) + i) % 4]
    if ph == 3 and (t + i * 0.9) % 2.4 < 1.6:
        return "uf, uf..."
    if ph == 5 and t > 51:
        return "Zzz..."
    return None


# ------------------------------------------------------------------- escena
class Scene:
    def __init__(self):
        self.bg = build_background()
        self.clouds = [[120, 60, 1.0, 6], [500, 120, 1.3, 4], [780, 150, 0.8, 8]]
        self.reset()

    def reset(self):
        self.t = 0.0
        self.pugs = [Pug(BLACK, 300, 500, 1, "Betina"), Pug(FAWN, 650, 520, -1, "Quesadilla")]
        self.bfs = [Butterfly(i) for i in range(4)]
        self.hearts = []
        self.heart_timer = 0.0

    # --- lógica ---
    def update(self, dt):
        self.t += dt
        if self.t >= T_LOOP:
            self.reset()
        t = self.t
        ph = phase_of(t)
        for c in self.clouds:
            c[0] = ((c[0] + c[3] * dt + 200) % (W + 400)) - 200

        for i, p in enumerate(self.pugs):
            tx, ty, vmax = p.x, p.y, 0
            tilt, tongue, wag, pant, alert, eye, lie_t, jump_t = 0, 0, 0.3, 0, 0, 1.0, 0, 0
            if ph == 0:      # olfateando el jardín
                tx = (300, 650)[i] + 50 * math.sin(0.55 * t + i * 2.0)
                ty = (500, 520)[i]
                vmax = 55
                tilt = -12 + 5 * math.sin(2.2 * t + i)
                wag = 0.5
            elif ph == 1:    # ¡ven una mariposa!
                p.facing = 1
                tilt, alert, wag = 22, 1, 0.2
            elif ph == 2:    # ¡a perseguirlas!
                b = self.bfs[i]
                if abs(b.x - p.x) > 70:
                    p.cdir = 1 if b.x > p.x else -1
                tx = b.x - p.cdir * 50
                ty = clamp(b.y + 135, 462, 548)
                vmax = 235
                tilt = 14 + 7 * math.sin(p.stride * 2)
                tongue, wag = 0.75, 1.0
                if abs(b.x - p.x) < 190:
                    jump_t = 30 * max(0.0, math.sin(3.2 * t + i * 1.7)) ** 3
            elif ph == 3:    # cansados, jadeando
                tilt, tongue, wag, pant = -8, 1.0, 0.15, 1
            elif ph == 4:    # se echan juntos
                tx, ty, vmax = (380, 640)[i], 505, 110
                tilt, wag = 3, 0.8
                if abs(p.x - tx) < 10:
                    lie_t = 1
                    p.facing = (1, -1)[i]
            else:            # a dormir
                lie_t, eye, wag = 1, 0.08, 0.2
                p.facing = (1, -1)[i]

            # movimiento
            dx = tx - p.x
            v = clamp(dx * 3.0, -vmax, vmax)
            p.vx += (v - p.vx) * min(1, dt * 6)
            p.x += p.vx * dt
            p.y += (ty - p.y) * min(1, dt * 2.5)
            if abs(p.vx) > 25 and ph != 1:
                p.facing = 1 if p.vx > 0 else -1
            p.stride += abs(p.vx) * dt * 0.075
            p.jump = jump_t

            k = min(1, dt * 5)
            p.tilt += (tilt - p.tilt) * k
            p.tongue += (tongue - p.tongue) * k
            p.wag += (wag - p.wag) * k
            p.panting += (pant - p.panting) * k
            p.alert += (alert - p.alert) * k
            p.lie += (lie_t - p.lie) * min(1, dt * 3)

            # parpadeo
            p.blink -= dt
            if p.blink < 0:
                p.blink, p.blinking = random.uniform(2, 5), 0.13
            if p.blinking > 0:
                p.blinking -= dt
            if ph == 4 and p.lie > 0.9:
                eye = 0.55
            target = 0.08 if p.blinking > 0 else eye
            p.eye += (target - p.eye) * min(1, dt * 18)

        # mariposas
        settled = ph >= 4 and all(p.lie > 0.93 for p in self.pugs)
        for b in self.bfs:
            if not b.visible:
                if t >= b.appear:
                    b.visible = True
                continue
            k = 2.0
            if ph <= 1:
                tx, ty = wander(b.i, t, "enter")
            elif ph == 2:
                tx, ty = wander(b.i, t, "chase")
                k = 4.0
            elif ph == 3:
                tx, ty = wander(b.i, t, "tease")
            elif ph == 4:
                p = self.pugs[b.i % 2]
                if settled:
                    tx, ty = p.anchor("nose" if b.i < 2 else "head")
                    k = 3.0
                else:
                    tx, ty = p.x + 60 * math.sin(t + b.i), 300 + 25 * math.sin(1.3 * t + b.i)
            else:
                tx, ty = b.x + (b.i - 1.5) * 120, -140
                k = 0.9
            b.x += (tx - b.x) * min(1, dt * k)
            b.y += (ty - b.y) * min(1, dt * k)
            b.landed = ph == 4 and settled and math.hypot(tx - b.x, ty - b.y) < 6
            b.flap += dt * (3.2 if b.landed else 17)

        # corazones
        if settled and t > 43.5:
            self.heart_timer -= dt
            if self.heart_timer <= 0:
                self.heart_timer = 0.55
                mx = (self.pugs[0].x + self.pugs[1].x) / 2 + random.uniform(-40, 40)
                self.hearts.append([mx, 470.0, 0.0])
        for h in self.hearts:
            h[1] -= 42 * dt
            h[0] += math.sin(h[2] * 3) * 12 * dt
            h[2] += dt
        self.hearts = [h for h in self.hearts if h[2] < 3.2]

    # --- dibujo ---
    def draw(self, screen):
        t = self.t
        ph = phase_of(t)
        screen.blit(self.bg, (0, 0))
        for x, y, s, _ in self.clouds:
            draw_cloud(screen, x, y, s)

        for p in sorted(self.pugs, key=lambda q: q.y):
            p.draw(screen, t)
        for b in self.bfs:
            b.draw(screen)
        for x, y, age in self.hearts:
            size = 14 + 14 * min(1, age / 0.6)
            draw_heart(screen, x, y, size, (240, 70, 110))

        for i, p in enumerate(self.pugs):
            txt = bubble_text(i, t, ph)
            if txt:
                bx, by = p.bubble_anchor()
                bubble(screen, bx, by, txt)

        # subtítulo de la historia
        for s, e, text in CAPTIONS:
            if s <= t <= e:
                a = int(255 * clamp(min((t - s) / 0.6, (e - t) / 0.6), 0, 1))
                lines = wrap(text, F_CAP, W - 120)
                lh = F_CAP.get_linesize()
                ph_ = lh * len(lines) + 24
                panel = pygame.Surface((W - 80, ph_), pygame.SRCALPHA)
                pygame.draw.rect(panel, (22, 28, 52, 185), panel.get_rect(), border_radius=18)
                for k, line in enumerate(lines):
                    img = F_CAP.render(line, True, (255, 250, 236))
                    panel.blit(img, img.get_rect(midtop=(panel.get_width() // 2, 12 + k * lh)))
                panel.set_alpha(a)
                screen.blit(panel, (40, 16))

        # título inicial
        if t < 5:
            a = int(255 * clamp(min(t / 0.8, (5 - t) / 0.8), 0, 1))
            for txt, f, y in (("Betina y Quesadilla", F_TITLE, 205), ("Una aventura en el jardín", F_SUB, 255)):
                for off, col in (((3, 3), (40, 50, 80)), ((0, 0), (255, 255, 255))):
                    img = f.render(txt, True, col)
                    img.set_alpha(a)
                    screen.blit(img, img.get_rect(center=(W // 2 + off[0], y + off[1])))

        # fundido a negro al inicio y al final
        fade = 0
        if t < 1:
            fade = 255 * (1 - t)
        elif t > T_LOOP - 1.5:
            fade = 255 * (t - (T_LOOP - 1.5)) / 1.5
        if fade > 0:
            ov = pygame.Surface((W, H))
            ov.set_alpha(int(clamp(fade, 0, 255)))
            screen.blit(ov, (0, 0))


# --------------------------------------------------------------------- main
def main():
    scene = Scene()
    paused = False
    while True:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    paused = not paused
                elif e.key == pygame.K_r:
                    scene.reset()
        if not paused:
            scene.update(dt)
        scene.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()