class_name Raquete
extends Area2D

const ALTURA_RAQUETE: float = 100.0
const ALTURA_TELA: float = 600.0

## "jogador" ou "oponente"
@export var autor: String = ""
## Para onde a raquete manda a bola: 1 (direita) ou -1 (esquerda).
@export var direcao: int = 1

var velocidade_y: float = 0.0

func _physics_process(delta: float) -> void:
	position.y += velocidade_y * delta
	# As raquetes param nas bordas.
	position.y = clampf(position.y, 0.0, ALTURA_TELA - ALTURA_RAQUETE)

func centro_y() -> float:
	return position.y + ALTURA_RAQUETE / 2.0
