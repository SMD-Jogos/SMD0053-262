import pygame
import random

# Inicializacao
pygame.init()

LARGURA = 800
ALTURA = 600
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()
fonte = pygame.font.Font(None, 74)

# Jogador (raquete da esquerda)
jogador_x = 30
jogador_y = 250
jogador_largura = 15
jogador_altura = 100
jogador_velocidade = 7

# Oponente (raquete da direita)
oponente_x = 755
oponente_y = 250
oponente_largura = 15
oponente_altura = 100
oponente_velocidade = 5

# Bola
bola_x = 400
bola_y = 300
bola_raio = 10
bola_vx = 5
bola_vy = 5

# Placar
placar_jogador = 0
placar_oponente = 0


def reiniciar_bola():
    """Recoloca a bola no centro e sorteia uma nova direcao."""
    global bola_x, bola_y, bola_vx, bola_vy
    bola_x = 400
    bola_y = 300
    bola_vx = 5 * random.choice([1, -1])
    bola_vy = 5 * random.choice([1, -1])


# Loop principal do jogo
rodando = True
while rodando:

    # --- Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # --- Entrada do jogador ---
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_UP]:
        jogador_y -= jogador_velocidade
    if teclas[pygame.K_DOWN]:
        jogador_y += jogador_velocidade

    # Nao deixa a raquete sair da tela
    if jogador_y < 0:
        jogador_y = 0
    if jogador_y > ALTURA - jogador_altura:
        jogador_y = ALTURA - jogador_altura

    # --- IA do oponente ---
    if oponente_y + oponente_altura / 2 < bola_y:
        oponente_y += oponente_velocidade
    if oponente_y + oponente_altura / 2 > bola_y:
        oponente_y -= oponente_velocidade

    # --- Movimento da bola ---
    bola_x += bola_vx
    bola_y += bola_vy

    # Colisao com o teto e o chao
    if bola_y - bola_raio < 0 or bola_y + bola_raio > ALTURA:
        bola_vy = -bola_vy

    # --- Colisao com as raquetes ---
    bola_rect = pygame.Rect(bola_x - bola_raio, bola_y - bola_raio,
                            bola_raio * 2, bola_raio * 2)
    jogador_rect = pygame.Rect(jogador_x, jogador_y,
                               jogador_largura, jogador_altura)
    oponente_rect = pygame.Rect(oponente_x, oponente_y,
                                oponente_largura, oponente_altura)

    if bola_rect.colliderect(jogador_rect) or bola_rect.colliderect(oponente_rect):
        bola_vx = -bola_vx

    # --- Pontuacao ---
    if bola_x < 0:
        placar_oponente += 1
        reiniciar_bola()
    if bola_x > LARGURA:
        placar_jogador += 1
        reiniciar_bola()

    # --- Desenho ---
    tela.fill(PRETO)
    pygame.draw.rect(tela, BRANCO, jogador_rect)
    pygame.draw.rect(tela, BRANCO, oponente_rect)
    pygame.draw.circle(tela, BRANCO, (int(bola_x), int(bola_y)), bola_raio)
    pygame.draw.aaline(tela, BRANCO, (400, 0), (400, ALTURA))

    texto = fonte.render(f"{placar_jogador}   {placar_oponente}", True, BRANCO)
    tela.blit(texto, (330, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
