extends Node2D

signal ponto(autor: String)
signal rebatida(autor: String)
signal saque()

@onready var bola: Bola = $Bola
@onready var jogador: Raquete = $Jogador
@onready var oponente: Raquete = $Oponente
@onready var gol_esquerdo: Gol = $GolEsquerdo
@onready var gol_direito: Gol = $GolDireito
@onready var parede_cima: Parede = $ParedeCima
@onready var parede_baixo: Parede = $ParedeBaixo
@onready var conquistas: Node = $Conquistas

func _ready() -> void:
	# O placar é conectado pelo editor; as conquistas, aqui.
	# Cada filho de Conquistas recebe só os sinais cujo método ele tem.
	# Tirar o nó Conquistas da cena desliga todas.
	for conquista: Node in conquistas.get_children():
		if conquista.has_method("_on_ponto"):
			ponto.connect(conquista._on_ponto)
		if conquista.has_method("_on_rebatida"):
			rebatida.connect(conquista._on_rebatida)
		if conquista.has_method("_on_saque"):
			saque.connect(conquista._on_saque)

	jogador.area_entered.connect(_on_raquete_area_entered.bind(jogador))
	oponente.area_entered.connect(_on_raquete_area_entered.bind(oponente))
	gol_esquerdo.area_entered.connect(_on_gol_area_entered.bind(gol_esquerdo))
	gol_direito.area_entered.connect(_on_gol_area_entered.bind(gol_direito))

	parede_cima.area_entered.connect(_on_parede_area_entered.bind(parede_cima))
	parede_baixo.area_entered.connect(_on_parede_area_entered.bind(parede_baixo))

	_repor_bola()

# Só conta como rebatida se a bola vinha na direção da raquete.
func _on_raquete_area_entered(_area: Area2D, raquete: Raquete) -> void:
	if bola.velocidade.x * raquete.direcao >= 0.0:
		return
	bola.velocidade.x = raquete.direcao * absf(bola.velocidade.x)
	rebatida.emit(raquete.autor)

func _on_gol_area_entered(_area: Area2D, gol: Gol) -> void:
	ponto.emit(gol.autor)
	_repor_bola()

# A parede não emite sinal: nenhum observador se importa com o quique.
func _on_parede_area_entered(_area: Area2D, parede: Parede) -> void:
	if bola.velocidade.y * parede.direcao > 0.0:
		return
	bola.velocidade.y = parede.direcao * absf(bola.velocidade.y)

func _repor_bola() -> void:
	bola.reiniciar()
	saque.emit()
