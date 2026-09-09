# DEMO — O tiro acertou a nave?  (ponto x volume delimitador)
# Rode com: python demo_ponto_x_volume.py   (requer pygame-ce)
#
# Mova o mouse: ele é o "tiro". Cinco painéis testam o MESMO foguete
# com volumes diferentes. Cada painel mostra ACERTOU / ERROU e quantas
# operações o teste custou.
#
#   ← / →   gira o foguete    (repare: o círculo não muda; o AABB incha)
#   T       mostra/esconde os triângulos das malhas
#   R       zera a rotação

import math
import pygame

pygame.init()
LARGURA, ALTURA = 1250, 640
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("O tiro acertou a nave?")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 26)
fonte_p = pygame.font.SysFont(None, 21)

PAPEL = (250, 249, 246)
TINTA = (22, 21, 15)
CINZA = (194, 188, 171)
NAVE = (157, 151, 137)
TIJOLO = (140, 47, 30)
VERDE = (60, 140, 80)

# o foguete, em coordenadas locais (centro em 0,0; y cresce para baixo)
FOGUETE = [(0, -70), (18, -35), (18, 20), (42, 52), (18, 42), (12, 55),
           (-12, 55), (-18, 42), (-42, 52), (-18, 20), (-18, -35)]

angulo = 0.0            # graus
mostrar_triangulos = True


# ----------------------------------------------------------------- geometria
def rotacionar(p, ang):
    r = math.radians(ang)
    c, s = math.cos(r), math.sin(r)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def pontos_mundo(cx, cy):
    return [(cx + x, cy + y) for x, y in (rotacionar(p, angulo) for p in FOGUETE)]


def fecho_convexo(pontos):
    """Cadeia monótona de Andrew."""
    pts = sorted(set(pontos))
    if len(pts) < 3:
        return pts
    def cruz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    baixo, cima = [], []
    for p in pts:
        while len(baixo) >= 2 and cruz(baixo[-2], baixo[-1], p) <= 0:
            baixo.pop()
        baixo.append(p)
    for p in reversed(pts):
        while len(cima) >= 2 and cruz(cima[-2], cima[-1], p) <= 0:
            cima.pop()
        cima.append(p)
    return baixo[:-1] + cima[:-1]


def leque(poligono, centro):
    """Triangulação em leque a partir de um ponto interior."""
    n = len(poligono)
    return [(centro, poligono[i], poligono[(i + 1) % n]) for i in range(n)]


# ----------------------------------------------------------- os cinco testes
# cada teste devolve (acertou, operacoes, detalhe)

def teste_circulo(p, cx, cy, raio):
    dx = p[0] - cx                      # 1 sub
    dy = p[1] - cy                      # 1 sub
    dist2 = dx * dx + dy * dy           # 2 mul + 1 add
    return dist2 <= raio * raio, 6, ""  # 1 cmp (raio² pré-calculado)


def teste_aabb(p, esq, topo, dir_, base):
    dentro = esq <= p[0] <= dir_ and topo <= p[1] <= base   # 4 cmp
    return dentro, 4, ""


def teste_obb(p, cx, cy, meia_l, meia_a, ang):
    # "des"rotaciona o ponto para o referencial da caixa: 2 sub, 4 mul, 2 add
    lx, ly = rotacionar((p[0] - cx, p[1] - cy), -ang)
    dentro = -meia_l <= lx <= meia_l and -meia_a <= ly <= meia_a   # 4 cmp
    return dentro, 12, ""


def ponto_em_triangulo(p, a, b, c):
    # três produtos vetoriais: o ponto está do mesmo lado das três arestas?
    def lado(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1, d2, d3 = lado(p, a, b), lado(p, b, c), lado(p, c, a)
    tem_neg = d1 < 0 or d2 < 0 or d3 < 0
    tem_pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (tem_neg and tem_pos)


def teste_malha(p, triangulos):
    ops = 0
    for i, (a, b, c) in enumerate(triangulos):
        ops += 18                       # ~3 produtos vetoriais + 3 sinais
        if ponto_em_triangulo(p, a, b, c):
            return True, ops, f"{i + 1} de {len(triangulos)} triângulos"
    return False, ops, f"{len(triangulos)} de {len(triangulos)} triângulos"


# --------------------------------------------------------------------- painéis
def desenhar_painel(x0, titulo, subtitulo, mouse, tipo):
    cx, cy = x0 + 125, 330
    pts = pontos_mundo(cx, cy)

    # o foguete
    pygame.draw.polygon(tela, NAVE, pts)

    if tipo == "circulo":
        raio = max(math.hypot(x, y) for x, y in FOGUETE)
        pygame.draw.circle(tela, TIJOLO, (cx, cy), int(raio), 2)
        acertou, ops, det = teste_circulo(mouse, cx, cy, raio)

    elif tipo == "aabb":
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        esq, dir_, topo, base = min(xs), max(xs), min(ys), max(ys)
        pygame.draw.rect(tela, TIJOLO, (esq, topo, dir_ - esq, base - topo), 2)
        acertou, ops, det = teste_aabb(mouse, esq, topo, dir_, base)

    elif tipo == "obb":
        xs = [p[0] for p in FOGUETE]; ys = [p[1] for p in FOGUETE]
        meia_l = (max(xs) - min(xs)) / 2
        meia_a = (max(ys) - min(ys)) / 2
        # o centro da caixa local não é (0,0) porque o foguete é assimétrico em y
        cyl = (max(ys) + min(ys)) / 2
        cantos = [(-meia_l, cyl - meia_a), (meia_l, cyl - meia_a),
                  (meia_l, cyl + meia_a), (-meia_l, cyl + meia_a)]
        cantos_m = [(cx + rx, cy + ry) for rx, ry in (rotacionar(c, angulo) for c in cantos)]
        pygame.draw.polygon(tela, TIJOLO, cantos_m, 2)
        # centro da caixa no mundo
        ccx, ccy = rotacionar((0, cyl), angulo)
        acertou, ops, det = teste_obb(mouse, cx + ccx, cy + ccy, meia_l, meia_a, angulo)

    elif tipo == "fecho":
        casco = fecho_convexo(pts)
        tris = leque(casco, (cx, cy))
        if mostrar_triangulos:
            for t in tris:
                pygame.draw.polygon(tela, CINZA, t, 1)
        pygame.draw.polygon(tela, TIJOLO, casco, 2)
        acertou, ops, det = teste_malha(mouse, tris)

    else:  # contorno
        tris = leque(pts, (cx, cy))
        if mostrar_triangulos:
            for t in tris:
                pygame.draw.polygon(tela, CINZA, t, 1)
        pygame.draw.polygon(tela, TIJOLO, pts, 2)
        acertou, ops, det = teste_malha(mouse, tris)

    # textos
    tela.blit(fonte.render(titulo, True, TINTA), (x0 + 12, 60))
    tela.blit(fonte_p.render(subtitulo, True, (125, 120, 106)), (x0 + 12, 86))

    cor = VERDE if acertou else TIJOLO
    txt = "ACERTOU" if acertou else "errou"
    tela.blit(fonte.render(txt, True, cor), (x0 + 12, 500))
    tela.blit(fonte_p.render(f"~{ops} operações", True, TINTA), (x0 + 12, 528))
    if det:
        tela.blit(fonte_p.render(det, True, (125, 120, 106)), (x0 + 12, 550))

    # divisória
    pygame.draw.line(tela, CINZA, (x0 + 250, 50), (x0 + 250, 600), 1)


PAINEIS = [
    ("Círculo", "centro + raio", "circulo"),
    ("AABB", "alinhada aos eixos", "aabb"),
    ("OBB", "orientada ao objeto", "obb"),
    ("Fecho convexo", "casco -> triângulos", "fecho"),
    ("Contorno", "polígono -> triângulos", "contorno"),
]

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_t:
                mostrar_triangulos = not mostrar_triangulos
            if evento.key == pygame.K_r:
                angulo = 0.0

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        angulo -= 1.5
    if teclas[pygame.K_RIGHT]:
        angulo += 1.5

    mouse = pygame.mouse.get_pos()

    tela.fill(PAPEL)
    for i, (t, st, tipo) in enumerate(PAINEIS):
        desenhar_painel(i * 250, t, st, mouse, tipo)

    # o tiro
    pygame.draw.circle(tela, TIJOLO, mouse, 6)

    tela.blit(fonte_p.render(
        f"rotação: {angulo:.0f}°     ←/→ gira   T triângulos   R zera     "
        "o mouse é o tiro", True, (125, 120, 106)), (12, 14))

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()