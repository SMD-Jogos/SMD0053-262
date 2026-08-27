# DEMO 1 — A DOR: máquinas de tipos diferentes
# Rode com: python demo2_tipos_diferentes.py  (requer pygame-ce)
#
# O movimento é "x += 5 POR FRAME". As teclas simulam máquinas diferentes:
#
#   1 = máquina fraca (15 fps)      3 = a "máquina esperada" (60 fps)
#   2 = máquina modesta (30 fps)    4 = PC gamer (240 fps)*
#   0 = FREIO NENHUM — vsync desligado, o loop na velocidade bruta da CPU
#
# * com vsync ligado, o 240 esbarra no teto da TELA (60/120 fps conforme
#   o monitor) — e o painel avisa. É proposital: o freio da tela existe.
#
# Dois freios diferentes aparecem nesta demo:
#   - o do RELÓGIO (tick)  → teclas 1–4
#   - o da TELA (vsync)    → sempre ligado nas teclas 1–4, desligado na 0
# Na tecla 0 não há freio algum: a bola dispara na velocidade da máquina.
#
# A pergunta para a turma: "como vender um jogo cuja velocidade muda
# conforme a máquina do cliente?" (é o motivo do botão TURBO existir!)

import pygame

pygame.init()
pygame.display.set_caption("Demo 2 — máquinas de tipos diferentes")


def abrir_janela(com_vsync):
    """Recria a janela com ou sem vsync (o freio da tela)."""
    if com_vsync:
        try:
            return pygame.display.set_mode((800, 420), pygame.SCALED, vsync=1)
        except Exception:
            pass  # vsync indisponível nesta máquina: segue sem
    return pygame.display.set_mode((800, 420))


tela = abrir_janela(com_vsync=True)
vsync_ligado = True
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 26)
fonte_p = pygame.font.SysFont(None, 22)

x = 50.0
velocidade = 5   # pixels POR FRAME — aí mora o problema
raio = 20
fps_alvo = 60    # 0 = freio nenhum

teto_da_tela = 0.0   # maior FPS visto COM vsync (o refresh do monitor)

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                if not vsync_ligado:                 # religando o freio da tela
                    tela = abrir_janela(com_vsync=True)
                    vsync_ligado = True
                if evento.key == pygame.K_1: fps_alvo = 15
                if evento.key == pygame.K_2: fps_alvo = 30
                if evento.key == pygame.K_3: fps_alvo = 60
                if evento.key == pygame.K_4: fps_alvo = 240
            if evento.key == pygame.K_0:             # FREIO NENHUM
                fps_alvo = 0
                tela = abrir_janela(com_vsync=False)
                vsync_ligado = False

    # movimento preso ao frame: mais frames por segundo = bola mais rápida
    x += velocidade
    if x + raio >= 800 or x - raio <= 0:
        velocidade = -velocidade
        x = max(raio, min(800 - raio, x))  # tira a bola da parede

    fps_real = relogio.get_fps()
    if vsync_ligado and fps_alvo == 240:
        teto_da_tela = max(teto_da_tela, fps_real)

    tela.fill((10, 25, 60))

    # linha central estilo Pong, só pelo charme
    for y in range(0, 420, 30):
        pygame.draw.rect(tela, (29, 47, 94), (398, y, 4, 15))

    pygame.draw.circle(tela, (255, 165, 0), (int(x), 230), raio)

    # ---------- painel ----------
    if fps_alvo == 0:
        pedido_txt = "FREIO NENHUM"
        freio_txt = "freio ativo: nenhum (vsync desligado, tick livre)"
    else:
        pedido_txt = f"{fps_alvo} fps"
        freio_txt = "freios ativos: relógio (tick) + tela (vsync)"

    px_por_seg = abs(velocidade) * fps_real  # 5 px/frame x frames/s

    linhas = [
        ((255, 255, 255), f"pedido: {pedido_txt}     real: {fps_real:.0f} fps"),
        ((255, 165, 0),   f"velocidade efetiva: {px_por_seg:.0f} pixels por segundo"),
        ((159, 176, 208), freio_txt),
        ((159, 176, 208), "no código: x += 5 por FRAME — a mesma linha, sempre"),
    ]
    for i, (cor, linha) in enumerate(linhas):
        tela.blit(fonte.render(linha, True, cor), (20, 16 + i * 28))

    # aviso honesto quando a tela é o gargalo
    if vsync_ligado and fps_alvo > 0 and fps_real > 0 and fps_real < fps_alvo * 0.9:
        aviso = (f"a TELA não passa de {teto_da_tela:.0f} fps "
                 f"— pedir {fps_alvo} não adianta")
        tela.blit(fonte_p.render(aviso, True, (229, 72, 77)), (20, 132))

    ajuda = "1 (15) · 2 (30) · 3 (60) · 4 (240) · 0 (FREIO NENHUM)"
    txt = fonte_p.render(ajuda, True, (159, 176, 208))
    tela.blit(txt, txt.get_rect(center=(400, 398)))

    pygame.display.flip()

    # o freio do relógio: tick(N) segura o loop em N voltas por segundo.
    # tick() sem argumento só MEDE — não segura nada.
    if fps_alvo > 0:
        relogio.tick(fps_alvo)
    else:
        relogio.tick()

pygame.quit()