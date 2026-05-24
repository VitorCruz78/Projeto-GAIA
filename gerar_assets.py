#!/usr/bin/env python3
"""Gera sprites pixel art e backgrounds para Projeto Gaia (stdlib apenas)."""
import struct, zlib, math, os

BASE   = os.path.dirname(os.path.abspath(__file__))
SDIR   = os.path.join(BASE, "assets/sprites/organismos")
TDIR   = os.path.join(BASE, "assets/tilesets")

# ── PNG helpers ───────────────────────────────────────────────────────────────

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
    idat = chunk(b'IDAT', zlib.compress(bytes(raw), 1))
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + ihdr + idat + chunk(b'IEND', b''))
    print(f"  OK  {os.path.basename(path)}")

def mk(w, h):
    return bytearray(w * h * 4)

def _c(v):
    return max(0, min(255, int(v)))

def sp(b, w, h, x, y, r, g, bl, a=255):
    if 0 <= x < w and 0 <= y < h:
        i = (y*w+x)*4
        b[i]=_c(r); b[i+1]=_c(g); b[i+2]=_c(bl); b[i+3]=_c(a)

def ell(b, w, h, cx, cy, rx, ry, r, g, bl, a=255):
    for dy in range(-ry, ry+1):
        t = 1.0 - (dy/ry)**2
        if t <= 0: continue
        dx_max = int(rx * math.sqrt(t))
        for dx in range(-dx_max, dx_max+1):
            sp(b, w, h, cx+dx, cy+dy, r, g, bl, a)

def rct(b, w, h, x1, y1, x2, y2, r, g, bl, a=255):
    for y in range(max(0,y1), min(h, y2+1)):
        for x in range(max(0,x1), min(w, x2+1)):
            sp(b, w, h, x, y, r, g, bl, a)

def tri(b, w, h, pts, r, g, bl, a=255):
    miny = max(0, min(p[1] for p in pts))
    maxy = min(h-1, max(p[1] for p in pts))
    n = len(pts)
    for y in range(miny, maxy+1):
        xs = []
        for i in range(n):
            ax,ay = pts[i]; bx,by = pts[(i+1)%n]
            if ay != by and min(ay,by) <= y <= max(ay,by):
                xs.append(int(ax + (y-ay)/(by-ay)*(bx-ax)))
        if len(xs) >= 2:
            xs.sort()
            for x in range(xs[0], xs[-1]+1):
                sp(b, w, h, x, y, r, g, bl, a)

# ── Sprites ───────────────────────────────────────────────────────────────────

def gen_lobo():
    """Lobo cinza, perfil virado para direita, 72x52"""
    W, H = 72, 52
    b = mk(W, H)
    M  = (88,  88, 100, 255)   # cinza médio
    LT = (145,145, 158, 255)   # cinza claro (barriga)
    DK = (48,  48,  58, 255)   # cinza escuro (orelhas/focinho)
    EY = (210,185,  30, 255)   # olho amarelo
    NK = (15,  15,  15, 255)   # nariz/pupila

    # Cauda (esquerda, curvada para cima)
    ell(b,W,H, 8,20, 5,12, *M)
    ell(b,W,H, 9,14, 3, 7, *M)
    ell(b,W,H,10, 9, 2, 4, *LT)

    # Corpo
    ell(b,W,H, 30,36, 20,11, *M)
    # Barriga
    ell(b,W,H, 30,40, 14, 7, *LT)

    # Pescoço
    ell(b,W,H, 45,29,  7, 7, *M)

    # Cabeça
    ell(b,W,H, 52,23, 11,10, *M)

    # Focinho (mais claro)
    ell(b,W,H, 60,28,  7, 5, *LT)

    # Orelhas (triângulos)
    tri(b,W,H, [(42,22),(46,10),(51,22)], *DK)
    tri(b,W,H, [(50,22),(54,10),(58,22)], *DK)
    tri(b,W,H, [(43,22),(46,14),(50,22)], *M)
    tri(b,W,H, [(51,22),(54,14),(57,22)], *M)

    # Patas (4)
    rct(b,W,H, 43,45, 46,51, *M)
    rct(b,W,H, 49,45, 52,51, *M)
    rct(b,W,H, 20,45, 23,51, *M)
    rct(b,W,H, 26,45, 29,51, *M)
    # Pés
    ell(b,W,H, 44,51, 4,2, *DK)
    ell(b,W,H, 50,51, 4,2, *DK)
    ell(b,W,H, 21,51, 4,2, *DK)
    ell(b,W,H, 27,51, 4,2, *DK)

    # Olho
    ell(b,W,H, 56,20, 2,2, *EY)
    sp(b,W,H, 56,20, *NK)

    # Nariz
    ell(b,W,H, 65,29, 2,2, *NK)
    return b, W, H

def gen_onca():
    """Onça/jaguar laranja com manchas, 72x52"""
    W, H = 72, 52
    b = mk(W, H)
    OR = (210,140, 20, 255)   # laranja corpo
    LT = (240,200, 80, 255)   # amarelo claro barriga
    SP = ( 55, 28,  0, 210)   # mancha escura
    EY = ( 50,200, 50, 255)   # olho verde
    NK = ( 15, 15, 15, 255)
    DK = (150, 85, 10, 255)   # patas/detalhes

    # Cauda grossa e curvada
    ell(b,W,H,  8,24, 5, 8, *OR)
    ell(b,W,H,  7,17, 4, 7, *OR)
    ell(b,W,H,  8,11, 3, 5, *OR)
    ell(b,W,H,  9, 7, 2, 3, *LT)

    # Corpo (mais largo que lobo)
    ell(b,W,H, 30,35, 21,12, *OR)
    ell(b,W,H, 30,40, 15, 7, *LT)

    # Pescoço
    ell(b,W,H, 46,28,  8, 8, *OR)

    # Cabeça (mais redonda)
    ell(b,W,H, 54,22, 12,11, *OR)

    # Focinho
    ell(b,W,H, 62,28,  7, 5, *LT)

    # Orelhas arredondadas
    ell(b,W,H, 46,13,  4, 4, *OR)
    ell(b,W,H, 55,12,  4, 4, *OR)
    ell(b,W,H, 46,13,  2, 2, *SP)
    ell(b,W,H, 55,12,  2, 2, *SP)

    # Manchas no corpo
    ell(b,W,H, 20,32, 4,3, *SP)
    ell(b,W,H, 29,28, 4,3, *SP)
    ell(b,W,H, 38,31, 4,3, *SP)
    ell(b,W,H, 24,38, 3,2, *SP)
    ell(b,W,H, 33,37, 3,2, *SP)

    # Patas
    rct(b,W,H, 44,43, 47,51, *OR)
    rct(b,W,H, 50,43, 53,51, *OR)
    rct(b,W,H, 19,43, 22,51, *OR)
    rct(b,W,H, 25,43, 28,51, *OR)
    ell(b,W,H, 45,51, 4,2, *DK)
    ell(b,W,H, 51,51, 4,2, *DK)
    ell(b,W,H, 20,51, 4,2, *DK)
    ell(b,W,H, 26,51, 4,2, *DK)

    # Olho
    ell(b,W,H, 58,19, 2,2, *EY)
    sp(b,W,H, 58,19, *NK)

    # Nariz
    ell(b,W,H, 67,29, 2,2, *NK)
    return b, W, H

def gen_gazela():
    """Gazela bege com chifres e pescoço longo, 52x72"""
    W, H = 52, 72
    b = mk(W, H)
    BD = (190,155, 90, 255)  # corpo bege
    LT = (230,210,165, 255)  # barriga clara
    DK = (120, 88, 45, 255)  # cascos/detalhes
    HN = ( 80, 58, 28, 255)  # chifres
    EY = ( 15, 15, 15, 255)
    WH = (240,240,240, 255)  # rabo branco

    # Corpo (mais oval, menor)
    ell(b,W,H, 24,34, 15,10, *BD)
    ell(b,W,H, 24,38,  9, 6, *LT)

    # Pescoço longo e elegante
    rct(b,W,H, 30,18, 36,32, *BD)
    ell(b,W,H, 33,19,  4, 4, *BD)

    # Cabeça pequena
    ell(b,W,H, 38,13,  8, 7, *BD)

    # Focinho fino
    ell(b,W,H, 44,16,  5, 4, *LT)

    # Chifres (para cima)
    rct(b,W,H, 35, 3, 36,11, *HN)
    rct(b,W,H, 39, 3, 40,11, *HN)
    # Curvatura dos chifres
    sp(b,W,H, 34, 4, *HN); sp(b,W,H, 34, 3, *HN)
    sp(b,W,H, 40, 4, *HN); sp(b,W,H, 41, 3, *HN)

    # Orelha
    tri(b,W,H, [(30,11),(33, 5),(37,11)], *BD)

    # Pernas longas e finas (4)
    rct(b,W,H, 33,42, 35,61, *BD)
    rct(b,W,H, 37,42, 39,61, *BD)
    rct(b,W,H, 14,42, 16,61, *BD)
    rct(b,W,H, 18,42, 20,61, *BD)

    # Cascos
    rct(b,W,H, 32,60, 36,64, *DK)
    rct(b,W,H, 36,60, 40,64, *DK)
    rct(b,W,H, 13,60, 17,64, *DK)
    rct(b,W,H, 17,60, 21,64, *DK)

    # Rabo branco (esquerda)
    ell(b,W,H,  9,30,  3, 5, *WH)

    # Olho
    ell(b,W,H, 41,11,  2, 2, *EY)
    # Nariz
    ell(b,W,H, 47,17,  2, 1, *EY)
    return b, W, H

def gen_invasora():
    """Planta invasora roxa/vermelha com espinhos, 52x64"""
    W, H = 52, 64
    b = mk(W, H)
    ST = ( 70, 20, 80, 255)   # caule roxo
    LF = (120, 15,100, 255)   # folhas roxo-escuro
    TH = (190,  0, 60, 255)   # espinhos vermelho-vivo
    DK = ( 35,  5, 40, 255)   # base escura
    CT = (200, 50,150, 255)   # centro (brilhante)

    # Base/raízes
    rct(b,W,H, 12,56, 39,62, *DK)
    rct(b,W,H, 16,58, 35,64, *DK)

    # Caule central
    rct(b,W,H, 23,18, 28,58, *ST)

    # Folhas laterais em leque
    ell(b,W,H, 11,30, 13, 6, *LF)
    ell(b,W,H,  8,22,  9, 5, *LF)
    ell(b,W,H, 40,30, 13, 6, *LF)
    ell(b,W,H, 43,22,  9, 5, *LF)
    # Topo
    ell(b,W,H, 25,15,  9, 7, *LF)

    # Espinhos (triângulos apontados)
    tri(b,W,H, [(10,27),( 2,23),(12,32)], *TH)
    tri(b,W,H, [( 7,20),( 0,16),( 9,24)], *TH)
    tri(b,W,H, [(40,27),(49,23),(38,32)], *TH)
    tri(b,W,H, [(44,20),(51,16),(42,24)], *TH)
    tri(b,W,H, [(21,13),(25, 4),(29,13)], *TH)
    # Espinho topo-esquerda e topo-direita
    tri(b,W,H, [(15,20),( 8,15),(17,25)], *TH)
    tri(b,W,H, [(37,20),(44,15),(35,25)], *TH)

    # Centros brilhantes
    ell(b,W,H, 25,15, 4,4, *CT)
    ell(b,W,H, 11,30, 4,3, *CT)
    ell(b,W,H, 40,30, 4,3, *CT)

    # Olho central (símbolo de ameaça)
    ell(b,W,H, 25,15, 2,2, *DK)
    return b, W, H

# ── Backgrounds ───────────────────────────────────────────────────────────────

def gen_bg_temperada():
    """Floresta Temperada: prado verde com árvores nas bordas, 576x324"""
    W, H = 576, 324
    b = bytearray(W * H * 4)

    # 1. Base: cor sólida de grama com micro-variação hash (sem padrão visível)
    for y in range(H):
        for x in range(W):
            # hash determinístico simples → variação pequena sem padrão
            h = (x * 2654435761 ^ y * 2246822519) & 0xFFFFFFFF
            v = (h >> 16) & 0x1F  # 0..31
            r  = _c(68  + v - 16)
            g  = _c(130 + v - 8)
            bl = _c(42  + (v>>1) - 8)
            i = (y*W+x)*4
            b[i]=r; b[i+1]=g; b[i+2]=bl; b[i+3]=255

    # 2. Clarear área central (onde os animais jogam)
    cx, cy = W//2, H//2
    for y in range(H):
        for x in range(W):
            dist = ((x-cx)/210)**2 + ((y-cy)/140)**2
            if dist < 1.0:
                f = int((1.0-dist) * 30)
                i = (y*W+x)*4
                b[i]  =_c(b[i]  +f)
                b[i+1]=_c(b[i+1]+f)
                b[i+2]=_c(b[i+2]+f//2)

    # 3. Manchas de copas de árvore nas bordas (verde bem escuro)
    trees = [
        # borda superior
        (0,0,70,55),(100,0,65,50),(210,0,75,55),(330,0,68,52),(450,0,70,50),(545,0,60,48),
        # borda inferior
        (0,324,72,55),(105,324,68,52),(220,324,75,58),(350,324,70,54),(470,324,68,50),(550,324,62,48),
        # borda esquerda
        (0,80,55,65),(0,170,52,68),(0,255,55,62),
        # borda direita
        (576,80,55,65),(576,175,52,68),(576,258,55,62),
        # cantos reforçados
        (0,0,80,70),(576,0,80,70),(0,324,80,70),(576,324,80,70),
        # árvores internas esparsas
        (140,90,42,35),(290,70,45,38),(420,100,40,34),(180,240,42,36),(360,250,44,37),(500,220,40,34),
    ]
    for tx,ty,trx,try_ in trees:
        for dy in range(-try_, try_+1):
            t = 1.0-(dy/try_)**2
            if t<=0: continue
            dx_max = int(trx*math.sqrt(t))
            for dx in range(-dx_max, dx_max+1):
                nx, ny = tx+dx, ty+dy
                if 0<=nx<W and 0<=ny<H:
                    i=(ny*W+nx)*4
                    # verde escuro de copa
                    b[i]  =_c(b[i]  *0.55 + 25)
                    b[i+1]=_c(b[i+1]*0.75 + 30)
                    b[i+2]=_c(b[i+2]*0.50 + 10)

    # 4. Pedras cinza dispersas
    rocks = [(88,148,10,7),(248,228,9,6),(468,182,10,7),(372,78,8,6),(125,288,9,6),(490,95,8,5)]
    for rx,ry,srx,sry in rocks:
        for dy in range(-sry, sry+1):
            t = 1.0-(dy/sry)**2
            if t<=0: continue
            dx_max = int(srx*math.sqrt(t))
            for dx in range(-dx_max, dx_max+1):
                nx, ny = rx+dx, ry+dy
                if 0<=nx<W and 0<=ny<H:
                    i=(ny*W+nx)*4
                    shade = _c(100 + dx*3)
                    b[i]=shade; b[i+1]=shade; b[i+2]=_c(shade-8)

    # 5. Trilhinha de água (pequena)
    for x in range(60, 140):
        wy = _c(int(155 + 12*math.sin(x*0.18)))
        for dy in range(-5, 6):
            ny = wy+dy
            if 0<=ny<H:
                i=(ny*W+x)*4
                b[i]=_c(60+dy*3); b[i+1]=_c(130+dy*2); b[i+2]=_c(175+dy*3)

    return b, W, H

def gen_bg_deserto():
    """Deserto: areia com rochas e textura, 576x324"""
    W, H = 576, 324
    b = bytearray(W * H * 4)
    sin, cos = math.sin, math.cos

    for y in range(H):
        # Gradiente sutil: mais claro em cima (céu/luz)
        sky_blend = max(0.0, 1.0 - y/H*2.5)
        for x in range(W):
            n = (sin(x*0.07+0.5)*sin(y*0.08+1.0)
               + sin(x*0.15-0.8)*cos(y*0.12+0.3)*0.4
               + cos(x*0.05+1.5)*sin(y*0.06-1.0)*0.3)

            r  = _c(195 + n*18 + sky_blend*20)
            g  = _c(165 + n*14 + sky_blend*15)
            bl = _c( 90 + n* 8 + sky_blend*10)

            i=(y*W+x)*4
            b[i]=r; b[i+1]=g; b[i+2]=bl; b[i+3]=255

    # Rochas (grupos)
    rock_groups = [
        (80,80,18,12),(240,60,20,14),(420,90,16,11),(550,70,14,10),
        (50,200,16,11),(180,230,22,14),(340,210,18,12),(500,225,20,13),
        (100,280,14,10),(260,270,16,11),(450,280,18,12),
    ]
    for rx,ry,srx,sry in rock_groups:
        for dy in range(-sry,sry+1):
            t = 1.0-(dy/sry)**2
            if t<=0: continue
            dx_max = int(srx*math.sqrt(t))
            for dx in range(-dx_max, dx_max+1):
                nx,ny = rx+dx,ry+dy
                if 0<=nx<W and 0<=ny<H:
                    shade = 0.7 + 0.3*((dx/srx)**2+(dy/sry)**2)
                    i=(ny*W+nx)*4
                    b[i]=_c(130*shade); b[i+1]=_c(115*shade); b[i+2]=_c(95*shade)

    # Sombras de pedras (lado direito-baixo)
    for rx,ry,srx,sry in rock_groups:
        for dy in range(-sry//2, sry//3+1):
            for dx in range(0, srx+4):
                nx,ny = rx+dx+srx//2, ry+dy+sry//2+2
                if 0<=nx<W and 0<=ny<H:
                    i=(ny*W+nx)*4
                    b[i]=_c(b[i]-20); b[i+1]=_c(b[i+1]-18); b[i+2]=_c(b[i+2]-10)

    return b, W, H

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Gerando sprites...")
    b,w,h = gen_lobo();     save_png(os.path.join(SDIR,"carnivoro_lobo.png"),     w,h,b)
    b,w,h = gen_onca();     save_png(os.path.join(SDIR,"carnivoro_onca.png"),     w,h,b)
    b,w,h = gen_gazela();   save_png(os.path.join(SDIR,"herbivoro_gazela.png"),   w,h,b)
    b,w,h = gen_invasora(); save_png(os.path.join(SDIR,"planta_invasora.png"),    w,h,b)

    print("Gerando backgrounds...")
    b,w,h = gen_bg_temperada(); save_png(os.path.join(TDIR,"floresta_temperada.png"), w,h,b)
    b,w,h = gen_bg_deserto();   save_png(os.path.join(TDIR,"fundo_deserto.png"),      w,h,b)

    print("Pronto!")
