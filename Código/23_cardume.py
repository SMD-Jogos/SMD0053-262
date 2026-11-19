"""Particionamento do espaço — Demo 1: o cardume.

Clique para tocar na água: os peixes perto do toque se assustam e fogem,
e cada peixe assustado assusta os vizinhos, num susto que se espalha.
Para assustar, cada peixe precisa descobrir quem está perto dele.

Teclas:
  clique  toca na água
  1 a 4   força bruta / grid / quadtree / k-d tree
  R       espalha os peixes de novo
  ESC     sai
"""

import math
import random

import pygame

LARGURA = 1280
ALTURA = 720
FPS_ALVO = 60
PASSO_FIXO = 1 / FPS_ALVO  # a simulação anda sempre o mesmo tanto por frame

QUANTIDADE = 3000
RAIO_PEIXE = 3
RAIO_VIZINHANCA = 25
RAIO_TOQUE = 80

FORCA_SUSTO = 400         # velocidade de fuga dada pelo toque (pixels por segundo)
PERDA_POR_CONTATO = 0.95  # cada peixe repassa 95% do susto que levou
SUSTO_MINIMO = 40         # abaixo disso o susto não passa adiante
ATRITO = 2.5              # quanto a velocidade cai por segundo

TAMANHO_CELULA = RAIO_VIZINHANCA
CAPACIDADE_QUADTREE = 16
PROFUNDIDADE_MAXIMA_QUADTREE = 8
TAMANHO_FOLHA_KD = 16

MODOS = ["força bruta", "grid", "quadtree", "k-d tree"]

COR_FUNDO = (250, 249, 246)
COR_TEXTO = (22, 21, 15)
COR_GRADE = (215, 211, 200)
COR_ARVORE = (160, 154, 138)
COR_CALMO = (125, 120, 106)
COR_ASSUSTADO = (140, 47, 30)


class Peixe:
    def __init__(self):
        self.x = random.uniform(0, LARGURA)
        self.y = random.uniform(0, ALTURA)
        self.vx = 0.0
        self.vy = 0.0
        self.susto_a_repassar = 0.0
        self.brilho = 0.0
        self.ultimo_toque = 0  # número do último toque que o assustou

    def fugir_de(self, origem_x, origem_y, forca, toque):
        dx = self.x - origem_x
        dy = self.y - origem_y
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            return
        self.vx += dx / distancia * forca
        self.vy += dy / distancia * forca
        self.susto_a_repassar = max(self.susto_a_repassar, forca * PERDA_POR_CONTATO)
        self.brilho = 1.0
        self.ultimo_toque = toque

    def mover(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        reducao = max(0.0, 1 - ATRITO * dt)
        self.vx *= reducao
        self.vy *= reducao
        self.brilho = max(0.0, self.brilho - dt)
        if self.x < 0 or self.x > LARGURA:
            self.vx = -self.vx
            self.x = min(max(self.x, 0), LARGURA)
        if self.y < 0 or self.y > ALTURA:
            self.vy = -self.vy
            self.y = min(max(self.y, 0), ALTURA)


def perto(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return dx * dx + dy * dy < RAIO_VIZINHANCA * RAIO_VIZINHANCA


# ---------- vizinhos: força bruta ----------

def vizinhos_forca_bruta(a, peixes, contador):
    encontrados = []
    for b in peixes:
        if a is b:
            continue
        contador[0] += 1
        if perto(a, b):
            encontrados.append(b)
    return encontrados


# ---------- vizinhos: grid ----------

def celula_de(x, y):
    return (int(x // TAMANHO_CELULA), int(y // TAMANHO_CELULA))


def montar_grid(peixes):
    grid = {}
    for b in peixes:
        celula = celula_de(b.x, b.y)
        if celula not in grid:
            grid[celula] = []
        grid[celula].append(b)
    return grid


def vizinhos_com_grid(a, grid, contador):
    coluna, linha = celula_de(a.x, a.y)
    encontrados = []
    for dc in (-1, 0, 1):
        for dl in (-1, 0, 1):
            for b in grid.get((coluna + dc, linha + dl), []):
                if a is b:
                    continue
                contador[0] += 1
                if perto(a, b):
                    encontrados.append(b)
    return encontrados


# ---------- vizinhos: quadtree ----------

class NoQuadtree:
    def __init__(self, x, y, largura, altura, profundidade):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura
        self.profundidade = profundidade
        self.peixes = []
        self.filhos = []

    def contem(self, b):
        return self.x <= b.x < self.x + self.largura and self.y <= b.y < self.y + self.altura

    def inserir(self, b):
        if not self.contem(b):
            return False
        if self.filhos:
            for filho in self.filhos:
                if filho.inserir(b):
                    return True
            return False
        self.peixes.append(b)
        if len(self.peixes) > CAPACIDADE_QUADTREE and self.profundidade < PROFUNDIDADE_MAXIMA_QUADTREE:
            self.dividir()
        return True

    def dividir(self):
        meia_l = self.largura / 2
        meia_a = self.altura / 2
        p = self.profundidade + 1
        self.filhos = [
            NoQuadtree(self.x, self.y, meia_l, meia_a, p),
            NoQuadtree(self.x + meia_l, self.y, meia_l, meia_a, p),
            NoQuadtree(self.x, self.y + meia_a, meia_l, meia_a, p),
            NoQuadtree(self.x + meia_l, self.y + meia_a, meia_l, meia_a, p),
        ]
        antigos = self.peixes
        self.peixes = []
        for b in antigos:
            for filho in self.filhos:
                if filho.inserir(b):
                    break

    def buscar(self, a, encontrados, contador):
        # pula o nó inteiro se o quadrado de busca em volta de a não encosta nele
        if (a.x + RAIO_VIZINHANCA < self.x or a.x - RAIO_VIZINHANCA > self.x + self.largura or
                a.y + RAIO_VIZINHANCA < self.y or a.y - RAIO_VIZINHANCA > self.y + self.altura):
            return
        for b in self.peixes:
            if a is b:
                continue
            contador[0] += 1
            if perto(a, b):
                encontrados.append(b)
        for filho in self.filhos:
            filho.buscar(a, encontrados, contador)

    def desenhar(self, tela):
        if not self.filhos:
            return
        meio_x = self.x + self.largura / 2
        meio_y = self.y + self.altura / 2
        pygame.draw.line(tela, COR_ARVORE, (meio_x, self.y), (meio_x, self.y + self.altura))
        pygame.draw.line(tela, COR_ARVORE, (self.x, meio_y), (self.x + self.largura, meio_y))
        for filho in self.filhos:
            filho.desenhar(tela)


def montar_quadtree(peixes):
    # um pouco maior que a tela, para incluir peixes encostados na borda
    raiz = NoQuadtree(-1, -1, LARGURA + 2, ALTURA + 2, 0)
    for b in peixes:
        raiz.inserir(b)
    return raiz


# ---------- vizinhos: k-d tree ----------

class NoKd:
    def __init__(self, peixes, profundidade):
        self.peixes = []
        self.esquerda = None
        self.direita = None
        self.eixo_x = profundidade % 2 == 0  # alterna: x, y, x, y...
        if len(peixes) <= TAMANHO_FOLHA_KD:
            self.peixes = peixes
            return
        if self.eixo_x:
            ordenados = sorted(peixes, key=lambda b: b.x)
        else:
            ordenados = sorted(peixes, key=lambda b: b.y)
        meio = len(ordenados) // 2
        antes, depois = ordenados[meio - 1], ordenados[meio]
        # o corte fica entre os dois do meio: metade dos peixes de cada lado
        if self.eixo_x:
            self.corte = (antes.x + depois.x) / 2
        else:
            self.corte = (antes.y + depois.y) / 2
        self.esquerda = NoKd(ordenados[:meio], profundidade + 1)
        self.direita = NoKd(ordenados[meio:], profundidade + 1)

    def buscar(self, a, encontrados, contador):
        if self.esquerda is None:
            for b in self.peixes:
                if a is b:
                    continue
                contador[0] += 1
                if perto(a, b):
                    encontrados.append(b)
            return
        posicao = a.x if self.eixo_x else a.y
        if posicao - RAIO_VIZINHANCA <= self.corte:
            self.esquerda.buscar(a, encontrados, contador)
        if posicao + RAIO_VIZINHANCA >= self.corte:
            self.direita.buscar(a, encontrados, contador)

    def desenhar(self, tela, esquerda, topo, direita, base):
        if self.esquerda is None:
            return
        if self.eixo_x:
            pygame.draw.line(tela, COR_ARVORE, (self.corte, topo), (self.corte, base))
            self.esquerda.desenhar(tela, esquerda, topo, self.corte, base)
            self.direita.desenhar(tela, self.corte, topo, direita, base)
        else:
            pygame.draw.line(tela, COR_ARVORE, (esquerda, self.corte), (direita, self.corte))
            self.esquerda.desenhar(tela, esquerda, topo, direita, self.corte)
            self.direita.desenhar(tela, esquerda, self.corte, direita, base)


# ---------- toque e susto ----------

def tocar_na_agua(x, y, peixes, toque):
    for b in peixes:
        if math.hypot(b.x - x, b.y - y) < RAIO_TOQUE:
            b.fugir_de(x, y, FORCA_SUSTO, toque)


def montar_estrutura(peixes, modo):
    """Refeita a cada frame, porque os peixes se movem."""
    if modo == "grid":
        return montar_grid(peixes)
    if modo == "quadtree":
        return montar_quadtree(peixes)
    if modo == "k-d tree":
        return NoKd(peixes, 0)
    return None


def propagar_susto(peixes, modo, estrutura, toque):
    """Cada peixe assustado assusta os vizinhos uma vez. Devolve testes e ativos."""
    contador = [0]
    ativos = [b for b in peixes if b.susto_a_repassar > SUSTO_MINIMO]
    for a in ativos:
        if modo == "força bruta":
            vizinhos = vizinhos_forca_bruta(a, peixes, contador)
        elif modo == "grid":
            vizinhos = vizinhos_com_grid(a, estrutura, contador)
        else:
            vizinhos = []
            estrutura.buscar(a, vizinhos, contador)
        forca = a.susto_a_repassar
        a.susto_a_repassar = 0.0
        for b in vizinhos:
            if b.ultimo_toque != toque:  # cada peixe se assusta uma vez por toque
                b.fugir_de(a.x, a.y, forca, toque)
    return contador[0], len(ativos)


# ---------- tela ----------

def desenhar_grade(tela):
    for x in range(0, LARGURA, TAMANHO_CELULA):
        pygame.draw.line(tela, COR_GRADE, (x, 0), (x, ALTURA))
    for y in range(0, ALTURA, TAMANHO_CELULA):
        pygame.draw.line(tela, COR_GRADE, (0, y), (LARGURA, y))


def misturar(cor_a, cor_b, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(cor_a, cor_b))


def desenhar_painel(tela, fonte, linhas):
    y = 12
    for texto in linhas:
        imagem = fonte.render(texto, True, COR_TEXTO, COR_FUNDO)
        tela.blit(imagem, (12, y))
        y += imagem.get_height() + 4


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Particionamento do espaço — cardume")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("monospace", 22, bold=True)

    peixes = [Peixe() for _ in range(QUANTIDADE)]
    modo = MODOS[0]
    pior_fps = FPS_ALVO
    toque = 0

    rodando = True
    while rodando:
        relogio.tick(FPS_ALVO)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                toque += 1
                tocar_na_agua(evento.pos[0], evento.pos[1], peixes, toque)
                pior_fps = FPS_ALVO
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False
                elif evento.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    modo = MODOS[evento.key - pygame.K_1]
                elif evento.key == pygame.K_r:
                    peixes = [Peixe() for _ in range(QUANTIDADE)]

        estrutura = montar_estrutura(peixes, modo)
        testes, ativos = propagar_susto(peixes, modo, estrutura, toque)
        for b in peixes:
            b.mover(PASSO_FIXO)

        fps = relogio.get_fps()
        if ativos > 0 and fps > 0:
            pior_fps = min(pior_fps, fps)

        tela.fill(COR_FUNDO)
        if modo == "grid":
            desenhar_grade(tela)
        elif modo == "quadtree":
            estrutura.desenhar(tela)
        elif modo == "k-d tree":
            estrutura.desenhar(tela, 0, 0, LARGURA, ALTURA)
        for b in peixes:
            cor = misturar(COR_CALMO, COR_ASSUSTADO, b.brilho)
            pygame.draw.circle(tela, cor, (int(b.x), int(b.y)), RAIO_PEIXE)

        desenhar_painel(tela, fonte, [
            f"FPS: {fps:.0f}   pior FPS do último toque: {pior_fps:.0f}",
            f"peixes: {len(peixes)}   assustando agora: {ativos}",
            f"testes por frame: {testes:,}".replace(",", "."),
            f"modo: {modo}   (1 a 4 troca)",
        ])
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()