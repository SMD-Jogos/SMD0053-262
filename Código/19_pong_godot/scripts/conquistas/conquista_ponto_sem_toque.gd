extends Node

## Quem marca o ponto: "jogador" ou "oponente"
@export var quem: String = ""
@export var texto: String = ""
@export var ruim: bool = false
@export var avisos: Avisos

var adversario_tocou: bool = false

func _on_saque() -> void:
	adversario_tocou = false

func _on_rebatida(autor: String) -> void:
	if autor != quem:
		adversario_tocou = true

func _on_ponto(autor: String) -> void:
	if autor == quem and not adversario_tocou:
		avisos.mostrar(texto, ruim)
