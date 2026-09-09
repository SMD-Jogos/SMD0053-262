
import pygame

pygame.init()
tela = pygame.display.set_mode((800, 600))
relogio = pygame.time.Clock()

raquete_y = 250
bola_x = 400
bola_y = 300
vel_x = 4
vel_y = 4

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()

    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_w]:
        raquete_y = raquete_y - 6
    if teclas[pygame.K_s]:
        raquete_y = raquete_y + 6

    bola_x = bola_x + vel_x
    bola_y = bola_y + vel_y

    if bola_x >= 790 or bola_x <= 10:
        vel_x = -vel_x
    if bola_y >= 590 or bola_y <= 10:
        vel_y = -vel_y

    tela.fill((10, 25, 60))
    pygame.draw.rect(tela, (255, 165, 0), (30, raquete_y, 12, 100))
    pygame.draw.circle(tela, (255, 255, 255), (bola_x, bola_y), 10)
    pygame.display.flip()

    relogio.tick(60)