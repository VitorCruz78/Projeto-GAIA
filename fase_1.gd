extends Node2D

const PLANTA_CENA = preload("res://planta_carvalho.tscn")
const HERBIVORO_CENA = preload("res://herbivoro_coelho.tscn")

var tipo_selecionado: String = "planta"
var pontos_biodiversidade: int = 100

@onready var label_pontos: Label = $UI_Layer/PainelUI/Margin/VBox/LabelPontos
@onready var label_plantas: Label = $UI_Layer/PainelUI/Margin/VBox/LabelPlantas
@onready var label_herbivoros: Label = $UI_Layer/PainelUI/Margin/VBox/LabelHerbivoros
@onready var label_modo: Label = $UI_Layer/PainelUI/Margin/VBox/LabelModo
@onready var organismos: Node2D = $Organismos

func _ready() -> void:
	# Processa mesmo com a arvore pausada para manter a UI responsiva
	process_mode = Node.PROCESS_MODE_ALWAYS
	atualizar_ui()

func _process(_delta: float) -> void:
	atualizar_ui()

# Usa _unhandled_input para nao conflitar com cliques nos botoes da UI
func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1:
				tipo_selecionado = "planta"
			KEY_2:
				tipo_selecionado = "herbivoro"
			KEY_P:
				_on_botao_pausar_pressed()
			KEY_N:
				_on_botao_normal_pressed()
			KEY_R:
				_on_botao_rapido_pressed()

	if event is InputEventMouseButton:
		if event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			spawn_organismo(event.position)

func spawn_organismo(posicao: Vector2) -> void:
	var nova_instancia: Node = null
	var custo: int = 0

	match tipo_selecionado:
		"planta":
			nova_instancia = PLANTA_CENA.instantiate()
			custo = 10
		"herbivoro":
			nova_instancia = HERBIVORO_CENA.instantiate()
			custo = 25

	if nova_instancia == null:
		return

	if pontos_biodiversidade < custo:
		nova_instancia.free()
		print("Pontos insuficientes para adicionar: ", tipo_selecionado)
		return

	pontos_biodiversidade -= custo
	nova_instancia.position = posicao
	organismos.add_child(nova_instancia)

# --- Callbacks dos botoes de especie ---

func _on_botao_planta_pressed() -> void:
	tipo_selecionado = "planta"

func _on_botao_herbivoro_pressed() -> void:
	tipo_selecionado = "herbivoro"

# --- Callbacks do sistema de tempo ---

func _on_botao_pausar_pressed() -> void:
	get_tree().paused = not get_tree().paused

func _on_botao_normal_pressed() -> void:
	Engine.time_scale = 1.0
	get_tree().paused = false

func _on_botao_rapido_pressed() -> void:
	Engine.time_scale = 3.0
	get_tree().paused = false

# --- Atualizacao da UI ---

func atualizar_ui() -> void:
	var num_plantas: int = get_tree().get_nodes_in_group("comida").size()
	var num_herbivoros: int = get_tree().get_nodes_in_group("herbivoros").size()

	label_pontos.text = "Pontos de Biodiversidade: %d" % pontos_biodiversidade
	label_plantas.text = "Plantas: %d" % num_plantas
	label_herbivoros.text = "Herbivoros: %d" % num_herbivoros

	var status_tempo: String = ""
	if get_tree().paused:
		status_tempo = " [PAUSADO]"
	elif Engine.time_scale > 1.0:
		status_tempo = " [x%.0f]" % Engine.time_scale

	label_modo.text = "Modo: %s%s" % [tipo_selecionado, status_tempo]
