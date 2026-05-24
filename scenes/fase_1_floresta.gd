extends Node2D

const PLANTA_CENA = preload("res://planta_carvalho.tscn")
const HERBIVORO_CENA = preload("res://herbivoro_coelho.tscn")
const CARNIVORO_CENA = preload("res://organismos/carnivoro_lobo.tscn")

const CUSTO_PLANTA: int = 10
const CUSTO_HERBIVORO: int = 25
const CUSTO_CARNIVORO: int = 50

var tipo_selecionado: String = ""
var tempo_equilibrio: float = 0.0
var tempo_total: float = 0.0
var fase_completa: bool = false
var fase_falhou: bool = false
var intro_ativa: bool = true
var renda_timer: float = 0.0
var estacao_timer: float = 0.0
var estacao_atual: int = 0  # 0=primavera 1=verão 2=outono 3=inverno
var TEMPO_META: float = 90.0
var TEMPO_ESTACAO: float = 45.0
var notificacao_timer: float = 0.0

@onready var organismos: Node2D = $Organismos
@onready var label_pontos: Label = $UI_Layer/TopBar/HBox/LabelPontos
@onready var label_bioma: Label = $UI_Layer/TopBar/HBox/LabelBioma
@onready var label_objetivo: Label = $UI_Layer/TopBar/HBox/LabelObjetivo
@onready var label_equilibrio_tempo: Label = $UI_Layer/TopBar/HBox/LabelEquilibrioTempo
@onready var label_plantas: Label = $UI_Layer/LeftPanel/VBox/LabelPlantas
@onready var label_herbivoros: Label = $UI_Layer/LeftPanel/VBox/LabelHerbivoros
@onready var label_carnivoros: Label = $UI_Layer/LeftPanel/VBox/LabelCarnivoros
@onready var barra_equilibrio: ProgressBar = $UI_Layer/LeftPanel/VBox/BarraEquilibrio
@onready var label_estacao: Label = $UI_Layer/LeftPanel/VBox/LabelEstacao
@onready var panel_vitoria: Panel = $UI_Layer/PanelVitoria
@onready var panel_derrota: Panel = $UI_Layer/PanelDerrota
@onready var panel_notificacao: Panel = $UI_Layer/PanelNotificacao
@onready var label_notificacao: Label = $UI_Layer/PanelNotificacao/VBox/LabelNotificacao
@onready var botao_planta: Button = $UI_Layer/BottomBar/HBox/BotaoPlanta
@onready var botao_herbivoro: Button = $UI_Layer/BottomBar/HBox/BotaoHerbivoro
@onready var botao_carnivoro: Button = $UI_Layer/BottomBar/HBox/BotaoCarnivoro
@onready var panel_intro: Panel = $UI_Layer/PanelIntro

const NOMES_ESTACOES: Array[String] = ["🌸 Primavera", "☀️ Verão", "🍂 Outono", "❄️ Inverno"]

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	panel_vitoria.visible = false
	panel_derrota.visible = false
	panel_notificacao.visible = false
	panel_intro.visible = true
	get_tree().paused = true
	label_bioma.text = "🌲 Floresta Temperada"
	label_objetivo.text = "Equilíbrio 90s (plantas≥4, herbívoros≥3, carnívoros≥1)"
	GameManager.pontos_atualizados.connect(_on_pontos_atualizados)
	atualizar_ui()

func _process(delta: float) -> void:
	if fase_completa or fase_falhou or intro_ativa:
		return
	tempo_total += delta
	estacao_timer += delta
	if estacao_timer >= TEMPO_ESTACAO:
		estacao_timer = 0.0
		avancar_estacao()
	renda_timer += delta
	if renda_timer >= 10.0:
		renda_timer = 0.0
		gerar_renda()
	if notificacao_timer > 0.0:
		notificacao_timer -= delta
		if notificacao_timer <= 0.0:
			panel_notificacao.visible = false
	verificar_equilibrio(delta)
	atualizar_ui()

func _unhandled_input(event: InputEvent) -> void:
	if fase_completa or fase_falhou:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1: selecionar_especie("planta")
			KEY_2: selecionar_especie("herbivoro")
			KEY_3: selecionar_especie("carnivoro")
			KEY_P: toggle_pausa()
			KEY_N: set_velocidade(1.0)
			KEY_R: set_velocidade(3.0)
			KEY_F: set_velocidade(6.0)
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		spawn_organismo(event.position)

func spawn_organismo(posicao: Vector2) -> void:
	var custo: int = 0
	var cena = null
	match tipo_selecionado:
		"planta": custo = CUSTO_PLANTA; cena = PLANTA_CENA
		"herbivoro": custo = CUSTO_HERBIVORO; cena = HERBIVORO_CENA
		"carnivoro": custo = CUSTO_CARNIVORO; cena = CARNIVORO_CENA
	if cena == null:
		mostrar_notificacao("Selecione uma espécie primeiro!")
		return
	if not GameManager.gastar_pontos(custo):
		mostrar_notificacao("Pontos de Biodiversidade insuficientes!")
		return
	var inst: Node = cena.instantiate()
	inst.position = posicao
	organismos.add_child(inst)

func verificar_equilibrio(delta: float) -> void:
	var n_p: int = get_tree().get_nodes_in_group("comida").size()
	var n_h: int = get_tree().get_nodes_in_group("herbivoros").size()
	var n_c: int = get_tree().get_nodes_in_group("carnivoros").size()
	var equilibrado: bool = n_p >= 4 and n_h >= 3 and n_c >= 1
	if equilibrado:
		tempo_equilibrio += delta
		if tempo_equilibrio >= TEMPO_META:
			vitoria()
	else:
		tempo_equilibrio = max(0.0, tempo_equilibrio - delta * 0.3)

func gerar_renda() -> void:
	var n_total: int = get_tree().get_nodes_in_group("comida").size() + \
		get_tree().get_nodes_in_group("herbivoros").size() + \
		get_tree().get_nodes_in_group("carnivoros").size()
	var renda: int = max(1, n_total / 3)
	var n_p: int = get_tree().get_nodes_in_group("comida").size()
	var n_h: int = get_tree().get_nodes_in_group("herbivoros").size()
	var n_c: int = get_tree().get_nodes_in_group("carnivoros").size()
	if n_p > 0 and n_h > 0 and n_c > 0:
		renda += 5
	if estacao_atual == 0:  # primavera bônus
		renda += 3
	GameManager.ganhar_pontos(renda)

func avancar_estacao() -> void:
	estacao_atual = (estacao_atual + 1) % 4
	mostrar_notificacao("Nova estação: " + NOMES_ESTACOES[estacao_atual])

func vitoria() -> void:
	if fase_completa:
		return
	fase_completa = true
	get_tree().paused = true
	panel_vitoria.visible = true
	GameManager.completar_bioma(1)

func mostrar_notificacao(texto: String) -> void:
	label_notificacao.text = texto
	panel_notificacao.visible = true
	notificacao_timer = 3.0

func atualizar_ui() -> void:
	var n_p: int = get_tree().get_nodes_in_group("comida").size()
	var n_h: int = get_tree().get_nodes_in_group("herbivoros").size()
	var n_c: int = get_tree().get_nodes_in_group("carnivoros").size()
	label_pontos.text = "🌿 %d BD" % GameManager.pontos_biodiversidade
	label_equilibrio_tempo.text = "Equilíbrio: %.0f/%.0fs" % [tempo_equilibrio, TEMPO_META]
	label_plantas.text = "🌳 Plantas: %d" % n_p
	label_herbivoros.text = "🐰 Herbívoros: %d" % n_h
	label_carnivoros.text = "🐺 Carnívoros: %d" % n_c
	label_estacao.text = NOMES_ESTACOES[estacao_atual]
	barra_equilibrio.value = (tempo_equilibrio / TEMPO_META) * 100.0

func selecionar_especie(esp: String) -> void:
	tipo_selecionado = esp
	botao_planta.button_pressed = (esp == "planta")
	botao_herbivoro.button_pressed = (esp == "herbivoro")
	botao_carnivoro.button_pressed = (esp == "carnivoro")

func toggle_pausa() -> void:
	get_tree().paused = not get_tree().paused

func set_velocidade(v: float) -> void:
	Engine.time_scale = v
	get_tree().paused = false

func _on_pontos_atualizados(_p: int) -> void:
	atualizar_ui()

func _on_botao_planta_pressed() -> void: selecionar_especie("planta")
func _on_botao_herbivoro_pressed() -> void: selecionar_especie("herbivoro")
func _on_botao_carnivoro_pressed() -> void: selecionar_especie("carnivoro")
func _on_botao_pausar_pressed() -> void: toggle_pausa()
func _on_botao_normal_pressed() -> void: set_velocidade(1.0)
func _on_botao_rapido_pressed() -> void: set_velocidade(3.0)
func _on_botao_muito_rapido_pressed() -> void: set_velocidade(6.0)

func _on_botao_mapa_pressed() -> void:
	get_tree().paused = false
	Engine.time_scale = 1.0
	get_tree().change_scene_to_file("res://scenes/mapa_mundo.tscn")

func _on_botao_vitoria_continuar_pressed() -> void:
	get_tree().paused = false
	Engine.time_scale = 1.0
	get_tree().change_scene_to_file("res://scenes/mapa_mundo.tscn")

func _on_botao_derrota_reiniciar_pressed() -> void:
	get_tree().paused = false
	Engine.time_scale = 1.0
	get_tree().reload_current_scene()

func _on_botao_notificacao_ok_pressed() -> void:
	panel_notificacao.visible = false
	notificacao_timer = 0.0

func _on_botao_intro_comecar_pressed() -> void:
	intro_ativa = false
	panel_intro.visible = false
	get_tree().paused = false
