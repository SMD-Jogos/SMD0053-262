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
# Na Aula 17 o oponente andava a 300 e nunca errava; a 205 ele erra com frequência, para dar para testar as conquistas.
VELOCIDADE_OPONENTE = 205

COR_RUIM = (235, 100, 80)
DURACAO_AVISO = 2.0


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
# Observer: o sujeito avisa, os observadores decidem o que fazer.
# ---------------------------------------------------------------------------

class Observador(ABC):
    # evento: o que aconteceu ("ponto", "rebatida"...)
    # autor: quem fez ("jogador" ou "oponente"); o aviso vai para todos da lista
    @abstractmethod
    def ao_notificar(self, evento, autor):
        ...


class Sujeito:
    def __init__(self):
        self.observadores = []

    def inscrever(self, observador):
        self.observadores.append(observador)

    def desinscrever(self, observador):
        self.observadores.remove(observador)

    def notificar(self, evento, autor):
        # Percorre uma copia da lista: um observador pode se desinscrever
        # enquanto a lista esta sendo percorrida.
        for observador in list(self.observadores):
            observador.ao_notificar(evento, autor)


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
# Observadores: o placar e as conquistas.
# ---------------------------------------------------------------------------

# O placar foi o primeiro observador do jogo, só não tinha esse nome.
class Placar(Observador):
    def __init__(self):
        self.jogador = 0
        self.oponente = 0
        self.fonte = pygame.font.Font(None, 74)

    def ao_notificar(self, evento, autor):
        if evento == "ponto" and autor == "jogador":
            self.jogador += 1
        if evento == "ponto" and autor == "oponente":
            self.oponente += 1

    def desenhar(self, tela):
        # cada número do seu lado da rede, a 40 px dela
        esquerdo = self.fonte.render(str(self.jogador), True, BRANCO)
        direito = self.fonte.render(str(self.oponente), True, BRANCO)
        tela.blit(esquerdo, esquerdo.get_rect(topright=(LARGURA / 2 - 40, 20)))
        tela.blit(direito, direito.get_rect(topleft=(LARGURA / 2 + 40, 20)))


def outro(quem):
    if quem == "jogador":
        return "oponente"
    return "jogador"


class ConquistaPrimeiroPonto(Observador):
    """Dispara uma vez e sai da lista de observadores."""

    def __init__(self, eventos, avisos):
        self.eventos = eventos
        self.avisos = avisos

    def ao_notificar(self, evento, autor):
        if evento == "ponto" and autor == "jogador":
            self.avisos.mostrar("Primeiro ponto!")
            self.eventos.desinscrever(self)


class ConquistaRebatidasSeguidas(Observador):
    def __init__(self, avisos, quantidade):
        self.avisos = avisos
        self.quantidade = quantidade
        self.contador = 0

    def ao_notificar(self, evento, autor):
        if evento == "rebatida" and autor == "jogador":
            self.contador += 1
            if self.contador == self.quantidade:
                self.avisos.mostrar(f"{self.quantidade} rebatidas seguidas!")
        if evento == "ponto" and autor == "oponente":
            self.contador = 0


class ConquistaRally(Observador):
    """Rebatidas dos dois lados, sem ninguem marcar ponto."""

    def __init__(self, avisos, quantidade):
        self.avisos = avisos
        self.quantidade = quantidade
        self.contador = 0

    def ao_notificar(self, evento, autor):
        if evento == "rebatida":
            self.contador += 1
            if self.contador == self.quantidade:
                self.avisos.mostrar(f"Rally de {self.quantidade} rebatidas!")
        if evento == "ponto":
            self.contador = 0


class ConquistaPontosSeguidos(Observador):
    """Serve para o hat-trick e para levar 3 seguidos: so muda quem."""

    def __init__(self, avisos, quem, quantidade, texto, ruim=False):
        self.avisos = avisos
        self.quem = quem
        self.quantidade = quantidade
        self.texto = texto
        self.ruim = ruim
        self.contador = 0

    def ao_notificar(self, evento, autor):
        if evento != "ponto":
            return
        if autor == self.quem:
            self.contador += 1
            if self.contador == self.quantidade:
                self.avisos.mostrar(self.texto, self.ruim)
        else:
            self.contador = 0


class ConquistaPontoSemToque(Observador):
    """Ponto marcado sem o adversario tocar na bola desde o saque."""

    def __init__(self, avisos, quem, texto, ruim=False):
        self.avisos = avisos
        self.quem = quem
        self.texto = texto
        self.ruim = ruim
        self.adversario_tocou = False

    def ao_notificar(self, evento, autor):
        if evento == "saque":
            self.adversario_tocou = False
        if evento == "rebatida" and autor == outro(self.quem):
            self.adversario_tocou = True
        if evento == "ponto" and autor == self.quem and not self.adversario_tocou:
            self.avisos.mostrar(self.texto, self.ruim)


class ConquistaVirada(Observador):
    """Estava perdendo por uma diferenca e passou a frente."""

    def __init__(self, avisos, quem, diferenca, texto, ruim=False):
        self.avisos = avisos
        self.quem = quem
        self.diferenca = diferenca
        self.texto = texto
        self.ruim = ruim
        self.saldo = 0          # pontos de quem menos pontos do outro
        self.esteve_atras = False

    def ao_notificar(self, evento, autor):
        if evento != "ponto":
            return
        if autor == self.quem:
            self.saldo += 1
        else:
            self.saldo -= 1

        if self.saldo <= -self.diferenca:
            self.esteve_atras = True
        if self.esteve_atras and self.saldo > 0:
            self.avisos.mostrar(self.texto, self.ruim)
            self.esteve_atras = False


class World:
    def __init__(self):
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Pong com todas as conquistas")
        self.clock = pygame.time.Clock()

        self.placar = Placar()
        self.avisos = Avisos()

        # O sujeito vem antes da bola: reiniciar_bola() avisa o saque.
        self.eventos = Sujeito()
        self.eventos.inscrever(self.placar)

        conquistas = [
            ConquistaPrimeiroPonto(self.eventos, self.avisos),
            ConquistaRebatidasSeguidas(self.avisos, 10),
            ConquistaRally(self.avisos, 10),
            ConquistaPontosSeguidos(self.avisos, "jogador", 3, "Hat-trick!"),
            ConquistaPontosSeguidos(self.avisos, "oponente", 3, "Levou 3 seguidos", ruim=True),
            ConquistaPontoSemToque(self.avisos, "jogador", "Ponto sem o oponente tocar"),
            ConquistaPontoSemToque(self.avisos, "oponente", "Ponto sem você tocar", ruim=True),
            ConquistaVirada(self.avisos, "jogador", 2, "Virada!"),
            ConquistaVirada(self.avisos, "oponente", 2, "Levou a virada", ruim=True),
        ]
        # Modo treino, sem conquistas? Comente as duas linhas abaixo.
        for conquista in conquistas:
            self.eventos.inscrever(conquista)

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

        self.rodando = True

    def reiniciar_bola(self):
        self.bola.x = 390
        self.bola.y = 290
        self.bola.vx = VELOCIDADE_BOLA * random.choice([1, -1])
        self.bola.vy = VELOCIDADE_BOLA * random.choice([1, -1])
        self.eventos.notificar("saque", None)

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
            self.eventos.notificar("rebatida", "jogador")
        if bola_rect.colliderect(self.oponente.rect()) and self.bola.vx > 0:
            self.bola.vx = -abs(self.bola.vx)
            self.eventos.notificar("rebatida", "oponente")

        if self.bola.x < 0:
            self.eventos.notificar("ponto", "oponente")
            self.reiniciar_bola()
        if self.bola.x > LARGURA:
            self.eventos.notificar("ponto", "jogador")
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
