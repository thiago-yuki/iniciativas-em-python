import random
import pygame

LARGURA, ALTURA = 800, 500
FPS = 60
COR_FUNDO = (15, 15, 25)
COR_OBJ = (235, 235, 235)

VEL_RAQUETE = 380
VEL_BOLA_INICIAL = 300
VEL_BOLA_MAX = 900
ACEL_PONTO = 40
ACEL_REBATIDA = 1.05
RAQ_ALTURA = 90
RAQ_ALTURA_MIN = 30
RAQ_ENCOLHE = 12
PONTOS_VITORIA = 5
DT_MAX = 0.05
PAUSA_SAQUE = 1.0

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pong")
relogio = pygame.time.Clock()
fonte = pygame.font.Font(None, 64)
fonte_peq = pygame.font.Font(None, 28)


class Raquete:
    def __init__(self, x):
        self.rect = pygame.Rect(x, 0, 12, RAQ_ALTURA)
        self.resetar()

    def resetar(self):
        self.rect.height = RAQ_ALTURA
        self.y = ALTURA / 2 - RAQ_ALTURA / 2
        self.rect.y = round(self.y)

    def mover(self, direcao, vel, dt):
        self.y += direcao * vel * dt
        self._limitar()

    def encolher(self):
        centro = self.y + self.rect.height / 2
        self.rect.height = max(RAQ_ALTURA_MIN, self.rect.height - RAQ_ENCOLHE)
        self.y = centro - self.rect.height / 2
        self._limitar()

    def _limitar(self):
        self.y = max(0, min(ALTURA - self.rect.height, self.y))
        self.rect.y = round(self.y)


esquerda = Raquete(30)
direita = Raquete(LARGURA - 42)
bola = pygame.Rect(0, 0, 16, 16)
bx = by = vx = vy = 0.0
vel_bola = VEL_BOLA_INICIAL
placar = [0, 0]
vencedor = None
contra_ia = True
aguardando = True
pausa = 0.0


def sacar(direcao):
    global vx, vy, bx, by
    bx, by = LARGURA / 2 - 8, ALTURA / 2 - 8
    bola.topleft = (round(bx), round(by))
    vx = vel_bola * direcao
    vy = vel_bola * random.uniform(-0.7, 0.7)


def novo_jogo():
    global placar, vencedor, vel_bola, aguardando, pausa
    placar = [0, 0]
    vencedor = None
    vel_bola = VEL_BOLA_INICIAL
    esquerda.resetar()
    direita.resetar()
    aguardando = True
    pausa = 0.0
    sacar(random.choice((-1, 1)))


def direcao_teclas(teclas, cima, baixo):
    return int(any(teclas[k] for k in baixo)) - int(any(teclas[k] for k in cima))


def direcao_ia(r):
    if r.rect.centery < bola.centery - 10:
        return 1
    if r.rect.centery > bola.centery + 10:
        return -1
    return 0


def rebater(raq, lado):
    global vx, vy, bx
    offset = (bola.centery - raq.rect.centery) / (raq.rect.height / 2)
    offset = max(-1.0, min(1.0, offset))
    velocidade = min(abs(vx) * ACEL_REBATIDA, VEL_BOLA_MAX)
    vx = velocidade * lado
    vy = velocidade * offset * 0.8
    bx = raq.rect.right if lado > 0 else raq.rect.left - bola.width


def pontuar(jogador):
    global vel_bola, vencedor, pausa
    placar[jogador] += 1
    (esquerda, direita)[jogador].encolher()
    vel_bola = min(vel_bola + ACEL_PONTO, VEL_BOLA_MAX)
    if placar[jogador] >= PONTOS_VITORIA:
        vencedor = "Esquerda" if jogador == 0 else "Direita"
    else:
        sacar(1 if jogador == 0 else -1)
        pausa = PAUSA_SAQUE


novo_jogo()
rodando = True
while rodando:
    dt = min(relogio.tick(FPS) / 1000, DT_MAX)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and aguardando:
                aguardando = False
            elif evento.key == pygame.K_r and vencedor:
                novo_jogo()
            elif evento.key in (pygame.K_1, pygame.K_2):
                novo_modo = evento.key == pygame.K_1
                if novo_modo != contra_ia:
                    contra_ia = novo_modo
                    novo_jogo()

    teclas = pygame.key.get_pressed()
    if contra_ia:
        esquerda.mover(direcao_teclas(teclas, (pygame.K_w, pygame.K_UP),
                                      (pygame.K_s, pygame.K_DOWN)), VEL_RAQUETE, dt)
        direita.mover(direcao_ia(direita), VEL_RAQUETE * 0.75, dt)
    else:
        esquerda.mover(direcao_teclas(teclas, (pygame.K_w,), (pygame.K_s,)), VEL_RAQUETE, dt)
        direita.mover(direcao_teclas(teclas, (pygame.K_UP,), (pygame.K_DOWN,)), VEL_RAQUETE, dt)

    if pausa > 0:
        pausa -= dt

    if vencedor is None and not aguardando and pausa <= 0:
        bx += vx * dt
        by += vy * dt
        bola.topleft = (round(bx), round(by))

        if bola.top <= 0 and vy < 0:
            vy = -vy
            by = 0
        elif bola.bottom >= ALTURA and vy > 0:
            vy = -vy
            by = ALTURA - bola.height

        if bola.colliderect(esquerda.rect) and vx < 0 and bola.centerx > esquerda.rect.centerx:
            rebater(esquerda, +1)
        elif bola.colliderect(direita.rect) and vx > 0 and bola.centerx < direita.rect.centerx:
            rebater(direita, -1)

        bola.topleft = (round(bx), round(by))

        if bola.right < 0:
            pontuar(1)
        elif bola.left > LARGURA:
            pontuar(0)

    tela.fill(COR_FUNDO)
    pygame.draw.line(tela, (70, 70, 90), (LARGURA // 2, 0), (LARGURA // 2, ALTURA), 2)
    pygame.draw.rect(tela, COR_OBJ, esquerda.rect)
    pygame.draw.rect(tela, COR_OBJ, direita.rect)
    pygame.draw.ellipse(tela, COR_OBJ, bola)
    txt = fonte.render(f"{placar[0]}   {placar[1]}", True, COR_OBJ)
    tela.blit(txt, txt.get_rect(midtop=(LARGURA // 2, 15)))
    if vencedor:
        msg = fonte_peq.render(f"{vencedor} venceu! R para reiniciar", True, COR_OBJ)
        tela.blit(msg, msg.get_rect(center=(LARGURA // 2, ALTURA // 2 - 40)))
    elif aguardando:
        msg = fonte_peq.render("Pressione ESPAÇO para começar", True, COR_OBJ)
        tela.blit(msg, msg.get_rect(center=(LARGURA // 2, ALTURA // 2 - 40)))
    modo = "1: contra IA (W/S ou setas)" if contra_ia else "2: dois jogadores (W/S e setas)"
    tela.blit(fonte_peq.render(modo, True, (150, 150, 170)), (10, ALTURA - 28))
    pygame.display.flip()

pygame.quit()
pygame.quit()