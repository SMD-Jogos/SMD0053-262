"""Particionamento do espaço — Demos 2 e 3: força bruta x grid.

Cada bolinha procura as vizinhas dentro de RAIO_VIZINHANCA.
Bolinha com vizinha fica vermelha; sem vizinha, cinza.

Teclas:
  + / -   mais ou menos bolinhas (de 100 em 100)
  G       alterna força bruta / grid
  [ / ]   diminui / aumenta o tamanho da célula do grid
  C       espalha / aglomera as bolinhas num canto
  ESC     sai
"""

import math
import random

import pygame

LARGURA = 1280
ALTURA = 720
FPS_ALVO = 60
PASSO_FIXO = 1 / FPS_ALVO  # a simulação anda sempre o mesmo tanto por frame

RAIO_BOLINHA = 4
RAIO_VIZINHANCA = 20
VELOCIDADE_MAXIMA = 60  # pixels por segundo

QUANTIDADE_INICIAL = 300
PASSO_QUANTIDADE = 100

TAMANHO_CELULA_INICIAL = 40
TAMANHO_CELULA_MINIMO = 10
TAMANHO_CELULA_MAXIMO = 640
AREA_AGLOMERADA = pygame.Rect(60, 180, 240, 160)

COR_FUNDO = (250, 249, 246)
COR_TEXTO = (22, 21, 15)
COR_GRADE = (215, 211, 200)
COR_SOZINHA = (125, 120, 106)
COR_COM_VIZINHA = (140, 47, 30)


class Bolinha:
    def __init__(self, area):
        self.x = random.uniform(area.left, area.right)
        self.y = random.uniform(area.top, area.bottom)
        self.vx = random.uniform(-VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA)
        self.vy = random.uniform(-VELOCIDADE_MAXIMA, VELOCIDADE_MAXIMA)
        self.tem_vizinha = False

    def mover(self, dt, area):
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x < area.left or self.x > area.right:
            self.vx = -self.vx
            self.x = min(max(self.x, area.left), area.right)
        if self.y < area.top or self.y > area.bottom:
            self.vy = -self.vy
            self.y = min(max(self.y, area.top), area.bottom)


def perto(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return dx * dx + dy * dy < RAIO_VIZINHANCA * RAIO_VIZINHANCA


# ---------- força bruta ----------

def buscar_forca_bruta(bolinhas):
    testes = 0
    for a in bolinhas:
        for b in bolinhas:
            if a is b:
                continue
            testes += 1
            if perto(a, b):
                a.tem_vizinha = True
    return testes


# ---------- grid ----------

def celula_de(x, y, tamanho_celula):
    coluna = int(x // tamanho_celula)
    linha = int(y // tamanho_celula)
    return (coluna, linha)


def montar_grid(bolinhas, tamanho_celula):
    grid = {}
    for b in bolinhas:
        celula = celula_de(b.x, b.y, tamanho_celula)
        if celula not in grid:
            grid[celula] = []
        grid[celula].append(b)
    return grid


def buscar_com_grid(bolinhas, tamanho_celula):
    grid = montar_grid(bolinhas, tamanho_celula)
    # quantas células para cada lado cobrem o raio de busca
    alcance = math.ceil(RAIO_VIZINHANCA / tamanho_celula)
    testes = 0
    for a in bolinhas:
        coluna, linha = celula_de(a.x, a.y, tamanho_celula)
        for dc in range(-alcance, alcance + 1):
            for dl in range(-alcance, alcance + 1):
                vizinhas = grid.get((coluna + dc, linha + dl), [])
                for b in vizinhas:
                    if a is b:
                        continue
                    testes += 1
                    if perto(a, b):
                        a.tem_vizinha = True
    return testes


# ---------- tela ----------

def desenhar_grade(tela, tamanho_celula):
    for x in range(0, LARGURA, tamanho_celula):
        pygame.draw.line(tela, COR_GRADE, (x, 0), (x, ALTURA))
    for y in range(0, ALTURA, tamanho_celula):
        pygame.draw.line(tela, COR_GRADE, (0, y), (LARGURA, y))


def desenhar_painel(tela, fonte, linhas):
    y = 12
    for texto in linhas:
        imagem = fonte.render(texto, True, COR_TEXTO, COR_FUNDO)
        tela.blit(imagem, (12, y))
        y += imagem.get_height() + 4


def criar_bolinhas(quantidade, area):
    return [Bolinha(area) for _ in range(quantidade)]


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Particionamento do espaço — força bruta x grid")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("monospace", 22, bold=True)

    area_livre = pygame.Rect(0, 0, LARGURA, ALTURA)
    area = area_livre
    bolinhas = criar_bolinhas(QUANTIDADE_INICIAL, area)
    usar_grid = False
    tamanho_celula = TAMANHO_CELULA_INICIAL

    rodando = True
    while rodando:
        relogio.tick(FPS_ALVO)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    bolinhas += criar_bolinhas(PASSO_QUANTIDADE, area)
                elif evento.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    bolinhas = bolinhas[:max(PASSO_QUANTIDADE, len(bolinhas) - PASSO_QUANTIDADE)]
                elif evento.key == pygame.K_g:
                    usar_grid = not usar_grid
                elif evento.key == pygame.K_LEFTBRACKET:
                    tamanho_celula = max(TAMANHO_CELULA_MINIMO, tamanho_celula // 2)
                elif evento.key == pygame.K_RIGHTBRACKET:
                    tamanho_celula = min(TAMANHO_CELULA_MAXIMO, tamanho_celula * 2)
                elif evento.key == pygame.K_c:
                    if area is area_livre:
                        area = AREA_AGLOMERADA
                    else:
                        area = area_livre
                    bolinhas = criar_bolinhas(len(bolinhas), area)

        for b in bolinhas:
            b.mover(PASSO_FIXO, area)
            b.tem_vizinha = False

        if usar_grid:
            testes = buscar_com_grid(bolinhas, tamanho_celula)
        else:
            testes = buscar_forca_bruta(bolinhas)

        tela.fill(COR_FUNDO)
        if usar_grid:
            desenhar_grade(tela, tamanho_celula)
        for b in bolinhas:
            cor = COR_COM_VIZINHA if b.tem_vizinha else COR_SOZINHA
            pygame.draw.circle(tela, cor, (int(b.x), int(b.y)), RAIO_BOLINHA)

        modo = f"grid (célula {tamanho_celula} px)" if usar_grid else "força bruta"
        desenhar_painel(tela, fonte, [
            f"FPS: {relogio.get_fps():.0f}",
            f"bolinhas: {len(bolinhas)}",
            f"testes por frame: {testes:,}".replace(",", "."),
            f"modo: {modo}",
        ])
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()