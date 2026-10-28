class_name Bola
extends Area2D

const DIAMETRO_BOLA: int = 20
const VELOCIDADE_BOLA: float = 300.0
const CENTRO_TELA: Vector2 = Vector2(400, 300)

var velocidade: Vector2 = Vector2.ZERO

func _draw() -> void:
	draw_circle(Vector2.ZERO, DIAMETRO_BOLA / 2.0, Color.WHITE)

func _physics_process(delta: float) -> void:
	position += velocidade * delta

## Volta ao centro, em diagonal aleatória.
func reiniciar() -> void:
	position = CENTRO_TELA
	velocidade.x = VELOCIDADE_BOLA * [1, -1].pick_random()
	velocidade.y = VELOCIDADE_BOLA * [1, -1].pick_random()
