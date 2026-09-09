# DEMO — Não determinismo do passo variável (tipo 3)
# Rode com: python 09_demo_nao_determinismo.py   (requer pygame-ce)
#
# Dois painéis, a MESMA bola: mesma posição inicial, mesma velocidade,
# o MESMO código de movimento e quique.
#
#   esquerda:  dt fixo de 1/60 s     (como se a máquina fosse perfeita)
#   direita:   dt irregular           (como uma máquina real: oscila)
#              — mesma MÉDIA de 1/60, mas cada quadro é diferente
#
# No começo as bolas andam coladas. A cada quique, a da direita rebate
# num ponto ligeiramente diferente (ela entrou mais, ou menos, na parede
# naquele quadro). A diferença se acumula. Depois de alguns quiques:
# mesma jogada, dois jogos.
#
#   1   direita com dt FIXO de 1/30  (constante, mas diferente da esquerda)
#   2   direita com dt FIXO de 1/60  (idêntico à esquerda: diferença zero)
#   3   direita com dt IRREGULAR leve   (1/75 a 1/48, média 1/60)
#   4   direita com dt IRREGULAR forte  (1/120 a 1/30, média 1/60)
#   R   reinicia as duas bolas juntas
#   P   pausa
#
# Repare no modo 1: o passo é constante e MESMO ASSIM diverge. Não basta
# ser fixo — precisa ser o MESMO em todas as máquinas. É por isso que o
# tipo 4 fixa o passo no código, e não "no que a máquina der".
#
# Nada aqui é "bug". É a consequência de a física avançar em passos
# de tamanho variável. Replay, multiplayer e teste automatizado
# precisam que os dois painéis cheguem no MESMO lugar.

import pygame
import random

pygame.init()
LARGURA, ALTURA = 1100, 640
PAINEL_L, PAINEL_A = 500, 420
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Mesma jogada, dois jogos")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 26)
fonte_p = pygame.font.SysFont(None, 22)
fonte_g = pygame.font.SysFont(None, 40)

PAPEL = (250, 249, 246)
TINTA = (22, 21, 15)
MUDO = (125, 120, 106)
CINZA = (194, 188, 171)
TIJOLO = (140, 47, 30)
BEGE = (240, 238, 230)

RAIO = 10
VEL_X0, VEL_Y0 = 300.0, 230.0       # px/s
DT_FIXO = 1 / 60

# um pilar redondo no meio do campo: rebater numa CURVA amplifica
# qualquer diferença no ponto de contato (é um pinball)
PILAR = (250.0, 210.0)
PILAR_R = 60

MODOS = {
    "1": ("fixo 1/30",        (1 / 30, 1 / 30)),
    "2": ("fixo 1/60",        (1 / 60, 1 / 60)),
    "3": ("irregular leve",   (1 / 75, 1 / 48)),
    "4": ("irregular forte",  (1 / 120, 1 / 30)),
}
modo = "4"


def nova_bola():
    return {"x": 60.0, "y": 60.0, "vx": VEL_X0, "vy": VEL_Y0, "rastro": []}


def mover(b, dt):
    """O MESMO código para os dois painéis. Só o dt muda."""
    b["x"] += b["vx"] * dt
    b["y"] += b["vy"] * dt
    if b["x"] - RAIO < 0 or b["x"] + RAIO > PAINEL_L:
        b["vx"] = -b["vx"]
        b["x"] = max(RAIO, min(PAINEL_L - RAIO, b["x"]))
    if b["y"] - RAIO < 0 or b["y"] + RAIO > PAINEL_A:
        b["vy"] = -b["vy"]
        b["y"] = max(RAIO, min(PAINEL_A - RAIO, b["y"]))

    # quique no pilar: reflete a velocidade na normal do círculo
    dx, dy = b["x"] - PILAR[0], b["y"] - PILAR[1]
    dist = (dx * dx + dy * dy) ** 0.5
    if dist < RAIO + PILAR_R and dist > 0:
        nx, ny = dx / dist, dy / dist
        escalar = b["vx"] * nx + b["vy"] * ny
        if escalar < 0:                          # indo para dentro
            b["vx"] -= 2 * escalar * nx
            b["vy"] -= 2 * escalar * ny
        b["x"] = PILAR[0] + nx * (RAIO + PILAR_R)   # expulsa da superfície
        b["y"] = PILAR[1] + ny * (RAIO + PILAR_R)
    b["rastro"].append((b["x"], b["y"]))
    if len(b["rastro"]) > 900:
        b["rastro"].pop(0)


def desenhar_painel(x0, y0, b, titulo, sub):
    pygame.draw.rect(tela, BEGE, (x0, y0, PAINEL_L, PAINEL_A))
    pygame.draw.rect(tela, CINZA, (x0, y0, PAINEL_L, PAINEL_A), 1)
    pygame.draw.circle(tela, CINZA, (x0 + int(PILAR[0]), y0 + int(PILAR[1])), PILAR_R)
    if len(b["rastro"]) > 1:
        pts = [(x0 + px, y0 + py) for px, py in b["rastro"]]
        pygame.draw.lines(tela, CINZA, False, pts, 1)
    pygame.draw.circle(tela, TINTA, (x0 + int(b["x"]), y0 + int(b["y"])), RAIO)
    tela.blit(fonte.render(titulo, True, TINTA), (x0, y0 - 52))
    tela.blit(fonte_p.render(sub, True, MUDO), (x0, y0 - 28))


def reiniciar():
    global bola_fixa, bola_var, tempo, quiques, acumulador, proximo_passo
    bola_fixa, bola_var = nova_bola(), nova_bola()
    tempo, quiques = 0.0, 0
    random.seed(7)          # a "máquina real" oscila sempre do mesmo jeito
    acumulador = 0.0        # tempo real acumulado pelo painel direito
    proximo_passo = None    # tamanho do próximo passo do painel direito


reiniciar()
pausado = False
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                reiniciar()
            if evento.key == pygame.K_p:
                pausado = not pausado
            if evento.unicode in MODOS:
                modo = evento.unicode
                reiniciar()

    if not pausado:
        # os dois painéis avançam o MESMO tempo total por quadro real;
        # o da direita só divide esse tempo em passos irregulares.
        dt_min, dt_max = MODOS[modo][1]
        vx_antes = bola_fixa["vx"]

        mover(bola_fixa, DT_FIXO)

        # painel direito: acumula o tempo real e só dá o passo quando
        # juntou o tamanho do passo. Um jogo a 30 fps dá 1 passo a cada
        # 2 quadros nossos; um irregular, quando der.
        acumulador += DT_FIXO
        if proximo_passo is None:
            proximo_passo = random.uniform(dt_min, dt_max)
        while acumulador >= proximo_passo - 1e-9:
            mover(bola_var, proximo_passo)
            acumulador -= proximo_passo
            proximo_passo = random.uniform(dt_min, dt_max)

        tempo += DT_FIXO
        if bola_fixa["vx"] != vx_antes:
            quiques += 1

    diff = ((bola_fixa["x"] - bola_var["x"]) ** 2 +
            (bola_fixa["y"] - bola_var["y"]) ** 2) ** 0.5

    tela.fill(PAPEL)
    desenhar_painel(40, 110, bola_fixa, "dt fixo = 1/60",
                    "a máquina perfeita")
    nome, (dmin, dmax) = MODOS[modo]
    if dmin == dmax:
        sub = f"cada quadro dura exatamente 1/{round(1/dmin)} s"
    else:
        sub = f"oscila entre 1/{round(1/dmax)} e 1/{round(1/dmin)} s — mesma média de 1/60"
    desenhar_painel(560, 110, bola_var, f"dt {nome}", sub)

    cor = TIJOLO if diff > 5 else TINTA
    tela.blit(fonte_g.render(f"diferença: {diff:5.0f} px", True, cor), (40, 560))
    tela.blit(fonte_p.render(
        f"tempo: {tempo:5.1f} s    quiques: {quiques}      "
        "1 fixo 1/30   2 fixo 1/60   3 irregular leve   4 irregular forte   R reinicia   P pausa",
        True, MUDO), (40, 604))
    tela.blit(fonte.render("Mesmo código. Mesma jogada. Só o tamanho dos passos muda.",
                           True, TINTA), (40, 24))

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()