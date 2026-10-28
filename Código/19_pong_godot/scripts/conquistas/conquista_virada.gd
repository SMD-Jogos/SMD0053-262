extends Node

## Quem faz a virada: "jogador" ou "oponente"
@export var quem: String = ""
@export var diferenca: int = 2
@export var texto: String = ""
@export var ruim: bool = false
@export var avisos: Avisos

# Pontos de quem menos pontos do outro.
var saldo: int = 0
var esteve_atras: bool = false

func _on_ponto(autor: String) -> void:
	if autor == quem:
		saldo += 1
	else:
		saldo -= 1

	if saldo <= -diferenca:
		esteve_atras = true
	if esteve_atras and saldo > 0:
		avisos.mostrar(texto, ruim)
		esteve_atras = false
