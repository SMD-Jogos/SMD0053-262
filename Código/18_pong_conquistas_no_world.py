import pygame
import random
from abc import ABC, abstractmethod

LARGURA = 800
ALTURA = 600
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

PASSO = 1 / 60
ATRASO_MAXIMO = 0.25

LARGURA_RAQUETE = 15
ALTURA_RAQUETE = 100
DIAMETRO_BOLA = 20
VELOCIDADE_BOLA = 300
# Na Aula 17 o oponente andava a 300 e nunca errava; a 265 ele erra de vez em quando.
VELOCIDADE_OPONENTE = 205

COR_RUIM = (235, 100, 80)
DURACAO_AVISO = 2.0

REBATIDAS_NO_RALLY = 10
PONTOS_SEGUIDOS = 3


# ---------------------------------------------------------------------------
# A entidade: so um conteiner de dados e de componentes.
# Nao existe mais Bola, Raquete, RaqueteDoJogador nem RaqueteDoOponente.
# ---------------------------------------------------------------------------

class Entidade:
    def __init__(self, x, y, largura, altura, controle, fisica, grafico):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.largura = largura
        self.altura = altura

        self.controle = controle
        self.fisica = fisica
        self.grafico = grafico

    def update(self, dt):
        if self.controle is not None:
            self.controle.update(self, dt)
        if self.fisica is not None:
            self.fisica.update(self, dt)

    def desenhar(self, tela):
        if self.grafico is not None:
            self.grafico.desenhar(self, tela)

    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


# ---------------------------------------------------------------------------
# Controle: quem decide para onde a entidade quer ir.
# ---------------------------------------------------------------------------

class Controle(ABC):
    @abstractmethod
    def update(self, entidade, dt):
        ...


class ControleTeclado(Controle):
    def __init__(self, tecla_cima, tecla_baixo, velocidade):
        self.tecla_cima = tecla_cima
        self.tecla_baixo = tecla_baixo
        self.velocidade = velocidade

    def update(self, entidade, dt):
        teclas = pygame.key.get_pressed()
        entidade.vy = 0

        if teclas[self.tecla_cima]:
            entidade.vy = -self.velocidade
        if teclas[self.tecla_baixo]:
            entidade.vy = self.velocidade


class ControleSeguidor(Controle):
    """Segue a altura de outra entidade (o oponente segue a bola)."""

    def __init__(self, alvo, velocidade):
        self.alvo = alvo
        self.velocidade = velocidade

    def update(self, entidade, dt):
        centro = entidade.y + entidade.altura / 2
        centro_alvo = self.alvo.y + self.alvo.altura / 2
        entidade.vy = 0

        if centro < centro_alvo:
            entidade.vy = self.velocidade
        if centro > centro_alvo:
            entidade.vy = -self.velocidade


# ---------------------------------------------------------------------------
# Fisica: como a entidade se move e reage aos limites da tela.
# ---------------------------------------------------------------------------

class Fisica(ABC):
    @abstractmethod
    def update(self, entidade, dt):
        ...


class FisicaRaquete(Fisica):
    def update(self, entidade, dt):
        entidade.y += entidade.vy * dt

        if entidade.y < 0:
            entidade.y = 0
        if entidade.y > ALTURA - entidade.altura:
            entidade.y = ALTURA - entidade.altura


class FisicaBola(Fisica):
    def update(self, entidade, dt):
        entidade.x += entidade.vx * dt
        entidade.y += entidade.vy * dt

        if entidade.y < 0 or entidade.y + entidade.altura > ALTURA:
            entidade.vy = -entidade.vy


# ---------------------------------------------------------------------------
# Grafico: como a entidade aparece na tela.
# ---------------------------------------------------------------------------

class Grafico(ABC):
    @abstractmethod
    def desenhar(self, entidade, tela):
        ...


class GraficoRetangulo(Grafico):
    def desenhar(self, entidade, tela):
        pygame.draw.rect(tela, BRANCO, entidade.rect())


class GraficoCirculo(Grafico):
    def desenhar(self, entidade, tela):
        raio = entidade.largura // 2
        centro = (int(entidade.x + raio), int(entidade.y + raio))
        pygame.draw.circle(tela, BRANCO, centro, raio)


# ---------------------------------------------------------------------------
# Avisos: faixas de texto que aparecem por alguns segundos.
# ---------------------------------------------------------------------------

class Aviso:
    def __init__(self, texto, cor):
        self.texto = texto
        self.cor = cor
        self.tempo = DURACAO_AVISO


class Avisos:
    def __init__(self):
        self.fonte = pygame.font.Font(None, 48)
        self.ativos = []

    def mostrar(self, texto, ruim=False):
        cor = BRANCO
        if ruim:
            cor = COR_RUIM
        self.ativos.append(Aviso(texto, cor))

    def update(self, dt):
        for aviso in self.ativos:
            aviso.tempo -= dt
        self.ativos = [aviso for aviso in self.ativos if aviso.tempo > 0]

    def desenhar(self, tela):
        y = ALTURA - 100
        for aviso in self.ativos:
            imagem = self.fonte.render(aviso.texto, True, aviso.cor)
            caixa = imagem.get_rect(center=(LARGURA / 2, y))
            pygame.draw.rect(tela, PRETO, caixa.inflate(24, 12))
            tela.blit(imagem, caixa)
            y -= 50


# ---------------------------------------------------------------------------
# O resto do jogo e o mesmo da Aula 17, mais as conquistas.
# ---------------------------------------------------------------------------

class Placar:
    def __init__(self):
        self.jogador = 0
        self.oponente = 0
        self.fonte = pygame.font.Font(None, 74)

    def desenhar(self, tela):
        # cada número do seu lado da rede, a 40 px dela
        esquerdo = self.fonte.render(str(self.jogador), True, BRANCO)
        direito = self.fonte.render(str(self.oponente), True, BRANCO)
        tela.blit(esquerdo, esquerdo.get_rect(topright=(LARGURA / 2 - 40, 20)))
        tela.blit(direito, direito.get_rect(topleft=(LARGURA / 2 + 40, 20)))


class World:
    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Pong: conquistas dentro do World")
        self.clock = pygame.time.Clock()

        # Bola: sem controle, so fisica e grafico.
        self.bola = Entidade(390, 290, DIAMETRO_BOLA, DIAMETRO_BOLA,
                             controle=None,
                             fisica=FisicaBola(),
                             grafico=GraficoCirculo())
        self.reiniciar_bola()   # começa na diagonal, como depois de um ponto

        # As duas raquetes sao a MESMA classe. So o controle muda.
        self.jogador = Entidade(30, 250, LARGURA_RAQUETE, ALTURA_RAQUETE,
                                controle=ControleTeclado(pygame.K_UP, pygame.K_DOWN, 420),
                                fisica=FisicaRaquete(),
                                grafico=GraficoRetangulo())

        self.oponente = Entidade(755, 250, LARGURA_RAQUETE, ALTURA_RAQUETE,
                                 controle=ControleSeguidor(self.bola, VELOCIDADE_OPONENTE),
                                 fisica=FisicaRaquete(),
                                 grafico=GraficoRetangulo())

        self.entidades = [self.jogador, self.oponente, self.bola]

        self.placar = Placar()
        self.avisos = Avisos()

        # Estado das conquistas: tudo guardado no World.
        self.rally = 0
        self.pontos_seguidos_jogador = 0
        self.pontos_seguidos_oponente = 0

        self.rodando = True

    def reiniciar_bola(self):
        self.bola.x = 390
        self.bola.y = 290
        self.bola.vx = VELOCIDADE_BOLA * random.choice([1, -1])
        self.bola.vy = VELOCIDADE_BOLA * random.choice([1, -1])

    def inputs(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False

    def update(self, dt):
        for entidade in self.entidades:
            entidade.update(dt)

        self.colisoes()
        self.avisos.update(dt)

    def colisoes(self):
        bola_rect = self.bola.rect()

        # Raquete esquerda sempre manda a bola para a direita, e vice-versa.
        # So conta como rebatida se a bola vinha na direcao da raquete.
        if bola_rect.colliderect(self.jogador.rect()) and self.bola.vx < 0:
            self.bola.vx = abs(self.bola.vx)
            # conquista: rally
            self.rally += 1
            if self.rally == REBATIDAS_NO_RALLY:
                self.avisos.mostrar(f"Rally de {REBATIDAS_NO_RALLY} rebatidas!")
        if bola_rect.colliderect(self.oponente.rect()) and self.bola.vx > 0:
            self.bola.vx = -abs(self.bola.vx)
            # conquista: rally
            self.rally += 1
            if self.rally == REBATIDAS_NO_RALLY:
                self.avisos.mostrar(f"Rally de {REBATIDAS_NO_RALLY} rebatidas!")

        if self.bola.x < 0:
            self.placar.oponente += 1
            # conquista: rally (zera)
            self.rally = 0
            # conquista: hat-trick (zera)
            self.pontos_seguidos_jogador = 0
            # conquista: levar 3 seguidos
            self.pontos_seguidos_oponente += 1
            if self.pontos_seguidos_oponente == PONTOS_SEGUIDOS:
                self.avisos.mostrar("Levou 3 seguidos", ruim=True)
            self.reiniciar_bola()
        if self.bola.x > LARGURA:
            self.placar.jogador += 1
            # conquista: rally (zera)
            self.rally = 0
            # conquista: hat-trick
            self.pontos_seguidos_jogador += 1
            if self.pontos_seguidos_jogador == PONTOS_SEGUIDOS:
                self.avisos.mostrar("Hat-trick!")
            # conquista: levar 3 seguidos (zera)
            self.pontos_seguidos_oponente = 0
            self.reiniciar_bola()

    def desenhar(self):
        self.tela.fill(PRETO)

        for entidade in self.entidades:
            entidade.desenhar(self.tela)

        pygame.draw.aaline(self.tela, BRANCO, (LARGURA / 2, 0), (LARGURA / 2, ALTURA))
        self.placar.desenhar(self.tela)
        self.avisos.desenhar(self.tela)

        pygame.display.flip()

    def game_loop(self):
        acumulador = 0

        while self.rodando:
            acumulador += min(self.clock.tick(240) / 1000, ATRASO_MAXIMO)
            self.inputs()

            while acumulador >= PASSO:
                self.update(PASSO)
                acumulador -= PASSO

            self.desenhar()


pygame.init()
mundo = World()
mundo.game_loop()
pygame.quit()
