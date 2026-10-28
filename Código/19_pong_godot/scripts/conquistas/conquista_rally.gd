extends Node

@export var quantidade: int = 10
@export var avisos: Avisos

var contador: int = 0

func _on_rebatida(_autor: String) -> void:
	contador += 1
	if contador == quantidade:
		avisos.mostrar("Rally de %d rebatidas!" % quantidade)

func _on_ponto(_autor: String) -> void:
	contador = 0
