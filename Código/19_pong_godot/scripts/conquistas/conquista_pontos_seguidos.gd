extends Node

## "jogador" ou "oponente"
@export var quem: String = ""
@export var quantidade: int = 3
@export var texto: String = ""
@export var ruim: bool = false
@export var avisos: Avisos

var seguidos: int = 0

func _on_ponto(autor: String) -> void:
	if autor == quem:
		seguidos += 1
	else:
		seguidos = 0

	if seguidos == quantidade:
		avisos.mostrar(texto, ruim)
