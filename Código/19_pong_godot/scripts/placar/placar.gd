extends Label

@onready var rotulo_oponente: Label = $Oponente

var pontos_jogador: int = 0
var pontos_oponente: int = 0

func _ready() -> void:
	_atualizar()

func _on_ponto(autor: String) -> void:
	if autor == "jogador":
		pontos_jogador += 1
	if autor == "oponente":
		pontos_oponente += 1
	_atualizar()

func _atualizar() -> void:
	text = str(pontos_jogador)
	rotulo_oponente.text = str(pontos_oponente)
