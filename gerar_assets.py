#!/usr/bin/env python3
"""Gera sprites e backgrounds do Projeto Gaia (stdlib apenas).

Tecnica: renderizacao por campos de distancia (SDF) com mistura suave de
formas (smin), iluminacao direcional com quantizacao em rampas de cor
(pixel art de alta resolucao), texturas procedurais de pelagem/escamas/folhas
e anti-aliasing por superamostragem.

Uso:
    python3 gerar_assets.py            # gera tudo
    python3 gerar_assets.py lobo onca  # gera apenas os nomes passados
"""
import struct, zlib, math, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SDIR = os.path.join(BASE, "assets/sprites/organismos")
TDIR = os.path.join(BASE, "assets/tilesets")

# ── PNG ───────────────────────────────────────────────────────────────────────

def save_png(path, w, h, buf):
    def chunk(name, data):
        c = name + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    rs = w * 4
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += buf[y*rs:(y+1)*rs]
    idat = chunk(b'IDAT', zlib.compress(bytes(raw), 6))
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + ihdr + idat + chunk(b'IEND', b''))
    print(f"  OK  {os.path.basename(path)}  {w}x{h}")

def mk(w, h):
    return bytearray(w * h * 4)

def _c(v):
    return max(0, min(255, int(v)))

# ── Ruido ─────────────────────────────────────────────────────────────────────

def hash2(x, y, seed=0):
    h = (x * 374761393 + y * 668265263 + seed * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0

def vnoise(x, y, seed=0):
    xi, yi = math.floor(x), math.floor(y)
    xf, yf = x - xi, y - yi
    u = xf * xf * (3 - 2 * xf)
    v = yf * yf * (3 - 2 * yf)
    a = hash2(xi, yi, seed); b = hash2(xi + 1, yi, seed)
    c = hash2(xi, yi + 1, seed); d = hash2(xi + 1, yi + 1, seed)
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v

def fbm(x, y, seed=0, octaves=3):
    s, amp, f, tot = 0.0, 1.0, 1.0, 0.0
    for i in range(octaves):
        s += vnoise(x * f, y * f, seed + i) * amp
        tot += amp
        amp *= 0.5
        f *= 2.0
    return s / tot

# ── SDF ───────────────────────────────────────────────────────────────────────

def sd_cap(px, py, ax, ay, bx, by, r1, r2):
    """Capsula com raio variavel de r1 (em a) a r2 (em b)."""
    pax, pay = px - ax, py - ay
    bax, bay = bx - ax, by - ay
    h = (pax * bax + pay * bay) / (bax * bax + bay * bay + 1e-9)
    h = 0.0 if h < 0.0 else (1.0 if h > 1.0 else h)
    dx, dy = pax - bax * h, pay - bay * h
    return math.hypot(dx, dy) - (r1 + (r2 - r1) * h)

def sd_ell(px, py, cx, cy, rx, ry):
    dx, dy = (px - cx) / rx, (py - cy) / ry
    k = math.hypot(dx, dy)
    if k < 1e-9:
        return -min(rx, ry)
    return (k - 1.0) * min(rx, ry)

def smin(a, b, k):
    h = 0.5 + 0.5 * (b - a) / k
    h = 0.0 if h < 0.0 else (1.0 if h > 1.0 else h)
    return b + (a - b) * h - k * h * (1.0 - h)

def part_sdf(part, x, y):
    d = 1e9
    k = part['k']
    for s in part['shapes']:
        if s[0] == 'c':
            dd = sd_cap(x, y, s[1], s[2], s[3], s[4], s[5], s[6])
        else:
            dd = sd_ell(x, y, s[1], s[2], s[3], s[4])
        d = smin(d, dd, k) if d < 1e8 else dd
    return d

def part_bbox(part):
    x0 = y0 = 1e9; x1 = y1 = -1e9
    for s in part['shapes']:
        if s[0] == 'c':
            r = max(s[5], s[6])
            xs = (s[1], s[3]); ys = (s[2], s[4])
        else:
            r = max(s[3], s[4])
            xs = (s[1],); ys = (s[2],)
        x0 = min(x0, min(xs) - r); x1 = max(x1, max(xs) + r)
        y0 = min(y0, min(ys) - r); y1 = max(y1, max(ys) + r)
    m = part['k'] + 2.5
    return (x0 - m, y0 - m, x1 + m, y1 + m)

# ── Renderizador ──────────────────────────────────────────────────────────────

def P(shapes, ramp, k=4.0, bevel=6.0, tex=None, grad=None, ramp2=None):
    """Parte solida sombreada. tex(px,py)->(dt,mul); grad(px,py)->0..1 mescla ramp2."""
    return {'shapes': shapes, 'ramp': ramp, 'k': k, 'bevel': bevel,
            'tex': tex, 'grad': grad, 'ramp2': ramp2, 'flat': None}

def FLAT(shapes, color, alpha, k=4.0):
    """Parte plana translucida (sombras no chao)."""
    return {'shapes': shapes, 'k': k, 'flat': (color, alpha)}

def _ramp_pick(ramp, t, px, py):
    n = len(ramp)
    q = t * (n - 1) + (hash2(int(px * 3.1) & 2047, int(py * 3.1) & 2047, 7) - 0.5) * 0.55
    i = int(round(q))
    if i < 0: i = 0
    elif i > n - 1: i = n - 1
    return ramp[i]

LIGHT = (-0.46, -0.64, 0.62)

def render(W, H, parts, decors=(), ss=2):
    lx, ly, lz = LIGHT
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / ln, ly / ln, lz / ln
    for p in parts:
        p['bbox'] = part_bbox(p)
    buf = mk(W, H)
    inv = 1.0 / (ss * ss)
    for y in range(H):
        for x in range(W):
            orr = og = ob = oa = 0.0
            for sy in range(ss):
                for sx in range(ss):
                    px = x + (sx + 0.5) / ss
                    py = y + (sy + 0.5) / ss
                    cr = cg = cb = ca = 0.0
                    for p in parts:
                        bb = p['bbox']
                        if px < bb[0] or px > bb[2] or py < bb[1] or py > bb[3]:
                            continue
                        d = part_sdf(p, px, py)
                        cov = 0.62 - d
                        if cov <= 0.0:
                            continue
                        if cov > 1.0:
                            cov = 1.0
                        if p['flat']:
                            (fr, fg, fb), fa = p['flat']
                            a = cov * fa
                            cr = cr * (1 - a) + fr * a
                            cg = cg * (1 - a) + fg * a
                            cb = cb * (1 - a) + fb * a
                            ca = ca * (1 - a) + a
                            continue
                        e = 0.85
                        gx = (part_sdf(p, px + e, py) - d) / e
                        gy = (part_sdf(p, px, py + e) - d) / e
                        s = -d / p['bevel']
                        s = 0.0 if s < 0.0 else (1.0 if s > 1.0 else s)
                        nz = 0.30 + 0.70 * s
                        gl = math.sqrt(gx * gx + gy * gy) + 1e-9
                        nx, ny = gx / gl * (1 - s), gy / gl * (1 - s)
                        nn = math.sqrt(nx * nx + ny * ny + nz * nz)
                        diff = (nx * lx + ny * ly + nz * lz) / nn
                        if diff < 0.0:
                            diff = 0.0
                        t = 0.14 + 0.82 * diff
                        mul = 1.0
                        if p['tex']:
                            dt, mul = p['tex'](px, py)
                            t += dt
                        if t < 0.0: t = 0.0
                        elif t > 1.0: t = 1.0
                        r_, g_, b_ = _ramp_pick(p['ramp'], t, px, py)
                        if p['grad']:
                            g2 = p['grad'](px, py)
                            if g2 > 0.01:
                                r2, gg2, b2 = _ramp_pick(p['ramp2'], t, px, py)
                                r_ = r_ + (r2 - r_) * g2
                                g_ = g_ + (gg2 - g_) * g2
                                b_ = b_ + (b2 - b_) * g2
                        r_ *= mul; g_ *= mul; b_ *= mul
                        if d > -1.25:                     # contorno escuro
                            o0 = p['ramp'][0]
                            r_, g_, b_ = o0[0] * 0.72, o0[1] * 0.72, o0[2] * 0.72
                        cr = cr * (1 - cov) + r_ * cov
                        cg = cg * (1 - cov) + g_ * cov
                        cb = cb * (1 - cov) + b_ * cov
                        ca = ca * (1 - cov) + cov
                    for dec in decors:
                        if dec[0] == 'circ':
                            _, cx0, cy0, r0, col, al = dec
                            dd = math.hypot(px - cx0, py - cy0) - r0
                        else:  # 'cap'
                            _, ax, ay, bx, by, r0, col, al = dec
                            dd = sd_cap(px, py, ax, ay, bx, by, r0, r0)
                        cov = 0.62 - dd
                        if cov <= 0.0:
                            continue
                        if cov > 1.0:
                            cov = 1.0
                        a = cov * al
                        cr = cr * (1 - a) + col[0] * a
                        cg = cg * (1 - a) + col[1] * a
                        cb = cb * (1 - a) + col[2] * a
                        ca = ca * (1 - a) + a
                    orr += cr; og += cg; ob += cb; oa += ca
            i = (y * W + x) * 4
            buf[i] = _c(orr * inv); buf[i + 1] = _c(og * inv)
            buf[i + 2] = _c(ob * inv); buf[i + 3] = _c(oa * inv * 255)
    return buf

def eye(x, y, r, iris):
    """Decoradores de um olho com iris, pupila e brilho."""
    return [
        ('circ', x, y, r + 0.9, (18, 14, 10), 1.0),
        ('circ', x, y, r, iris, 1.0),
        ('circ', x + r * 0.15, y + r * 0.1, r * 0.55, (12, 10, 8), 1.0),
        ('circ', x - r * 0.38, y - r * 0.40, r * 0.30, (250, 250, 245), 0.95),
    ]

def sombra(cx, cy, rx, ry):
    return FLAT([('e', cx, cy, rx, ry)], (18, 22, 12), 0.32, k=3.0)

def escala(ramp, f):
    return [(_c(r * f), _c(g * f), _c(b * f)) for r, g, b in ramp]

# ── Rampas de cor ─────────────────────────────────────────────────────────────

LOBO_R    = [(30, 32, 40), (58, 61, 72), (86, 90, 104), (118, 123, 138), (152, 158, 172), (198, 202, 212)]
LOBO_BR   = [(96, 94, 96), (140, 136, 132), (176, 172, 164), (205, 200, 190), (228, 224, 214), (245, 243, 236)]
ONCA_R    = [(56, 32, 8), (110, 66, 14), (160, 100, 22), (198, 132, 34), (226, 166, 58), (244, 204, 110)]
ONCA_BR   = [(120, 100, 66), (170, 150, 110), (204, 186, 148), (228, 214, 182), (243, 234, 210), (252, 248, 234)]
GAZELA_R  = [(62, 42, 18), (110, 78, 36), (156, 116, 60), (192, 150, 88), (218, 182, 122), (238, 214, 166)]
GAZELA_BR = [(150, 132, 104), (190, 176, 150), (218, 208, 186), (236, 230, 214), (248, 244, 234), (255, 253, 248)]
COELHO_R  = [(52, 38, 24), (92, 70, 44), (132, 104, 68), (168, 138, 96), (200, 172, 130), (228, 206, 170)]
COELHO_BR = [(140, 126, 108), (184, 172, 152), (214, 204, 186), (234, 226, 212), (248, 242, 232), (255, 252, 246)]
LAGART_R  = [(38, 48, 22), (66, 84, 36), (96, 118, 52), (128, 150, 72), (162, 182, 98), (198, 212, 136)]
SERP_R    = [(52, 38, 20), (94, 70, 38), (136, 104, 58), (172, 138, 82), (204, 172, 114), (230, 204, 152)]
CARV_TR   = [(40, 28, 18), (70, 50, 32), (100, 74, 48), (128, 98, 66), (156, 124, 88), (184, 152, 114)]
CARV_FL   = [(22, 48, 16), (38, 76, 24), (56, 104, 34), (78, 132, 46), (104, 160, 62), (138, 190, 88)]
PALM_TR   = [(52, 38, 24), (88, 66, 42), (122, 94, 62), (152, 122, 84), (180, 150, 110), (206, 180, 140)]
PALM_FL   = [(16, 52, 22), (26, 80, 32), (40, 110, 44), (58, 138, 58), (84, 164, 76), (120, 190, 102)]
CACTO_R   = [(20, 48, 24), (34, 76, 36), (50, 104, 50), (70, 130, 64), (94, 154, 82), (126, 178, 108)]
INVAS_R   = [(38, 10, 44), (66, 18, 74), (98, 26, 104), (130, 36, 130), (164, 52, 152), (198, 84, 176)]
INVAS_FL  = [(70, 6, 30), (112, 10, 44), (154, 16, 58), (192, 28, 70), (222, 52, 88), (240, 96, 120)]

# ── Texturas ──────────────────────────────────────────────────────────────────

def tex_pelo(fx=0.14, fy=0.52, amp=0.16, seed=3):
    def t(px, py):
        return ((vnoise(px * fx, py * fy, seed) - 0.5) * 2 * amp, 1.0)
    return t

def tex_rosetas(seed=11, cell=17.0, amp=0.11):
    """Rosetas de onca: aneis escuros esparsos em celulas jitteradas."""
    def t(px, py):
        dt = (vnoise(px * 0.18, py * 0.5, seed + 5) - 0.5) * 2 * amp
        cx, cy = math.floor(px / cell), math.floor(py / cell)
        best = 1e9
        for oy in (-1, 0, 1):
            for ox in (-1, 0, 1):
                if hash2(cx + ox, cy + oy, seed + 2) < 0.25:
                    continue  # celula sem roseta
                jx = (cx + ox + 0.5 + (hash2(cx + ox, cy + oy, seed) - 0.5) * 0.7) * cell
                jy = (cy + oy + 0.5 + (hash2(cx + ox, cy + oy, seed + 1) - 0.5) * 0.7) * cell
                dd = math.hypot(px - jx, py - jy)
                if dd < best:
                    best = dd
        ring = abs(best - 3.4)
        if ring < 1.3:
            return (dt - 0.04, 0.50)
        if best < 1.6:
            return (dt - 0.10, 0.90)
        return (dt, 1.0)
    return t

def tex_pintas(seed=23, cell=6.5, amp=0.10):
    """Pintas pequenas (cabeca/patas da onca)."""
    def t(px, py):
        dt = (vnoise(px * 0.2, py * 0.4, seed + 5) - 0.5) * 2 * amp
        if hash2(int(px / cell), int(py / cell), seed) < 0.30:
            jx = px % cell - cell / 2
            jy = py % cell - cell / 2
            if jx * jx + jy * jy < 1.9:
                return (dt, 0.55)
        return (dt, 1.0)
    return t

def tex_escamas(amp=0.10, seed=9):
    def t(px, py):
        v = math.sin((px + 2.1 * py) * 1.25) * math.sin((px - 2.1 * py) * 1.25)
        dt = v * amp
        n = vnoise(px * 0.09, py * 0.09, seed)
        mul = 0.66 if n < 0.40 else 1.0
        return (dt, mul)
    return t

def tex_folhas(fx=0.35, amp=0.30, seed=21):
    def t(px, py):
        n = fbm(px * fx, py * fx, seed, 3)
        return ((n - 0.5) * 2 * amp, 1.0)
    return t

def tex_casca(amp=0.22, seed=17):
    def t(px, py):
        n = vnoise(px * 0.55, py * 0.07, seed)
        return ((n - 0.5) * 2 * amp, 1.0)
    return t

def tex_ribs(cx, freq=0.85, amp=0.16):
    def t(px, py):
        dt = math.sin((px - cx) * freq) * amp
        dt += (vnoise(px * 0.3, py * 0.3, 33) - 0.5) * 0.08
        return (dt, 1.0)
    return t

def grad_barriga(y0, y1):
    """Mescla para rampa clara abaixo de y0 (saturando em y1)."""
    def g(px, py):
        v = (py - y0) / (y1 - y0)
        return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)
    return g

# ── Organismos ────────────────────────────────────────────────────────────────

def gen_lobo():
    W, H = 124, 84
    fur = tex_pelo(0.13, 0.5, 0.15, 3)
    belly = grad_barriga(46, 60)
    parts = [
        sombra(62, 78, 44, 6),
        # patas traseiras (par distante, mais escuro)
        P([('c', 40, 56, 34, 76, 6, 4)], escala(LOBO_R, 0.72), tex=fur),
        P([('c', 82, 54, 78, 76, 5.5, 3.8)], escala(LOBO_R, 0.72), tex=fur),
        # cauda peluda caida
        P([('c', 34, 44, 13, 64, 7, 5), ('e', 12, 66, 6, 7)], LOBO_R, k=6, tex=tex_pelo(0.2, 0.3, 0.2, 8)),
        # corpo
        P([('c', 40, 46, 80, 42, 17, 15), ('e', 38, 48, 15, 16), ('e', 78, 46, 13, 14)],
          LOBO_R, k=8, bevel=9, tex=fur, grad=belly, ramp2=LOBO_BR),
        # patas dianteiras (par proximo)
        P([('c', 48, 56, 44, 78, 7, 4.5), ('e', 44, 78, 5.5, 3.5)], LOBO_R, k=4, tex=fur),
        P([('c', 86, 52, 90, 78, 6.5, 4.2), ('e', 91, 78, 5.5, 3.5)], LOBO_R, k=4, tex=fur),
        # pescoco + cabeca + focinho
        P([('c', 84, 40, 97, 25, 12, 9.5), ('e', 100, 22, 10.5, 9),
           ('c', 105, 23, 118, 25, 5.8, 3.0)],
          LOBO_R, k=5, bevel=7, tex=fur, grad=grad_barriga(27, 38), ramp2=LOBO_BR),
        # orelhas
        P([('c', 93, 16, 89, 3, 4.5, 1.4)], LOBO_R, k=3, bevel=3),
        P([('c', 102, 15, 103, 2, 4.5, 1.4)], LOBO_R, k=3, bevel=3),
    ]
    decors = [
        ('cap', 90, 5, 92, 13, 1.6, (26, 24, 30), 0.9),     # interior orelha
        ('cap', 102, 4, 102, 12, 1.6, (26, 24, 30), 0.9),
        ('cap', 106, 26, 116, 27, 1.0, (30, 30, 38), 0.75), # linha da boca
        ('circ', 119, 24, 2.6, (16, 14, 16), 1.0),          # nariz
        ('circ', 118.2, 23.2, 0.9, (90, 88, 92), 0.8),
    ] + eye(101, 19, 2.7, (208, 168, 52))
    return render(W, H, parts, decors), W, H

def gen_onca():
    W, H = 132, 82
    ros = tex_rosetas(11, 13.0, 0.12)
    belly = grad_barriga(46, 60)
    parts = [
        sombra(66, 76, 48, 6),
        # patas distantes
        P([('c', 42, 54, 36, 74, 7, 5)], escala(ONCA_R, 0.72), tex=tex_pintas(24)),
        P([('c', 88, 52, 84, 74, 6.5, 4.6)], escala(ONCA_R, 0.72), tex=tex_pintas(25)),
        # cauda longa curvada
        P([('c', 36, 42, 14, 50, 6, 4.5), ('c', 14, 50, 8, 32, 4.5, 3.2)],
          ONCA_R, k=5, tex=tex_pintas(26)),
        # corpo musculoso
        P([('c', 42, 44, 86, 42, 18, 17), ('e', 40, 46, 16, 17), ('e', 86, 45, 15, 15)],
          ONCA_R, k=9, bevel=10, tex=ros, grad=belly, ramp2=ONCA_BR),
        # patas proximas (grossas)
        P([('c', 50, 54, 46, 76, 8, 5.5), ('e', 47, 76, 6.5, 4)], ONCA_R, k=4, tex=tex_pintas(27)),
        P([('c', 94, 50, 98, 76, 7.5, 5.2), ('e', 99, 76, 6.5, 4)], ONCA_R, k=4, tex=tex_pintas(28)),
        # pescoco + cabeca redonda + focinho
        P([('c', 92, 40, 106, 28, 13, 11), ('e', 108, 25, 12, 11),
           ('c', 112, 27, 125, 30, 6.5, 3.6)],
          ONCA_R, k=5, bevel=8, tex=tex_pintas(23), grad=grad_barriga(34, 46), ramp2=ONCA_BR),
        # orelhas redondas
        P([('e', 102, 14, 4.0, 4.0)], ONCA_R, k=3, bevel=3),
        P([('e', 113, 13, 4.0, 4.0)], ONCA_R, k=3, bevel=3),
        # queixo claro
        P([('e', 117, 32, 5, 3.2)], ONCA_BR, k=3, bevel=4),
    ]
    decors = [
        ('circ', 100, 11, 1.6, (40, 24, 8), 0.75),
        ('circ', 114, 10, 1.6, (40, 24, 8), 0.75),
        ('cap', 115, 29, 123, 31, 1.0, (44, 26, 8), 0.7),
        ('circ', 126, 29, 2.4, (24, 16, 14), 1.0),
        ('circ', 125.3, 28.3, 0.8, (110, 90, 84), 0.8),
        ('circ', 117, 27, 0.9, (40, 24, 8), 0.8),           # pintas focinho
        ('circ', 120, 25.5, 0.8, (40, 24, 8), 0.8),
    ] + eye(109, 21, 2.8, (150, 190, 70))
    return render(W, H, parts, decors), W, H

def gen_gazela():
    W, H = 100, 110
    fur = tex_pelo(0.16, 0.5, 0.10, 5)
    CHIFRE = [(36, 26, 14), (64, 48, 26), (94, 74, 44), (120, 98, 62)]
    parts = [
        sombra(48, 104, 36, 5),
        # pernas distantes
        P([('c', 32, 76, 26, 88, 3.6, 2.6), ('c', 26, 88, 24, 102, 2.6, 2.0)],
          escala(GAZELA_R, 0.74), k=3),
        P([('c', 62, 74, 60, 88, 3.4, 2.5), ('c', 60, 88, 62, 102, 2.5, 2.0)],
          escala(GAZELA_R, 0.74), k=3),
        # corpo elegante
        P([('c', 32, 64, 64, 60, 13.5, 12), ('e', 30, 65, 12, 12), ('e', 64, 60, 11, 11)],
          GAZELA_R, k=7, bevel=8, tex=fur, grad=grad_barriga(64, 76), ramp2=GAZELA_BR),
        # traseiro branco
        P([('e', 21, 62, 5, 9)], GAZELA_BR, k=3, bevel=4),
        # cauda curta escura
        P([('c', 18, 60, 14, 72, 2.0, 1.2)], [(20, 16, 12), (44, 38, 30), (70, 62, 52)], k=2),
        # pernas proximas
        P([('c', 38, 74, 36, 88, 4, 2.8), ('c', 36, 88, 34, 103, 2.8, 2.2)],
          GAZELA_R, k=3, tex=fur),
        P([('c', 68, 72, 70, 88, 3.8, 2.7), ('c', 70, 88, 72, 103, 2.7, 2.2)],
          GAZELA_R, k=3, tex=fur),
        # pescoco diagonal + cabeca
        P([('c', 66, 58, 80, 28, 8, 5.5), ('e', 82, 24, 7.5, 6.8),
           ('c', 86, 25, 96, 28, 4.2, 2.4)],
          GAZELA_R, k=4, bevel=5, tex=fur, grad=grad_barriga(28, 36), ramp2=GAZELA_BR),
        # orelha para tras
        P([('c', 76, 20, 66, 10, 3.4, 1.2)], GAZELA_R, k=3, bevel=3),
        # chifres longos em S (aneis escuros)
        P([('c', 80, 18, 74, 6, 2.1, 1.5), ('c', 74, 6, 76, -2, 1.5, 0.8)],
          CHIFRE, k=2, bevel=2, tex=tex_pelo(0.1, 1.7, 0.24, 12)),
        P([('c', 85, 18, 84, 5, 2.1, 1.5), ('c', 84, 5, 88, -2, 1.5, 0.8)],
          CHIFRE, k=2, bevel=2, tex=tex_pelo(0.1, 1.7, 0.24, 13)),
    ]
    decors = [
        # listra lateral escura caracteristica
        ('cap', 24, 72, 62, 70, 2.6, (74, 52, 26), 0.85),
        ('cap', 68, 13, 74, 17, 1.2, (110, 88, 60), 0.8),   # interior orelha
        ('circ', 97, 27, 1.8, (24, 18, 14), 1.0),           # focinho
        ('cap', 90, 29, 95, 29.5, 0.8, (90, 66, 40), 0.6),
        # cascos escuros
        ('cap', 24, 100, 24, 103, 2.0, (40, 30, 18), 1.0),
        ('cap', 62, 100, 62, 103, 2.0, (40, 30, 18), 1.0),
        ('cap', 34, 101, 34, 104, 2.2, (40, 30, 18), 1.0),
        ('cap', 72, 101, 72, 104, 2.2, (40, 30, 18), 1.0),
    ] + eye(83, 22, 2.4, (70, 48, 26))
    return render(W, H, parts, decors), W, H

def gen_coelho():
    W, H = 68, 60
    fur = tex_pelo(0.2, 0.55, 0.13, 4)
    parts = [
        sombra(34, 56, 24, 4),
        # orelha distante
        P([('c', 40, 22, 30, 4, 4, 2)], escala(COELHO_R, 0.8), k=3, bevel=3),
        # corpo sentado (anca grande)
        P([('e', 26, 40, 16, 15), ('c', 34, 42, 46, 38, 10, 9)],
          COELHO_R, k=7, bevel=8, tex=fur, grad=grad_barriga(42, 52), ramp2=COELHO_BR),
        # rabinho branco
        P([('e', 10, 40, 4.5, 4.5)], COELHO_BR, k=3, bevel=3),
        # pata traseira grande
        P([('c', 26, 52, 40, 54, 4.5, 3.2)], COELHO_R, k=3, tex=fur),
        # pata dianteira
        P([('c', 47, 46, 48, 55, 3.2, 2.4)], COELHO_R, k=3, tex=fur),
        # cabeca
        P([('e', 50, 26, 9.5, 8.5), ('c', 54, 28, 61, 30, 4.5, 3)],
          COELHO_R, k=4, bevel=6, tex=fur, grad=grad_barriga(29, 36), ramp2=COELHO_BR),
        # orelha proxima
        P([('c', 48, 18, 42, 2, 4.5, 2.2)], COELHO_R, k=3, bevel=3),
    ]
    decors = [
        ('cap', 43, 5, 47, 15, 1.7, (196, 140, 130), 0.85),  # interior rosa
        ('circ', 62, 29, 1.6, (188, 110, 104), 1.0),         # nariz rosa
        ('cap', 58, 32, 62, 31, 0.7, (60, 44, 32), 0.6),     # boca
        ('circ', 54, 34, 3.2, (238, 232, 222), 0.9),         # bochecha clara
    ] + eye(52, 24, 2.4, (60, 38, 20))
    return render(W, H, parts, decors), W, H

def gen_lagartixa():
    W, H = 76, 44
    def tex_lag(px, py):
        dt = (vnoise(px * 0.3, py * 0.3, 6) - 0.5) * 0.16
        if hash2(int(px / 4), int(py / 4), 19) < 0.16:
            return (dt, 0.72)
        return (dt, 1.0)
    parts = [
        sombra(38, 40, 28, 3.5),
        # cauda longa enrolada
        P([('c', 26, 28, 12, 26, 4, 2.4), ('c', 12, 26, 6, 32, 2.4, 1.2),
           ('c', 6, 32, 12, 37, 1.2, 0.7)], LAGART_R, k=3, bevel=3, tex=tex_lag),
        # patas (dedos de gecko)
        P([('c', 32, 32, 26, 39, 2.4, 1.6)], escala(LAGART_R, 0.8), k=2),
        P([('c', 48, 31, 54, 39, 2.4, 1.6)], escala(LAGART_R, 0.8), k=2),
        # corpo baixo
        P([('c', 28, 28, 50, 27, 7.5, 6.5)],
          LAGART_R, k=5, bevel=5, tex=tex_lag, grad=grad_barriga(29, 36),
          ramp2=[(150, 160, 120), (185, 194, 152), (214, 220, 182), (238, 242, 212)]),
        # cabeca achatada
        P([('e', 58, 25, 8, 5.5), ('c', 62, 25, 70, 27, 3.5, 2)],
          LAGART_R, k=4, bevel=4, tex=tex_lag),
    ]
    decors = [
        # listra dorsal
        ('cap', 24, 24, 52, 23, 1.6, (52, 66, 30), 0.65),
        # dedos
        ('circ', 24, 40, 1.1, (88, 108, 52), 1.0), ('circ', 27, 41, 1.1, (88, 108, 52), 1.0),
        ('circ', 30, 40, 1.1, (88, 108, 52), 1.0),
        ('circ', 52, 40, 1.1, (88, 108, 52), 1.0), ('circ', 55, 41, 1.1, (88, 108, 52), 1.0),
        ('circ', 58, 40, 1.1, (88, 108, 52), 1.0),
        ('circ', 71, 26, 1.1, (30, 36, 18), 0.9),            # narina
        ('cap', 64, 28, 70, 28, 0.6, (40, 50, 24), 0.7),     # boca
    ] + eye(60, 22, 2.6, (196, 150, 40))
    return render(W, H, parts, decors), W, H

def gen_serpente():
    W, H = 92, 66
    esc = tex_escamas(0.09, 9)
    parts = [
        sombra(46, 60, 34, 5),
        # anel inferior da espiral (corpo enrolado)
        P([('c', 20, 50, 46, 56, 8, 9), ('c', 46, 56, 70, 50, 9, 8),
           ('c', 70, 50, 74, 44, 8, 6)], SERP_R, k=5, bevel=7, tex=esc),
        # anel medio
        P([('c', 24, 40, 46, 44, 6.5, 7.5), ('c', 46, 44, 66, 39, 7.5, 6)],
          SERP_R, k=5, bevel=6, tex=esc),
        # chocalho erguido (cascavel)
        P([('c', 78, 40, 84, 26, 2.8, 1.3)],
          [(56, 42, 24), (92, 72, 42), (130, 106, 64), (170, 144, 96)],
          k=2, bevel=1.6, tex=tex_pelo(0.1, 1.8, 0.34, 15)),
        # pescoco erguido + cabeca triangular
        P([('c', 34, 38, 34, 22, 5.5, 4.5), ('e', 38, 16, 8.5, 5.5),
           ('c', 42, 16, 48, 18, 3.5, 2)], SERP_R, k=4, bevel=5, tex=esc),
    ]
    decors = [
        ('cap', 49, 18, 56, 19, 0.7, (168, 40, 40), 0.95),   # lingua bifurcada
        ('cap', 56, 19, 59, 17, 0.55, (168, 40, 40), 0.95),
        ('cap', 56, 19, 59, 21, 0.55, (168, 40, 40), 0.95),
        ('circ', 45, 17.5, 0.9, (30, 22, 14), 0.9),          # narina
        ('cap', 40, 19.5, 47, 19.5, 0.6, (48, 36, 22), 0.7), # boca
    ] + eye(40, 14, 2.2, (200, 160, 40))
    return render(W, H, parts, decors), W, H

def gen_carvalho():
    W, H = 160, 176
    folha = tex_folhas(0.30, 0.32, 21)
    casca = tex_casca(0.24, 17)
    parts = [
        sombra(80, 168, 52, 7),
        # tronco com raizes
        P([('c', 80, 168, 78, 96, 13, 9), ('c', 66, 170, 76, 140, 6, 7),
           ('c', 96, 170, 84, 140, 6, 7)], CARV_TR, k=7, bevel=8, tex=casca),
        # galhos principais
        P([('c', 78, 104, 52, 74, 7, 3.5), ('c', 79, 100, 108, 70, 7, 3.5)],
          CARV_TR, k=5, bevel=5, tex=casca),
        # copa: aglomerado organico de folhagem
        P([('e', 80, 58, 52, 40), ('e', 44, 74, 30, 24), ('e', 118, 72, 30, 24),
           ('e', 60, 38, 28, 22), ('e', 102, 40, 28, 22), ('e', 80, 88, 40, 20)],
          CARV_FL, k=14, bevel=16, tex=folha),
    ]
    return render(W, H, parts, ()), W, H

def gen_palmeira():
    W, H = 144, 176
    def frond(cx, cy, ang_deg, ln, droop, seed):
        """Fronde: cadeia de 3 capsulas que caem progressivamente."""
        a = math.radians(ang_deg)
        sinal = 1.0 if math.cos(a) >= 0 else -1.0   # cai sempre para baixo
        pts = [(cx, cy)]
        seg = ln / 3.0
        for i in range(3):
            a2 = a + sinal * droop * (i + 1) * 0.55
            x0, y0 = pts[-1]
            pts.append((x0 + math.cos(a2) * seg, y0 + math.sin(a2) * seg))
        dirx, diry = math.cos(a + 1.5708), math.sin(a + 1.5708)
        def t(px, py):
            v = math.sin((px * dirx + py * diry) * 2.1 + seed) * 0.30
            return (v, 1.0)
        shapes = []
        rr = [5.5, 4.0, 2.4, 1.0]
        for i in range(3):
            shapes.append(('c', pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], rr[i], rr[i + 1]))
        return P(shapes, PALM_FL, k=3.5, bevel=4, tex=t)
    def casca_palm(px, py):
        v = math.sin(py * 0.55) * 0.20
        v += (vnoise(px * 0.4, py * 0.12, 27) - 0.5) * 0.10
        return (v, 1.0)
    cx, cy = 76, 44
    parts = [
        sombra(70, 168, 44, 7),
        # tronco curvo com aneis
        P([('c', 62, 168, 66, 120, 9, 7.5), ('c', 66, 120, 72, 78, 7.5, 6),
           ('c', 72, 78, 76, 48, 6, 5)], PALM_TR, k=5, bevel=6, tex=casca_palm),
        # frondes traseiras (caem para os lados)
        frond(cx, cy, -150, 54, 0.52, 1), frond(cx, cy, -55, 50, 0.60, 2),
        frond(cx, cy, -100, 52, 0.42, 3),
        # frondes dianteiras arqueadas
        frond(cx, cy, -178, 58, 0.55, 4), frond(cx, cy, -10, 56, 0.62, 5),
        frond(cx, cy, -130, 58, 0.58, 6), frond(cx, cy, -75, 54, 0.55, 7),
        frond(cx - 2, cy + 2, 8, 50, 0.66, 8), frond(cx + 2, cy, -165, 52, 0.72, 9),
        # cocos na base da copa
        P([('e', 70, 52, 5, 5), ('e', 80, 54, 5, 5), ('e', 75, 59, 5, 5)],
          [(48, 32, 18), (78, 54, 30), (108, 78, 44), (136, 102, 62)], k=3, bevel=4),
    ]
    return render(W, H, parts, ()), W, H

def gen_cactus():
    W, H = 104, 128
    ribs_c = tex_ribs(52, 0.95, 0.15)
    parts = [
        sombra(52, 122, 30, 5),
        # braco esquerdo
        P([('c', 42, 78, 30, 74, 8, 7), ('c', 30, 74, 30, 50, 7, 6.5)],
          CACTO_R, k=5, bevel=7, tex=tex_ribs(30, 1.0, 0.14)),
        # braco direito
        P([('c', 62, 64, 76, 60, 8, 7), ('c', 76, 60, 76, 38, 7, 6.5)],
          CACTO_R, k=5, bevel=7, tex=tex_ribs(76, 1.0, 0.14)),
        # coluna principal
        P([('c', 52, 118, 52, 30, 14, 11)], CACTO_R, k=5, bevel=10, tex=ribs_c),
    ]
    decors = []
    # espinhos claros ao longo das costelas
    for (colx, y0, y1, rx) in ((52, 26, 114, 10), (30, 48, 72, 5.5), (76, 36, 58, 5.5)):
        yy = y0
        while yy < y1:
            for off in (-rx, 0, rx):
                jx = (hash2(int(colx + off), int(yy), 41) - 0.5) * 2.0
                decors.append(('circ', colx + off + jx, yy, 0.8, (235, 232, 200), 0.85))
            yy += 7
    # flor no topo
    decors += [
        ('circ', 52, 22, 4.2, (232, 110, 150), 1.0),
        ('circ', 49, 20, 2.4, (246, 160, 190), 1.0),
        ('circ', 55, 21, 2.2, (246, 160, 190), 1.0),
        ('circ', 52, 23.5, 2.2, (246, 160, 190), 1.0),
        ('circ', 52, 21.5, 1.4, (250, 220, 120), 1.0),
    ]
    return render(W, H, parts, decors), W, H

def gen_invasora():
    W, H = 88, 104
    def tex_inv(px, py):
        return ((vnoise(px * 0.3, py * 0.3, 14) - 0.5) * 0.24, 1.0)
    parts = [
        sombra(44, 98, 28, 5),
        # caule retorcido
        P([('c', 44, 98, 38, 70, 5, 4), ('c', 38, 70, 48, 46, 4, 3.2)],
          [(30, 8, 34), (52, 14, 58), (76, 22, 82), (102, 32, 106), (128, 46, 128)],
          k=4, bevel=4, tex=tex_inv),
        # folhas-espada espinhosas
        P([('c', 40, 76, 12, 62, 4.5, 0.8)], INVAS_R, k=3, bevel=3, tex=tex_inv),
        P([('c', 42, 70, 74, 58, 4.5, 0.8)], INVAS_R, k=3, bevel=3, tex=tex_inv),
        P([('c', 40, 84, 10, 88, 4.5, 0.8)], INVAS_R, k=3, bevel=3, tex=tex_inv),
        P([('c', 44, 82, 78, 84, 4.5, 0.8)], INVAS_R, k=3, bevel=3, tex=tex_inv),
        # cabeca floral bulbosa
        P([('e', 48, 34, 13, 15)], INVAS_R, k=5, bevel=9, tex=tex_inv),
        # petalas-espinho vermelhas
        P([('c', 48, 24, 40, 6, 3.5, 0.6)], INVAS_FL, k=2, bevel=2.5),
        P([('c', 50, 24, 56, 6, 3.5, 0.6)], INVAS_FL, k=2, bevel=2.5),
        P([('c', 42, 28, 28, 16, 3.2, 0.6)], INVAS_FL, k=2, bevel=2.5),
        P([('c', 55, 28, 68, 16, 3.2, 0.6)], INVAS_FL, k=2, bevel=2.5),
        P([('c', 40, 34, 24, 32, 3.0, 0.6)], INVAS_FL, k=2, bevel=2.5),
        P([('c', 57, 34, 72, 32, 3.0, 0.6)], INVAS_FL, k=2, bevel=2.5),
    ]
    decors = [
        # espinhos no caule
        ('cap', 40, 88, 34, 84, 0.9, (222, 52, 88), 0.9),
        ('cap', 41, 62, 47, 58, 0.9, (222, 52, 88), 0.9),
        ('cap', 43, 52, 37, 48, 0.9, (222, 52, 88), 0.9),
        # centro pulsante da flor
        ('circ', 48, 34, 5.5, (240, 96, 120), 0.95),
        ('circ', 48, 34, 3.0, (255, 190, 90), 1.0),
        ('circ', 48, 34, 1.4, (90, 8, 40), 1.0),
    ]
    return render(W, H, parts, decors), W, H

# ── Backgrounds ───────────────────────────────────────────────────────────────

def gen_bg_temperada():
    """Prado de floresta temperada visto de cima/frente, 1152x648."""
    W, H = 1152, 648
    b = mk(W, H)
    # arvores das bordas: (x, y, raio_copa)
    trees = []
    for i in range(14):
        trees.append((i * 88 + (hash2(i, 0, 51) - 0.5) * 40, -20 + hash2(i, 1, 51) * 46, 58 + hash2(i, 2, 51) * 30))
    for i in range(14):
        trees.append((i * 88 + (hash2(i, 3, 52) - 0.5) * 40, 648 + 16 - hash2(i, 4, 52) * 48, 60 + hash2(i, 5, 52) * 30))
    for i in range(6):
        trees.append((-16 + hash2(i, 6, 53) * 40, i * 118 + 40, 52 + hash2(i, 7, 53) * 26))
        trees.append((1152 + 14 - hash2(i, 8, 53) * 40, i * 118 + 70, 52 + hash2(i, 9, 53) * 26))
    inner = [(300, 170, 44), (760, 130, 50), (980, 250, 40), (240, 460, 46), (620, 500, 44), (900, 470, 42)]
    rocks = [(180, 300, 22, 14), (540, 220, 18, 11), (860, 360, 24, 15), (420, 430, 16, 10), (1020, 160, 18, 12)]
    flores = [(hash2(i, 0, 61) * W, hash2(i, 1, 61) * H, i) for i in range(140)]

    for y in range(H):
        for x in range(W):
            # grama base com manchas organicas
            n1 = fbm(x * 0.006, y * 0.006, 71, 3)
            n2 = vnoise(x * 0.08, y * 0.08, 72)
            g = 0.5 + (n1 - 0.5) * 1.4
            r_ = 62 + g * 40 + (n2 - 0.5) * 22
            g_ = 118 + g * 52 + (n2 - 0.5) * 26
            b_ = 40 + g * 26 + (n2 - 0.5) * 12
            # clareira central mais iluminada
            dc = ((x - 576) / 430.0) ** 2 + ((y - 340) / 290.0) ** 2
            if dc < 1.0:
                f = (1.0 - dc) * 26
                r_ += f; g_ += f; b_ += f * 0.5
            # copas de arvores (sombra + folhagem)
            for tx, ty, tr in trees:
                dx, dy = x - tx, y - ty
                dd = dx * dx + dy * dy
                if dd < (tr + 26) ** 2:
                    d = math.sqrt(dd)
                    edge = tr + fbm(math.atan2(dy, dx) * 3.0, d * 0.05, 73, 2) * 22 - 11
                    if d < edge:
                        lf = fbm(x * 0.05, y * 0.05, 74, 3)
                        sh = max(0.0, -(dx * 0.5 + dy * 0.6) / (tr + 1) * 0.5)
                        v = 0.30 + lf * 0.55 + sh * 0.35
                        r_ = 20 + v * 52
                        g_ = 48 + v * 74
                        b_ = 14 + v * 30
                    elif d < edge + 14:
                        r_ *= 0.82; g_ *= 0.85; b_ *= 0.80
            for tx, ty, tr in inner:
                dx, dy = x - tx, y - ty
                dd = dx * dx + dy * dy
                if dd < (tr + 24) ** 2:
                    d = math.sqrt(dd)
                    edge = tr + fbm(math.atan2(dy, dx) * 3.0, d * 0.05, 75, 2) * 18 - 9
                    if d < edge:
                        lf = fbm(x * 0.05, y * 0.05, 74, 3)
                        hi = max(0.0, -(dx * 0.55 + dy * 0.7) / (tr + 1))
                        v = 0.32 + lf * 0.5 + hi * 0.45
                        r_ = 22 + v * 56
                        g_ = 52 + v * 80
                        b_ = 16 + v * 32
                    elif d < edge + 16 and dy > 0:
                        r_ *= 0.78; g_ *= 0.82; b_ *= 0.76
            i = (y * W + x) * 4
            b[i] = _c(r_); b[i + 1] = _c(g_); b[i + 2] = _c(b_); b[i + 3] = 255

    # riacho serpenteante no canto inferior esquerdo
    for x in range(0, 340):
        cy = 560 + 30 * math.sin(x * 0.012) - x * 0.22
        for dy in range(-14, 15):
            yy = int(cy) + dy
            if 0 <= yy < H:
                i = (yy * W + x) * 4
                t = 1.0 - abs(dy) / 14.0
                sh = vnoise(x * 0.06, yy * 0.2, 77)
                b[i]     = _c(46 + t * 24 + sh * 20)
                b[i + 1] = _c(102 + t * 34 + sh * 22)
                b[i + 2] = _c(150 + t * 44 + sh * 24)
        # margens
        for dy in (-17, -16, -15, 15, 16, 17):
            yy = int(cy) + dy
            if 0 <= yy < H:
                i = (yy * W + x) * 4
                b[i] = _c(b[i] * 0.8); b[i + 1] = _c(b[i + 1] * 0.85); b[i + 2] = _c(b[i + 2] * 0.75)

    # pedras sombreadas
    for rx, ry, srx, sry in rocks:
        for dy in range(-sry, sry + 1):
            t = 1.0 - (dy / sry) ** 2
            if t <= 0:
                continue
            dxm = int(srx * math.sqrt(t))
            for dx in range(-dxm, dxm + 1):
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < W and 0 <= ny < H:
                    i = (ny * W + nx) * 4
                    lit = 0.55 - (dx / srx) * 0.18 - (dy / sry) * 0.22
                    n = vnoise(nx * 0.3, ny * 0.3, 78)
                    v = _c(120 * (lit + n * 0.25) + 60)
                    b[i] = v; b[i + 1] = v; b[i + 2] = _c(v - 10)
        # sombra projetada
        for dy in range(0, sry):
            for dx in range(-srx, srx + 1):
                nx, ny = rx + dx + 4, ry + sry + dy
                if 0 <= nx < W and 0 <= ny < H and (dx / srx) ** 2 + (dy / (sry * 0.6 + 1)) ** 2 < 1:
                    i = (ny * W + nx) * 4
                    b[i] = _c(b[i] * 0.82); b[i + 1] = _c(b[i + 1] * 0.85); b[i + 2] = _c(b[i + 2] * 0.8)

    # flores e tufos de grama
    for fx, fy, idx in flores:
        fx, fy = int(fx), int(fy)
        if not (10 < fx < W - 10 and 60 < fy < H - 10):
            continue
        i = (fy * W + fx) * 4
        if b[i + 2] > 110:  # dentro do riacho, pula
            continue
        h = hash2(idx, 5, 62)
        if h < 0.30:
            col = (244, 240, 236) if h < 0.15 else (240, 210, 80)
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                j = ((fy + dy) * W + fx + dx) * 4
                b[j] = col[0]; b[j + 1] = col[1]; b[j + 2] = col[2]
        else:
            for k in range(3):
                gx = fx + k - 1
                for gy in range(fy - 3 - (k == 1), fy + 1):
                    if 0 <= gx < W and 0 <= gy < H:
                        j = (gy * W + gx) * 4
                        b[j] = _c(b[j] * 0.7 + 20); b[j + 1] = _c(b[j + 1] * 0.75 + 40); b[j + 2] = _c(b[j + 2] * 0.6 + 8)
    return b, W, H

def gen_bg_deserto():
    """Deserto com dunas, mesas ao fundo e vegetacao seca, 1152x648."""
    W, H = 1152, 648
    b = mk(W, H)
    rocks = [(160, 300, 30, 18), (520, 240, 22, 14), (880, 380, 34, 20), (1040, 200, 20, 13), (340, 500, 26, 16), (700, 540, 22, 14)]
    for y in range(H):
        horizon = y < 92
        for x in range(W):
            if horizon:
                # faixa de ceu palido + mesas distantes
                t = y / 92.0
                r_ = 236 - t * 20; g_ = 214 - t * 26; b_ = 168 - t * 30
                mesa = 52 + fbm(x * 0.008, 3.0, 81, 2) * 44
                if y > mesa:
                    mh = (y - mesa) / (92.0 - mesa + 1)
                    r_ = 176 - mh * 20; g_ = 134 - mh * 16; b_ = 96 - mh * 10
            else:
                # areia com dunas onduladas
                n = fbm(x * 0.004, y * 0.007, 82, 3)
                ridge = math.sin(y * 0.030 + n * 9.0 + x * 0.0022)
                lit = 0.5 + ridge * 0.24 + (vnoise(x * 0.11, y * 0.11, 83) - 0.5) * 0.14
                r_ = 168 + lit * 78
                g_ = 132 + lit * 66
                b_ = 76 + lit * 42
            i = (y * W + x) * 4
            b[i] = _c(r_); b[i + 1] = _c(g_); b[i + 2] = _c(b_); b[i + 3] = 255

    # rochas
    for rx, ry, srx, sry in rocks:
        for dy in range(-sry, sry + 1):
            t = 1.0 - (dy / sry) ** 2
            if t <= 0:
                continue
            dxm = int(srx * math.sqrt(t))
            for dx in range(-dxm, dxm + 1):
                nx, ny = rx + dx, ry + dy
                if 0 <= nx < W and 0 <= ny < H:
                    i = (ny * W + nx) * 4
                    lit = 0.6 - (dx / srx) * 0.2 - (dy / sry) * 0.25
                    n = vnoise(nx * 0.25, ny * 0.25, 84)
                    b[i] = _c(150 * lit + n * 40 + 30)
                    b[i + 1] = _c(126 * lit + n * 34 + 24)
                    b[i + 2] = _c(100 * lit + n * 26 + 16)
        for dy in range(0, sry):
            for dx in range(-srx, srx + 1):
                nx, ny = rx + dx + 6, ry + sry + dy
                if 0 <= nx < W and 0 <= ny < H and (dx / srx) ** 2 + (dy / (sry * 0.55 + 1)) ** 2 < 1:
                    i = (ny * W + nx) * 4
                    b[i] = _c(b[i] * 0.80); b[i + 1] = _c(b[i + 1] * 0.80); b[i + 2] = _c(b[i + 2] * 0.82)

    # arbustos secos e ossadas
    for k in range(26):
        bx = int(hash2(k, 0, 85) * (W - 60)) + 30
        by = int(hash2(k, 1, 85) * (H - 200)) + 140
        n_tw = 4 + int(hash2(k, 2, 85) * 4)
        for tw in range(n_tw):
            a = -0.4 - hash2(k, tw + 3, 85) * 2.4
            ln = 7 + hash2(k, tw + 9, 85) * 9
            for st in range(int(ln)):
                nx = int(bx + math.cos(a) * st)
                ny = int(by + math.sin(a) * st)
                if 0 <= nx < W and 0 <= ny < H:
                    i = (ny * W + nx) * 4
                    b[i] = 106; b[i + 1] = 82; b[i + 2] = 48
    return b, W, H

# ── Main ──────────────────────────────────────────────────────────────────────

GERADORES = {
    'lobo':      (gen_lobo,      SDIR, 'carnivoro_lobo.png'),
    'onca':      (gen_onca,      SDIR, 'carnivoro_onca.png'),
    'serpente':  (gen_serpente,  SDIR, 'carnivoro_serpente.png'),
    'coelho':    (gen_coelho,    SDIR, 'herbivoro_coelho.png'),
    'gazela':    (gen_gazela,    SDIR, 'herbivoro_gazela.png'),
    'lagartixa': (gen_lagartixa, SDIR, 'herbivoro_lagartixa.png'),
    'carvalho':  (gen_carvalho,  SDIR, 'planta_carvalho.png'),
    'palmeira':  (gen_palmeira,  SDIR, 'planta_palmeira.png'),
    'cactus':    (gen_cactus,    SDIR, 'planta_cactus.png'),
    'invasora':  (gen_invasora,  SDIR, 'planta_invasora.png'),
    'bg_temperada': (gen_bg_temperada, TDIR, 'floresta_temperada.png'),
    'bg_deserto':   (gen_bg_deserto,   TDIR, 'fundo_deserto.png'),
}

if __name__ == "__main__":
    alvos = sys.argv[1:] or list(GERADORES)
    for nome in alvos:
        fn, d, arq = GERADORES[nome]
        buf, w, h = fn()
        save_png(os.path.join(d, arq), w, h, buf)
    print("Pronto!")
