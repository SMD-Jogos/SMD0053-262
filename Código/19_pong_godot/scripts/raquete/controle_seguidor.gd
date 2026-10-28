extends Node

const VELOCIDADE_OPONENTE: float = 205.0

## Quem o oponente segue (a bola).
@export var alvo: Node2D

@onready var raquete: Raquete = get_parent()

func _physics_process(_delta: float) -> void:
	raquete.velocidade_y = 0.0

	if raquete.centro_y() < alvo.position.y:
		raquete.velocidade_y = VELOCIDADE_OPONENTE
	if raquete.centro_y() > alvo.position.y:
		raquete.velocidade_y = -VELOCIDADE_OPONENTE
