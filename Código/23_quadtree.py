"""Particionamento do espaço — Demo 4: quadtree visível.

A quadtree é refeita a cada frame. Um nó com mais de CAPACIDADE
bolinhas se divide em quatro quadrantes iguais, até a profundidade máxima.
No limite de profundidade a célula não divide mais e fica destacada.

Teclas:
  + / -   mais ou menos bolinhas (de 10 em 10)
  C       espalha / aglomera as bolinhas num canto
  [ / ]   diminui / aumenta a profundidade máxima
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

CAPACIDADE = 4
PROFUNDIDADE_INICIAL = 6  # célula mais funda: 20 x 11 px
PROFUNDIDADE_LIMITE = 9
AREA_AGLOMERADA = pygame.Rect(60, 180, 240, 160)

COR_FUNDO = (250, 249, 246)
COR_TEXTO = (22, 21, 15)
COR_DIVISAO = (125, 120, 106)
COR_BOLINHA = (140, 47, 30)
COR_LOTADA = (235, 216, 210)  # folha no limite de profundidade com mais que a capacidade


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


class NoQuadtree:
    def __init__(self, retangulo, profundidade, profundidade_maxima):
        self.retangulo = retangulo
        self.profundidade = profundidade
        self.profundidade_maxima = profundidade_maxima
        self.bolinhas = []
        self.filhos = []

    def inserir(self, bolinha):
        if not self.retangulo.collidepoint(bolinha.x, bolinha.y):
            return False
        if self.filhos:
            for filho in self.filhos:
                if filho.inserir(bolinha):
                    return True
            return False
        self.bolinhas.append(bolinha)
        if len(self.bolinhas) > CAPACIDADE and self.profundidade < self.profundidade_maxima:
            self.dividir()
        return True

    def dividir(self):
        r = self.retangulo
        meia_largura = r.width // 2
        meia_altura = r.height // 2
        self.filhos = [
            NoQuadtree(pygame.Rect(r.left, r.top, meia_largura, meia_altura), self.profundidade + 1, self.profundidade_maxima),
            NoQuadtree(pygame.Rect(r.left + meia_largura, r.top, r.width - meia_largura, meia_altura), self.profundidade + 1, self.profundidade_maxima),
            NoQuadtree(pygame.Rect(r.left, r.top + meia_altura, meia_largura, r.height - meia_altura), self.profundidade + 1, self.profundidade_maxima),
            NoQuadtree(pygame.Rect(r.left + meia_largura, r.top + meia_altura, r.width - meia_largura, r.height - meia_altura), self.profundidade + 1, self.profundidade_maxima),
        ]
        bolinhas_antigas = self.bolinhas
        self.bolinhas = []
        for b in bolinhas_antigas:
            for filho in self.filhos:
                if filho.inserir(b):
                    break

    def contar_nos(self):
        total = 1
        for filho in self.filhos:
            total += filho.contar_nos()
        return total

    def desenhar(self, tela):
        if len(self.bolinhas) > CAPACIDADE:
            pygame.draw.rect(tela, COR_LOTADA, self.retangulo)
        pygame.draw.rect(tela, COR_DIVISAO, self.retangulo, 1)
        for filho in self.filhos:
            filho.desenhar(tela)


def criar_bolinhas(quantidade, area):
    return [Bolinha(area) for _ in range(quantidade)]


def desenhar_painel(tela, fonte, texto):
    pygame.draw.rect(tela, COR_FUNDO, (0, 0, LARGURA, ALTURA_PAINEL))
    imagem = fonte.render(texto, True, COR_TEXTO)
    tela.blit(imagem, (12, (ALTURA_PAINEL - imagem.get_height()) // 2))


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Particionamento do espaço — quadtree")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("monospace", 22, bold=True)

    area_livre = pygame.Rect(0, ALTURA_PAINEL, LARGURA, ALTURA - ALTURA_PAINEL)
    area = area_livre
    bolinhas = criar_bolinhas(QUANTIDADE_INICIAL, area)
    pausado = False
    profundidade_maxima = PROFUNDIDADE_INICIAL

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
                    profundidade_maxima = max(1, profundidade_maxima - 1)
                elif evento.key == pygame.K_RIGHTBRACKET:
                    profundidade_maxima = min(PROFUNDIDADE_LIMITE, profundidade_maxima + 1)
                elif evento.key == pygame.K_c:
                    if area is area_livre:
                        area = AREA_AGLOMERADA
                    else:
                        area = area_livre
                    bolinhas = criar_bolinhas(len(bolinhas), area)

        if not pausado:
            for b in bolinhas:
                b.mover(PASSO_FIXO, area)

        raiz = NoQuadtree(area_livre.copy(), 0, profundidade_maxima)
        for b in bolinhas:
            raiz.inserir(b)

        tela.fill(COR_FUNDO)
        raiz.desenhar(tela)
        for b in bolinhas:
            pygame.draw.circle(tela, COR_BOLINHA, (int(b.x), int(b.y)), RAIO_BOLINHA)

        desenhar_painel(tela, fonte,
            f"FPS {relogio.get_fps():.0f}   bolinhas {len(bolinhas)}   nós {raiz.contar_nos()}"
            f"   capacidade {CAPACIDADE}   profundidade máxima {profundidade_maxima}")
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()