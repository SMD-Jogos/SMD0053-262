"""Particionamento do espaço — Demo 5: k-d tree visível.

A k-d tree é refeita a cada frame. Cada nó ordena as suas bolinhas
pelo eixo da vez (x, y, x, y...) e corta entre as duas do meio,
deixando metade de cada lado. Para quando sobram TAMANHO_FOLHA ou menos.

Teclas:
  + / -   mais ou menos bolinhas (de 10 em 10)
  C       espalha / aglomera as bolinhas num canto
  [ / ]   diminui / aumenta o tamanho da folha
  ESPAÇO  pausa
  ESC     sai
"""

import random

import pygame

LARGURA = 1280
ALTURA = 720
FPS_ALVO = 60
ALTURA_PAINEL = 40  # faixa de texto no topo, fora da área da simulação
PASSO_FIXO = 1 / FPS_ALVO  # a simulação anda sempre o mesmo tanto por frame

RAIO_BOLINHA = 4
VELOCIDADE_MAXIMA = 60  # pixels por segundo
QUANTIDADE_INICIAL = 12
PASSO_QUANTIDADE = 100

TAMANHO_FOLHA_INICIAL = 2
TAMANHO_FOLHA_MAXIMO = 16
AREA_AGLOMERADA = pygame.Rect(60, 180, 240, 160)

COR_FUNDO = (250, 249, 246)
COR_TEXTO = (22, 21, 15)
COR_CORTE_X = (125, 120, 106)    # cortes verticais
COR_CORTE_Y = (190, 150, 140)    # cortes horizontais
COR_BOLINHA = (140, 47, 30)


class Bolinha:
    def __init__(self, area):
        self.x = random.uniform(area.left, area.right)
        self.y = random.uniform(area.top, area.bottom)
        self.vx = random.uniform(-VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA)
        self.vy = random.uniform(-VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA)

    def mover(self, dt, area):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < area.left or self.x > area.right:
            self.vx = -self.vx
            self.x = min(max(self.x, area.left), area.right)
        if self.y < area.top or self.y > area.bottom:
            self.vy = -self.vy
            self.y = min(max(self.y, area.top), area.bottom)


class NoKd:
    def __init__(self, bolinhas, nivel, tamanho_folha):
        self.bolinhas = []
        self.esquerda = None
        self.direita = None
        self.eixo_x = nivel % 2 == 0  # alterna: x, y, x, y...
        if len(bolinhas) <= tamanho_folha:
            self.bolinhas = bolinhas
            return
        if self.eixo_x:
            ordenadas = sorted(bolinhas, key=lambda b: b.x)
        else:
            ordenadas = sorted(bolinhas, key=lambda b: b.y)
        meio = len(ordenadas) // 2
        antes, depois = ordenadas[meio - 1], ordenadas[meio]
        # o corte fica entre as duas do meio: metade das bolinhas de cada lado
        if self.eixo_x:
            self.corte = (antes.x + depois.x) / 2
        else:
            self.corte = (antes.y + depois.y) / 2
        self.esquerda = NoKd(ordenadas[:meio], nivel + 1, tamanho_folha)
        self.direita = NoKd(ordenadas[meio:], nivel + 1, tamanho_folha)

    def contar_nos(self):
        if self.esquerda is None:
            return 1
        return 1 + self.esquerda.contar_nos() + self.direita.contar_nos()

    def desenhar(self, tela, esquerda, topo, direita, base):
        if self.esquerda is None:
            return
        if self.eixo_x:
            pygame.draw.line(tela, COR_CORTE_X, (self.corte, topo), (self.corte, base), 2)
            self.esquerda.desenhar(tela, esquerda, topo, self.corte, base)
            self.direita.desenhar(tela, self.corte, topo, direita, base)
        else:
            pygame.draw.line(tela, COR_CORTE_Y, (esquerda, self.corte), (direita, self.corte), 2)
            self.esquerda.desenhar(tela, esquerda, topo, direita, self.corte)
            self.direita.desenhar(tela, esquerda, self.corte, direita, base)


def criar_bolinhas(quantidade, area):
    return [Bolinha(area) for _ in range(quantidade)]


def desenhar_painel(tela, fonte, texto):
    pygame.draw.rect(tela, COR_FUNDO, (0, 0, LARGURA, ALTURA_PAINEL))
    imagem = fonte.render(texto, True, COR_TEXTO)
    tela.blit(imagem, (12, (ALTURA_PAINEL - imagem.get_height()) // 2))


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Particionamento do espaço — k-d tree")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("monospace", 22, bold=True)

    area_livre = pygame.Rect(0, ALTURA_PAINEL, LARGURA, ALTURA - ALTURA_PAINEL)
    area = area_livre
    bolinhas = criar_bolinhas(QUANTIDADE_INICIAL, area)
    pausado = False
    tamanho_folha = TAMANHO_FOLHA_INICIAL

    rodando = True
    while rodando:
        relogio.tick(FPS_ALVO)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key == pygame.K_SPACE:
                    pausado = not pausado
                elif evento.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    bolinhas += criar_bolinhas(PASSO_QUANTIDADE, area)
                elif evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    bolinhas = bolinhas[:max(PASSO_QUANTIDADE, len(bolinhas) - PASSO_QUANTIDADE)]
                elif evento.key == pygame.K_LEFTBRACKET:
                    tamanho_folha = max(1, tamanho_folha - 1)
                elif evento.key == pygame.K_RIGHTBRACKET:
                    tamanho_folha = min(TAMANHO_FOLHA_MAXIMO, tamanho_folha + 1)
                elif evento.key == pygame.K_c:
                    if area is area_livre:
                        area = AREA_AGLOMERADA
                    else:
                        area = area_livre
                    bolinhas = criar_bolinhas(len(bolinhas), area)

        if not pausado:
            for b in bolinhas:
                b.mover(PASSO_FIXO, area)

        raiz = NoKd(bolinhas, 0, tamanho_folha)

        tela.fill(COR_FUNDO)
        raiz.desenhar(tela, area_livre.left, area_livre.top, area_livre.right, area_livre.bottom)
        for b in bolinhas:
            pygame.draw.circle(tela, COR_BOLINHA, (int(b.x), int(b.y)), RAIO_BOLINHA)

        desenhar_painel(tela, fonte,
            f"FPS {relogio.get_fps():.0f}   bolinhas {len(bolinhas)}   nós {raiz.contar_nos()}"
            f"   tamanho da folha {tamanho_folha}")
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
