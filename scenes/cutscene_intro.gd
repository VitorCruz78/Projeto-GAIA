extends Control

var textos: Array[String] = [
	"Em um futuro próximo, o planeta enfrenta colapso ecológico causado por décadas de negligência...",
	"Quando tudo parece perdido, Gaia — espírito guardião da Terra — desperta e procura um aliado.",
	"Ela escolhe você: um jovem ecologista, curioso e compassivo.",
	"Munido do Códice de Gaia, você deve restaurar os biomas do mundo, um a um.",
	"Cada bioma tem seus próprios desafios. Observe, analise e equilibre os ecossistemas.",
	"A Terra precisa de você. A jornada começa agora."
]
var indice_atual: int = 0

@onready var label_texto: RichTextLabel = $Panel/VBox/LabelTexto
@onready var botao_continuar: Button = $Panel/VBox/BotaoContinuar
@onready var label_progresso: Label = $Panel/VBox/LabelProgresso

func _ready() -> void:
	mostrar_texto()

func mostrar_texto() -> void:
	label_texto.text = "[center]" + textos[indice_atual] + "[/center]"
	label_progresso.text = "%d / %d" % [indice_atual + 1, textos.size()]
	botao_continuar.text = "Próximo →" if indice_atual < textos.size() - 1 else "Começar!"

func _on_botao_continuar_pressed() -> void:
	indice_atual += 1
	if indice_atual >= textos.size():
		get_tree().change_scene_to_file("res://scenes/mapa_mundo.tscn")
	else:
		mostrar_texto()

func _on_botao_pular_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/mapa_mundo.tscn")
