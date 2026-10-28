extends Node

@export var avisos: Avisos

func _on_ponto(autor: String) -> void:
	if autor != "jogador":
		return
	avisos.mostrar("Primeiro ponto!")
	# Dispara uma vez e sai da lista de observadores (o desinscrever da Aula 18).
	# owner é o World, a raiz da cena.
	owner.ponto.disconnect(_on_ponto)
