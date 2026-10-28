extends Node

const VELOCIDADE_JOGADOR: float = 420.0

@onready var raquete: Raquete = get_parent()

func _physics_process(_delta: float) -> void:
	raquete.velocidade_y = Input.get_axis("mover_cima", "mover_baixo") * VELOCIDADE_JOGADOR
