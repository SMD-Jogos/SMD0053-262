import pygame
import random
from abc import ABC, abstractmethod

LARGURA = 800
ALTURA = 600
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

PASSO = 1 / 60
ATRASO_MAXIMO = 0.25


class Entidade(ABC):
    """O contrato: toda entidade do jogo se atualiza e se desenha."""

    @abstractmethod
    def update(self, dt):
        ...

    @abstractmethod
    def desenhar(self, tela):
        ...


class Bola(Entidade):
    RAIO = 10
    VELOCIDADE = 300

    def __init__(self):
        self.x = 400
        self.y = 300
        self.vx = self.VELOCIDADE
        self.vy = 0

    def reiniciar(self):
        self.x = 400
        self.y = 300
        self.vx = self.VELOCIDADE * random.choice([1, -1])
        self.vy = self.VELOCIDADE * random.choice([1, -1])

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.y - self.RAIO < 0 or self.y + self.RAIO > ALTURA:
            self.vy = -self.vy

    def rect(self):
        return pygame.Rect(self.x - self.RAIO, self.y - self.RAIO,
                           self.RAIO * 2, self.RAIO * 2)

    def desenhar(self, tela):
        pygame.draw.circle(tela, BRANCO, (int(self.x), int(self.y)), self.RAIO)


class Raquete(Entidade):
    """O que toda raquete tem e faz. Quem decide o movimento sao as filhas."""

    LARGURA = 15
    ALTURA = 100

    def __init__(self, x):
        self.x = x
        self.y = 250

    def limitar_na_tela(self):
        if self.y < 0:
            self.y = 0
        if self.y > ALTURA - self.ALTURA:
            self.y = ALTURA - self.ALTURA

    def rect(self):
        return pygame.Rect(self.x, self.y, self.LARGURA, self.ALTURA)

    def desenhar(self, tela):
        pygame.draw.rect(tela, BRANCO, self.rect())


class RaqueteDoJogador(Raquete):
    VELOCIDADE = 420

    def update(self, dt):
        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_UP]:
            self.y -= self.VELOCIDADE * dt
        if teclas[pygame.K_DOWN]:
            self.y += self.VELOCIDADE * dt

        self.limitar_na_tela()


class RaqueteDoOponente(Raquete):
    VELOCIDADE = 300

    def __init__(self, x, bola):
        super().__init__(x)
        self.bola = bola

    def update(self, dt):
        if self.y + self.ALTURA / 2 < self.bola.y:
            self.y += self.VELOCIDADE * dt
        if self.y + self.ALTURA / 2 > self.bola.y:
            self.y -= self.VELOCIDADE * dt


class Placar:
    """Desenha, mas nao se atualiza: por isso nao e uma Entidade."""

    def __init__(self):
        self.jogador = 0
        self.oponente = 0
        self.fonte = pygame.font.Font(None, 74)

    def desenhar(self, tela):
        texto = self.fonte.render(f"{self.jogador}   {self.oponente}", True, BRANCO)
        tela.blit(texto, (330, 20))


class World:
    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()

        self.bola = Bola()
        self.jogador = RaqueteDoJogador(30)
        self.oponente = RaqueteDoOponente(755, self.bola)
        self.entidades = [self.jogador, self.oponente, self.bola]

        self.placar = Placar()
        self.rodando = True

    def inputs(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False

    def update(self, dt):
        for entidade in self.entidades:
            entidade.update(dt)

        self.fisica()

    def fisica(self):
        bola_rect = self.bola.rect()

        if bola_rect.colliderect(self.jogador.rect()):
            self.bola.vx = -self.bola.vx
        if bola_rect.colliderect(self.oponente.rect()):
            self.bola.vx = -self.bola.vx

        if self.bola.x < 0:
            self.placar.oponente += 1
            self.bola.reiniciar()
        if self.bola.x > LARGURA:
            self.placar.jogador += 1
            self.bola.reiniciar()

    def desenhar(self):
        self.tela.fill(PRETO)

        for entidade in self.entidades:
            entidade.desenhar(self.tela)

        pygame.draw.aaline(self.tela, BRANCO, (LARGURA / 2, 0), (LARGURA / 2, ALTURA))
        self.placar.desenhar(self.tela)

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
