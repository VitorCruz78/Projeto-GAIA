extends Control

var paginas: Array[String] = [
	"🌱 [b]Plantas[/b] são [b]produtores[/b]: convertem luz solar em energia por fotossíntese. São a base de toda cadeia alimentar.",
	"🐰 [b]Herbívoros[/b] são consumidores primários: se alimentam de plantas. Sem plantas suficientes, morrem de fome.",
	"🐺 [b]Carnívoros[/b] são consumidores secundários: caçam herbívoros. Regulam a população de herbívoros.",
	"⚖️ [b]Equilíbrio ecológico[/b]: cada espécie depende das outras. Muitos herbívoros destroem as plantas; poucos e os carnívoros morrem de fome.",
	"🔄 [b]Cadeia alimentar[/b]:\nSol → Plantas → Herbívoros → Carnívoros\nA energia flui em um único sentido.",
	"🌿 [b]Biodiversidade[/b]: quanto mais espécies diferentes, mais resiliente é o ecossistema. Sistemas com baixa diversidade colapsam facilmente.",
	"🌡️ [b]Eventos ambientais[/b] como secas e espécies invasoras testam a resiliência do ecossistema. Espécies adaptadas sobrevivem melhor.",
	"🧬 [b]Evolução[/b]: ao longo do tempo, espécies desenvolvem adaptações ao ambiente. No jogo, você pode acelerar esse processo!",
]
var indice: int = 0

@onready var label_pagina: RichTextLabel = $Panel/VBox/LabelPagina
@onready var label_num: Label = $Panel/VBox/LabelNum
@onready var botao_anterior: Button = $Panel/VBox/HBoxBtns/BotaoAnterior
@onready var botao_proximo: Button = $Panel/VBox/HBoxBtns/BotaoProximo

func _ready() -> void:
	mostrar_pagina()

func mostrar_pagina() -> void:
	label_pagina.text = "[center]" + paginas[indice] + "[/center]"
	label_num.text = "Página %d / %d" % [indice + 1, paginas.size()]
	botao_anterior.disabled = (indice == 0)
	botao_proximo.disabled = (indice == paginas.size() - 1)

func _on_botao_anterior_pressed() -> void:
	if indice > 0:
		indice -= 1
		mostrar_pagina()

func _on_botao_proximo_pressed() -> void:
	if indice < paginas.size() - 1:
		indice += 1
		mostrar_pagina()

func _on_botao_voltar_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/mapa_mundo.tscn")
