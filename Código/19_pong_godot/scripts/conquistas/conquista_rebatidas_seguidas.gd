extends Node

@export var quantidade: int = 10
@export var avisos: Avisos

var contador: int = 0

func _on_rebatida(autor: String) -> void:
	if autor != "jogador":
		return
	contador += 1
	if contador == quantidade:
		avisos.mostrar("%d rebatidas seguidas!" % quantidade)

func _on_ponto(autor: String) -> void:
	if autor == "oponente":
		contador = 0
