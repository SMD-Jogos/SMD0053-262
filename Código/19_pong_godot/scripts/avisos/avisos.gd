class_name Avisos
extends VBoxContainer

const DURACAO_AVISO: float = 2.0
const TAMANHO_FONTE: int = 40
const COR_BOA: Color = Color(1, 1, 1)
const COR_RUIM: Color = Color8(235, 100, 80)
const MARGEM_HORIZONTAL: int = 12
const MARGEM_VERTICAL: int = 6

func mostrar(texto: String, ruim: bool = false) -> void:
	var cor: Color = COR_BOA
	if ruim:
		cor = COR_RUIM

	var fundo: StyleBoxFlat = StyleBoxFlat.new()
	fundo.bg_color = Color.BLACK
	fundo.content_margin_left = MARGEM_HORIZONTAL
	fundo.content_margin_right = MARGEM_HORIZONTAL
	fundo.content_margin_top = MARGEM_VERTICAL
	fundo.content_margin_bottom = MARGEM_VERTICAL

	var faixa: Label = Label.new()
	faixa.text = texto
	faixa.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	faixa.add_theme_font_size_override("font_size", TAMANHO_FONTE)
	faixa.add_theme_color_override("font_color", cor)
	faixa.add_theme_stylebox_override("normal", fundo)
	add_child(faixa)
	# O aviso mais novo fica em cima.
	move_child(faixa, 0)

	get_tree().create_timer(DURACAO_AVISO).timeout.connect(faixa.queue_free)
