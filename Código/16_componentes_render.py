import pygame, sys, math

pygame.init()
screen = pygame.display.set_mode((900, 600))
pygame.display.set_caption("Src 01")

clock = pygame.time.Clock()

class RenderComponent:
    def __init__(self,entity):
        self.entity = entity

    def draw(self,screen):
        pygame.draw.circle(
            screen,
            self.entity.color,
            (int(self.entity.x),int(self.entity.y)),
            20
        )

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 250
        self.health = 100
        self.color = (50, 150, 255)
        self.renderer = RenderComponent(self)

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.x -= self.speed * dt

        if keys[pygame.K_d]:
            self.x += self.speed * dt

        if keys[pygame.K_w]:
            self.y -= self.speed * dt

        if keys[pygame.K_s]:
            self.y += self.speed * dt


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 100
        self.health = 50
        self.color = (220, 60, 60)
        self.renderer = RenderComponent(self)

    def update(self, dt):
        self.x -= self.speed * dt




class FlyingEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 100
        self.health = 50
        self.color = (220, 120, 60)
        self.renderer = RenderComponent(self)

    def update(self, dt):
        self.x -= self.speed * dt
        self.y += math.sin(pygame.time.get_ticks() * 0.005) * 2




player = Player(450, 450)

enemies = [
    FlyingEnemy(800, 150),
    Enemy(800, 450),
]


running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    player.update(dt)

    for enemy in enemies:
        enemy.update(dt)

    screen.fill((25, 25, 35))

    #player.draw(screen)
    if player.renderer:
        player.renderer.draw(screen)

    for enemy in enemies:
        if enemy.renderer:
            enemy.renderer.draw(screen)
        #enemy.draw(screen)

    pygame.display.flip()


pygame.quit()
