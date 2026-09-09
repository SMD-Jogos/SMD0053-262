# DEMO — Movimento fixo, desenho variável (passo a passo)
# Rode com: python 09_demo_movimento_fixo_desenho_variavel.py   (requer pygame-ce)
#
# NÃO é tempo real. Quem dita o ritmo é o MOVIMENTO: cada ESPAÇO é um
# passo fixo de 16 ms. O DESENHO acontece quando a máquina lenta consegue
# — ela decide quanto cada quadro dura (16, 33, 50, 80 ms...).
#
#   embaixo — MOVIMENTO: um ponto por passo, sempre igualmente espaçados.
#             Passo com anel = foi desenhado. Ponto simples = ninguém viu.
#   em cima — DESENHO: a bola onde foi desenhada em cada quadro, e um
#             fantasma claro numerado para cada quadro anterior.
#
#   ESPAÇO  um passo de movimento (16 ms)
#   T       a máquina engasga: o próximo desenho atrasa 300 ms
#   A       avanço automático (4 passos por segundo) liga/desliga
#   R       recomeça

import pygame
import random

pygame.init()
LARGURA, ALTURA = 1280, 720
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Movimento fixo, desenho variável")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 30)
fonte_p = pygame.font.SysFont(None, 24)
fonte_n = pygame.font.SysFont(None, 19)

PAPEL = (250, 249, 246)
TINTA = (22, 21, 15)
MUDO = (125, 120, 106)
CINZA = (194, 188, 171)
TIJOLO = (140, 47, 30)
FANTASMA = (222, 190, 182)

X0, X1 = 100, 1180
Y_DESENHO = 250
Y_MOVIMENTO = 410
RAIO = 12

PASSO_MS = 16                                  # o passo FIXO do movimento
PX_POR_PASSO = 24
DURACOES = [16, 21, 27, 33, 40, 50, 80]        # quanto a máquina leva por quadro
                                               # (valores "tortos" de propósito:
                                               #  o desenho cai entre dois passos)

automatico = False


def desenhar_quadro(instante):
    """A máquina desenhou no instante dado: mostra a bola onde o ÚLTIMO
    passo concluído a deixou. O que sobra entre o passo e o instante é o lag."""
    global quadro, proximo_desenho_ms, ultimo_desenho_passo, ultimo_lag
    quadro += 1
    fantasmas.append((x, quadro))
    desenhados.add(n_passo)
    tempos_quadro.append(instante)
    ultimo_desenho_passo = n_passo
    ultimo_lag = instante - tempo_ms
    proximo_desenho_ms = instante + random.choice(DURACOES)


def recomecar():
    global tempo_ms, x, passos, desenhados, fantasmas, quadro, proximo_desenho_ms
    global n_passo, ultimo_desenho_passo, tempos_passo, tempos_quadro, ultimo_lag
    random.seed(3)
    tempo_ms = 0
    x = X0
    passos = [X0]            # x de cada passo (o passo 0 é a posição inicial)
    desenhados = set()       # índices dos passos que foram mostrados num desenho
    fantasmas = []           # (x, número do quadro)
    quadro = 0
    n_passo = 0
    ultimo_desenho_passo = 0
    ultimo_lag = 0           # quanto tempo depois do passo o desenho aconteceu
    proximo_desenho_ms = 0
    tempos_passo = [0]
    tempos_quadro = []
    desenhar_quadro(0)       # o jogo desenha o estado inicial: quadro 1, sem atraso


def um_passo():
    global tempo_ms, x, n_passo
    fim_do_passo = tempo_ms + PASSO_MS

    # ---- DESENHO que cai ANTES de este passo terminar ----
    # a máquina desenha no instante dela, entre dois passos: mostra a bola
    # onde o último passo (o anterior) a deixou
    while proximo_desenho_ms < fim_do_passo:
        desenhar_quadro(proximo_desenho_ms)

    # ---- MOVIMENTO: sempre 16 ms, sempre o mesmo tanto ----
    n_passo += 1
    tempo_ms = fim_do_passo
    x += PX_POR_PASSO
    passos.append(x)
    tempos_passo.append(tempo_ms)

    # desenho que cai exatamente no fim do passo (raro): mostra o passo novo
    if proximo_desenho_ms == tempo_ms:
        desenhar_quadro(tempo_ms)

    if x > X1 - 30:
        recomecar()


def engasgar():
    global proximo_desenho_ms
    proximo_desenho_ms = max(proximo_desenho_ms, tempo_ms) + 300


recomecar()
ultimo_auto = 0
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                um_passo()
            if evento.key == pygame.K_t:
                engasgar()
            if evento.key == pygame.K_a:
                automatico = not automatico
            if evento.key == pygame.K_r:
                recomecar()

    agora = pygame.time.get_ticks()
    if automatico and agora - ultimo_auto >= 250:
        um_passo()
        ultimo_auto = agora

    # ---------------- desenhar a demo ----------------
    tela.fill(PAPEL)
    tela.blit(fonte.render("Movimento fixo, desenho variável", True, TINTA), (X0, 40))
    tela.blit(fonte_p.render(
        "ESPAÇO um passo de movimento (16 ms)     T a máquina engasga     A automático     R recomeça",
        True, MUDO), (X0, 76))

    # faixa do DESENHO
    pygame.draw.line(tela, CINZA, (X0, Y_DESENHO), (X1, Y_DESENHO), 1)
    tela.blit(fonte_p.render("DESENHO — quando a máquina consegue", True, TINTA), (X0, Y_DESENHO - 104))
    tela.blit(fonte_p.render("cada quadro deixa um fantasma numerado", True, MUDO), (X0, Y_DESENHO - 80))

    def altura_num(n):
        return Y_DESENHO - RAIO - (18 if n % 2 else 34)
    for fx, n in fantasmas[:-1]:
        pygame.draw.circle(tela, FANTASMA, (int(fx), Y_DESENHO), RAIO)
        num = fonte_n.render(str(n), True, MUDO)
        tela.blit(num, (int(fx) - num.get_width() // 2, altura_num(n)))
    if fantasmas:
        fx, n = fantasmas[-1]
        pygame.draw.circle(tela, TIJOLO, (int(fx), Y_DESENHO), RAIO)
        num = fonte_n.render(str(n), True, TIJOLO)
        tela.blit(num, (int(fx) - num.get_width() // 2, altura_num(n)))

    # faixa do MOVIMENTO
    pygame.draw.line(tela, CINZA, (X0, Y_MOVIMENTO), (X1, Y_MOVIMENTO), 1)
    tela.blit(fonte_p.render("MOVIMENTO — um passo fixo de 16 ms por vez", True, TINTA), (X0, Y_MOVIMENTO - 96))
    tela.blit(fonte_p.render("anel = este passo foi desenhado    ponto simples = ninguém viu", True, MUDO), (X0, Y_MOVIMENTO - 72))
    for i, px in enumerate(passos):
        pygame.draw.circle(tela, TINTA, (int(px), Y_MOVIMENTO), 4)
        if i in desenhados:
            pygame.draw.circle(tela, TIJOLO, (int(px), Y_MOVIMENTO), 9, 2)
    if passos:
        pygame.draw.circle(tela, TINTA, (int(x), Y_MOVIMENTO), RAIO, 2)

    # o que está acontecendo
    yb = 500
    if n_passo == 0:
        tela.blit(fonte.render("aperte ESPAÇO para o primeiro passo", True, MUDO), (X0, yb))
    else:
        nao_vistos = n_passo - ultimo_desenho_passo
        tela.blit(fonte.render(
            f"passo {n_passo}   ·   tempo do jogo: {tempo_ms} ms   ·   quadros desenhados: {quadro}",
            True, TINTA), (X0, yb))
        if quadro > 0:
            if ultimo_lag == 0:
                msg = f"quadro {quadro}: desenhado exatamente no passo {ultimo_desenho_passo}"
            else:
                msg = (f"quadro {quadro}: desenhado {ultimo_lag} ms depois do passo {ultimo_desenho_passo} "
                       f"— mostrou a bola onde o passo {ultimo_desenho_passo} a deixou")
            tela.blit(fonte_p.render(msg, True, TINTA), (X0, yb + 34))
        if nao_vistos > 0:
            msg2 = f"{nao_vistos} passo{'s' if nao_vistos > 1 else ''} desde o último desenho — a máquina ainda não conseguiu desenhar"
            tela.blit(fonte_p.render(msg2, True, TIJOLO if nao_vistos > 1 else MUDO), (X0, yb + 60))
        falta = proximo_desenho_ms - tempo_ms
        tela.blit(fonte_p.render(f"próximo desenho daqui a {max(falta, 0)} ms de jogo", True, MUDO), (X0, yb + 86))

    # linha do tempo
    yt = 640
    pygame.draw.line(tela, CINZA, (X0, yt), (X1, yt), 1)
    tela.blit(fonte_p.render("linha do tempo     | passo de movimento      · quadro desenhado", True, MUDO), (X0, yt + 14))
    escala = (X1 - X0) / max(tempo_ms, 900)
    for t in tempos_passo:
        xt = int(X0 + t * escala)
        pygame.draw.line(tela, TINTA, (xt, yt - 14), (xt, yt + 2), 2)
    for t in tempos_quadro:
        xt = int(X0 + t * escala)
        pygame.draw.circle(tela, TIJOLO, (xt, yt - 24), 4)

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()