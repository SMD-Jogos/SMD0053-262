"""
Monte a entidade — Aula 17, Programação para Jogos I

Arraste as peças de baixo para os encaixes da Entidade.
A entidade montada roda no campo à direita.

  arrastar peça -> encaixe   encaixa (só no encaixe da mesma família)
  arrastar peça para fora    tira do encaixe
  clique direito no encaixe  esvazia o encaixe
  ESPAÇO                     mostra / esconde que entidade é essa
  R                          esvazia tudo e recomeça
  setas                      controlam a entidade quando ela tem ControleTeclado
"""

import pygame
import random
from abc import ABC, abstractmethod

LARGURA_JANELA = 1280
ALTURA_JANELA = 720

# Cores do sistema "Papel técnico"
PAPEL = (250, 249, 246)
TINTA = (22, 21, 15)
APOIO = (125, 120, 106)
TIJOLO = (140, 47, 30)
BLOCO = (240, 238, 230)
CAMPO = (22, 21, 15)
BRANCO = (250, 249, 246)

# O campo onde a entidade roda (coordenadas próprias, como no Pong)
CAMPO_X, CAMPO_Y = 640, 60
CAMPO_L, CAMPO_A = 600, 420

PASSO = 1 / 60
ATRASO_MAXIMO = 0.25


# ---------------------------------------------------------------------------
# Os mesmos componentes do 17_pong_componentes.py, com as medidas do campo
# ---------------------------------------------------------------------------

class Entidade:
    def __init__(self):
        self.controle = None
        self.fisica = None
        self.grafico = None
        self.reiniciar()

    def reiniciar(self):
        self.x = CAMPO_L / 2
        self.y = CAMPO_A / 2
        self.vx = 0
        self.vy = 0
        self.largura = 15
        self.altura = 100

    def update(self, dt):
        if self.controle is not None:
            self.controle.update(self, dt)
        if self.fisica is not None:
            self.fisica.update(self, dt)

    def desenhar(self, tela):
        if self.grafico is not None:
            self.grafico.desenhar(self, tela)

    def rect(self):
        return pygame.Rect(CAMPO_X + self.x, CAMPO_Y + self.y, self.largura, self.altura)


class Controle(ABC):
    @abstractmethod
    def update(self, entidade, dt):
        ...


class ControleTeclado(Controle):
    def __init__(self, tecla_cima=pygame.K_UP, tecla_baixo=pygame.K_DOWN, velocidade=420):
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
    def __init__(self, alvo, velocidade=300):
        self.alvo = alvo
        self.velocidade = velocidade

    def update(self, entidade, dt):
        centro = entidade.y + entidade.altura / 2
        centro_alvo = self.alvo.y
        entidade.vy = 0
        if centro < centro_alvo - 2:
            entidade.vy = self.velocidade
        if centro > centro_alvo + 2:
            entidade.vy = -self.velocidade


class Fisica(ABC):
    @abstractmethod
    def update(self, entidade, dt):
        ...


class FisicaRaquete(Fisica):
    def update(self, entidade, dt):
        entidade.y += entidade.vy * dt
        if entidade.y < 0:
            entidade.y = 0
        if entidade.y > CAMPO_A - entidade.altura:
            entidade.y = CAMPO_A - entidade.altura


class FisicaBola(Fisica):
    VELOCIDADE = 300

    def update(self, entidade, dt):
        if entidade.vx == 0:
            entidade.vx = self.VELOCIDADE * random.choice([1, -1])
            entidade.vy = self.VELOCIDADE * random.choice([1, -1])

        entidade.x += entidade.vx * dt
        entidade.y += entidade.vy * dt

        if entidade.y < 0 or entidade.y + entidade.altura > CAMPO_A:
            entidade.vy = -entidade.vy
        # sem raquetes neste campo: a bola quica também nas laterais
        if entidade.x < 0 or entidade.x + entidade.largura > CAMPO_L:
            entidade.vx = -entidade.vx


class Grafico(ABC):
    @abstractmethod
    def desenhar(self, entidade, tela):
        ...


class GraficoRetangulo(Grafico):
    def desenhar(self, entidade, tela):
        pygame.draw.rect(tela, BRANCO, entidade.rect())


class GraficoCirculo(Grafico):
    def desenhar(self, entidade, tela):
        r = entidade.rect()
        raio = min(r.width, r.height) // 2
        pygame.draw.circle(tela, BRANCO, r.center, raio)


# ---------------------------------------------------------------------------
# A bancada: peças, encaixes e arrastar
# ---------------------------------------------------------------------------

FAMILIAS = ["controle", "fisica", "grafico"]

PECAS = [
    ("controle", "ControleTeclado"),
    ("controle", "ControleSeguidor"),
    ("fisica", "FisicaRaquete"),
    ("fisica", "FisicaBola"),
    ("grafico", "GraficoRetangulo"),
    ("grafico", "GraficoCirculo"),
]

# Combinações conhecidas do Pong: (controle, fisica, grafico) -> nome
CONHECIDAS = {
    ("ControleTeclado", "FisicaRaquete", "GraficoRetangulo"): "Jogador",
    ("ControleSeguidor", "FisicaRaquete", "GraficoRetangulo"): "Oponente",
    (None, "FisicaBola", "GraficoCirculo"): "Bola",
}

PECA_L, PECA_A = 280, 48
ENCAIXE_X, ENCAIXE_Y = 60, 150
ENCAIXE_L, ENCAIXE_A = 360, 64


class Bancada:
    def __init__(self):
        self.entidade = Entidade()
        self.alvo = Entidade()          # uma bola-guia para o ControleSeguidor
        self.alvo.largura = self.alvo.altura = 14
        self.alvo.fisica = FisicaBola()
        self.encaixes = {f: None for f in FAMILIAS}
        self.arrastando = None          # (familia, nome, deslocamento)
        self.pos_mouse = (0, 0)
        self.revelar = False

        self.fonte_titulo = pygame.font.Font(None, 44)
        self.fonte = pygame.font.Font(None, 32)
        self.fonte_peq = pygame.font.Font(None, 26)

        self.retangulos_pecas = []
        x0, y0 = 60, 560
        for i, (familia, nome) in enumerate(PECAS):
            coluna = i // 2
            linha = i % 2
            r = pygame.Rect(x0 + coluna * (PECA_L + 30), y0 + linha * (PECA_A + 14), PECA_L, PECA_A)
            self.retangulos_pecas.append((r, familia, nome))

    # --- encaixes --------------------------------------------------------
    def retangulo_encaixe(self, familia):
        i = FAMILIAS.index(familia)
        return pygame.Rect(ENCAIXE_X, ENCAIXE_Y + ENCAIXE_A * (i + 1), ENCAIXE_L, ENCAIXE_A)

    def criar(self, nome):
        if nome == "ControleTeclado":
            return ControleTeclado()
        if nome == "ControleSeguidor":
            return ControleSeguidor(self.alvo)
        if nome == "FisicaRaquete":
            return FisicaRaquete()
        if nome == "FisicaBola":
            return FisicaBola()
        if nome == "GraficoRetangulo":
            return GraficoRetangulo()
        if nome == "GraficoCirculo":
            return GraficoCirculo()

    def aplicar(self):
        """Remonta a entidade a partir dos encaixes."""
        e = self.entidade
        e.reiniciar()
        e.controle = self.criar(self.encaixes["controle"]) if self.encaixes["controle"] else None
        e.fisica = self.criar(self.encaixes["fisica"]) if self.encaixes["fisica"] else None
        e.grafico = self.criar(self.encaixes["grafico"]) if self.encaixes["grafico"] else None

        # o tamanho acompanha o formato desenhado
        if self.encaixes["grafico"] == "GraficoCirculo":
            e.largura = e.altura = 24
        e.x = CAMPO_L / 2 - e.largura / 2
        e.y = CAMPO_A / 2 - e.altura / 2

    def nome_da_entidade(self):
        chave = (self.encaixes["controle"], self.encaixes["fisica"], self.encaixes["grafico"])
        if chave == (None, None, None):
            return "Entidade vazia"
        return CONHECIDAS.get(chave, "Nenhuma do Pong: uma entidade nova")

    # --- eventos ---------------------------------------------------------
    def evento(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.pos_mouse = ev.pos

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for r, familia, nome in self.retangulos_pecas:
                if r.collidepoint(ev.pos):
                    self.arrastar(familia, nome, r, ev.pos)
                    return
            for familia in FAMILIAS:
                nome = self.encaixes[familia]
                r = self.retangulo_encaixe(familia)
                if nome and r.collidepoint(ev.pos):
                    self.encaixes[familia] = None
                    self.aplicar()
                    self.arrastar(familia, nome, r, ev.pos)
                    return

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
            for familia in FAMILIAS:
                if self.retangulo_encaixe(familia).collidepoint(ev.pos):
                    self.encaixes[familia] = None
                    self.aplicar()

        if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and self.arrastando:
            familia, nome, _ = self.arrastando
            if self.retangulo_encaixe(familia).collidepoint(ev.pos):
                self.encaixes[familia] = nome
                self.aplicar()
            self.arrastando = None

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                self.revelar = not self.revelar
            if ev.key == pygame.K_r:
                self.encaixes = {f: None for f in FAMILIAS}
                self.revelar = False
                self.aplicar()

    def arrastar(self, familia, nome, r, pos):
        deslocamento = (pos[0] - r.x, pos[1] - r.y)
        self.arrastando = (familia, nome, deslocamento)

    # --- atualização e desenho -------------------------------------------
    def update(self, dt):
        self.alvo.update(dt)
        self.entidade.update(dt)

    def desenhar_peca(self, tela, r, familia, nome, destaque=False):
        pygame.draw.rect(tela, BLOCO, r)
        pygame.draw.rect(tela, TIJOLO if destaque else TINTA, r, 3 if destaque else 1)
        texto = self.fonte.render(nome, True, TINTA)
        tela.blit(texto, texto.get_rect(center=r.center))

    def desenhar(self, tela):
        tela.fill(PAPEL)

        titulo = self.fonte_titulo.render("Monte a entidade", True, TINTA)
        tela.blit(titulo, (60, 50))
        dica = self.fonte_peq.render("arraste as peças para os encaixes  ·  ESPAÇO revela  ·  R recomeça", True, APOIO)
        tela.blit(dica, (60, 95))

        # a entidade (contêiner)
        cabecalho = pygame.Rect(ENCAIXE_X, ENCAIXE_Y, ENCAIXE_L, ENCAIXE_A)
        pygame.draw.rect(tela, TIJOLO, cabecalho)
        t = self.fonte.render("Entidade", True, BRANCO)
        tela.blit(t, t.get_rect(center=cabecalho.center))

        familia_arrastada = self.arrastando[0] if self.arrastando else None
        for familia in FAMILIAS:
            r = self.retangulo_encaixe(familia)
            nome = self.encaixes[familia]
            if nome:
                self.desenhar_peca(tela, r, familia, nome)
            else:
                pygame.draw.rect(tela, PAPEL, r)
                pygame.draw.rect(tela, TIJOLO if familia == familia_arrastada else APOIO, r,
                                 3 if familia == familia_arrastada else 1)
                vazio = self.fonte_peq.render(familia + ": vazio", True, APOIO)
                tela.blit(vazio, vazio.get_rect(center=r.center))

        # resposta
        if self.revelar:
            resp = self.fonte_titulo.render(self.nome_da_entidade(), True, TIJOLO)
            tela.blit(resp, (ENCAIXE_X, ENCAIXE_Y + ENCAIXE_A * 4 + 30))

        # peças disponíveis
        rotulo = self.fonte_peq.render("Peças", True, APOIO)
        tela.blit(rotulo, (60, 530))
        for r, familia, nome in self.retangulos_pecas:
            self.desenhar_peca(tela, r, familia, nome)

        # o campo onde a entidade roda
        campo = pygame.Rect(CAMPO_X, CAMPO_Y, CAMPO_L, CAMPO_A)
        pygame.draw.rect(tela, CAMPO, campo)
        if self.encaixes["controle"] == "ControleSeguidor":
            pygame.draw.circle(tela, APOIO, self.alvo.rect().center, 7)
        if self.encaixes["grafico"] is None and any(self.encaixes.values()):
            # sem gráfico, a entidade existe mas não aparece
            pygame.draw.rect(tela, APOIO, self.entidade.rect(), 1)
        tela.set_clip(campo)
        self.entidade.desenhar(tela)
        tela.set_clip(None)

        legenda = self.fonte_peq.render("a entidade montada, rodando", True, APOIO)
        tela.blit(legenda, (CAMPO_X, CAMPO_Y + CAMPO_A + 10))

        # peça sendo arrastada
        if self.arrastando:
            familia, nome, (dx, dy) = self.arrastando
            r = pygame.Rect(self.pos_mouse[0] - dx, self.pos_mouse[1] - dy, PECA_L, PECA_A)
            self.desenhar_peca(tela, r, familia, nome, destaque=True)

        pygame.display.flip()


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption("Monte a entidade")
    relogio = pygame.time.Clock()
    bancada = Bancada()
    bancada.aplicar()

    acumulador = 0
    rodando = True
    while rodando:
        acumulador += min(relogio.tick(240) / 1000, ATRASO_MAXIMO)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            bancada.evento(ev)

        while acumulador >= PASSO:
            bancada.update(PASSO)
            acumulador -= PASSO

        bancada.desenhar(tela)

    pygame.quit()


if __name__ == "__main__":
    main()
