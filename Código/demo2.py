# DEMO — OS INTERRUPTORES: o que cada parte do ciclo faz pelo jogo
# Rode com: python demo_interruptores.py  (requer pygame-ce)
#
# A cada volta do loop, três coisas acontecem: o jogo ESCUTA o jogador,
# MOVE o mundo e DESENHA a tela. Esta demo desliga cada uma ao vivo:
#
#   E = para de ESCUTAR (religa sozinha após 5s — senão a janela fica surda!)
#   M = para de MOVER   (liga/desliga)
#   D = para de DESENHAR (liga/desliga)
#
# O que observar com a turma:
#   E desligado -> a janela fica SURDA: nem o X fecha, nem teclas respondem.
#                  (no Mac/Windows o sistema pode até marcar "não respondendo")
#   M desligado -> a tela continua viva (60 qps), mas o mundo virou FOTO.
#   D desligado -> a tela congela... mas o mundo CONTINUA! Ao religar (D),
#                  a bola reaparece LONGE de onde congelou — ela andou no
#                  escuro. Mover e desenhar são coisas separadas.
#
# Os contadores no painel provam: o loop nunca parou de girar — só
# pulamos partes dele. E cada parte que falta quebra o jogo de um
# jeito diferente.

import pygame

pygame.init()
tela = pygame.display.set_mode((800, 460))
pygame.display.set_caption("Demo — os interruptores do ciclo")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 26)
fonte_p = pygame.font.SysFont(None, 22)

# a bola de sempre
x = 400.0
y = 260.0
vel_x = 5
vel_y = 4
raio = 20

# os três interruptores
escutando = True
movendo = True
desenhando = True
religar_escuta_em = 0        # instante (ms) de religar a escuta
ultimo_quadro = False        # desenha 1 quadro final ao desligar o desenho

# contadores: quantas vezes cada parte rodou
voltas = 0
c_escutar = 0
c_mover = 0
c_desenhar = 0

rodando = True
while rodando:
    voltas += 1
    agora = pygame.time.get_ticks()

    # trava de segurança: a escuta religa sozinha após 5 segundos
    if not escutando and agora >= religar_escuta_em:
        escutando = True

    # 1) ESCUTAR o jogador ------------------------------------------
    if escutando:
        c_escutar += 1
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e:
                    escutando = False
                    religar_escuta_em = agora + 5000   # 5 s de surdez
                if evento.key == pygame.K_m:
                    movendo = not movendo
                if evento.key == pygame.K_d:
                    desenhando = not desenhando
                    if not desenhando:
                        # desenha UM último quadro com o painel já em
                        # "DESLIGADO" — a tela congela dizendo a verdade
                        ultimo_quadro = True
    # (se não escutamos, os eventos se acumulam na fila e a janela
    #  fica surda — repare que nem o X funciona)

    # 2) MOVER o mundo ----------------------------------------------
    if movendo:
        c_mover += 1
        x += vel_x
        y += vel_y
        if x + raio >= 800 or x - raio <= 0:
            vel_x = -vel_x
            x = max(raio, min(800 - raio, x))
        if y + raio >= 460 or y - raio <= 0:
            vel_y = -vel_y
            y = max(raio, min(460 - raio, y))

    # 3) DESENHAR a tela --------------------------------------------
    if desenhando or ultimo_quadro:
        ultimo_quadro = False
        c_desenhar += 1
        tela.fill((10, 25, 60))
        pygame.draw.circle(tela, (255, 165, 0), (int(x), int(y)), raio)

        # painel: estado dos interruptores + contadores
        def led(ligado):
            return "LIGADO" if ligado else "DESLIGADO"

        surdez = ""
        if not escutando:
            surdez = f"  (religa em {max(0, (religar_escuta_em - agora)) / 1000:.0f}s)"

        linhas = [
            ((255, 255, 255), f"voltas do loop: {voltas}"),
            ((120, 200, 130) if escutando else (229, 72, 77),
             f"[E] escutar:  {led(escutando)}{surdez}   ({c_escutar} vezes)"),
            ((120, 200, 130) if movendo else (229, 72, 77),
             f"[M] mover:    {led(movendo)}   ({c_mover} vezes)"),
            ((120, 200, 130) if desenhando else (229, 72, 77),
             f"[D] desenhar: {led(desenhando)}   ({c_desenhar} vezes)"),
        ]
        for i, (cor, linha) in enumerate(linhas):
            tela.blit(fonte.render(linha, True, cor), (20, 16 + i * 28))

        ajuda = "E · M · D desligam cada parte — repare no que quebra"
        txt = fonte_p.render(ajuda, True, (159, 176, 208))
        tela.blit(txt, txt.get_rect(center=(400, 438)))

        pygame.display.flip()
    # (se não desenhamos, a tela congela no último quadro — mas olhe
    #  o contador de MOVER quando religar: o mundo nunca parou)

    relogio.tick(60)

pygame.quit()