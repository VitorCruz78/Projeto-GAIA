extends Node2D

const PLANTA_CENA = preload("res://organismos/planta_palmeira.tscn")
const HERBIVORO_CENA = preload("res://organismos/herbivoro_gazela.tscn")
const CARNIVORO_CENA = preload("res://organismos/carnivoro_onca.tscn")
const INVASORA_CENA = preload("res://organismos/planta_invasora.tscn")

const CUSTO_PLANTA: int = 10
const CUSTO_HERBIVORO: int = 30
const CUSTO_CARNIVORO: int = 60

var tipo_selecionado: String = ""
var tempo_equilibrio: float = 0.0
var tempo_total: float = 0.0
var fase_completa: bool = false
var fase_falhou: bool = false
var invasora_apareceu: bool = false
var invasora_eliminada: bool = false
var renda_timer: float = 0.0
var notificacao_timer: float = 0.0
var TEMPO_META: float = 60.0
var LIMITE_INVASORAS: int = 18
var modo_remocao: bool = false
var intro_ativa: bool = true

@onready var organismos: Node2D = $Organismos
@onready var label_pontos: Label = $UI_Layer/TopBar/HBox/LabelPontos
@onready var label_bioma: Label = $UI_Layer/TopBar/HBox/LabelBioma
@onready var label_objetivo: Label = $UI_Layer/TopBar/HBox/LabelObjetivo
@onready var label_equilibrio_tempo: Label = $UI_Layer/TopBar/HBox/LabelEquilibrioTempo
@onready var label_plantas: Label = $UI_Layer/LeftPanel/VBox/LabelPlantas
@onready var label_herbivoros: Label = $UI_Layer/LeftPanel/VBox/LabelHerbivoros
@onready var label_carnivoros: Label = $UI_Layer/LeftPanel/VBox/LabelCarnivoros
@onready var barra_equilibrio: ProgressBar = $UI_Layer/LeftPanel/VBox/BarraEquilibrio
@onready var label_invasoras: Label = $UI_Layer/LeftPanel/VBox/LabelInvasoras
@onready var panel_vitoria: Panel = $UI_Layer/PanelVitoria
@onready var panel_derrota: Panel = $UI_Layer/PanelDerrota
@onready var panel_notificacao: Panel = $UI_Layer/PanelNotificacao
@onready var label_notificacao: Label = $UI_Layer/PanelNotificacao/VBox/LabelNotificacao
@onready var botao_planta: Button = $UI_Layer/BottomBar/HBox/BotaoPlanta
@onready var botao_herbivoro: Button = $UI_Layer/BottomBar/HBox/BotaoHerbivoro
@onready var botao_carnivoro: Button = $UI_Layer/BottomBar/HBox/BotaoCarnivoro
@onready var botao_remover: Button = $UI_Layer/BottomBar/HBox/BotaoRemover
@onready var panel_intro: Panel = $UI_Layer/PanelIntro

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	panel_vitoria.visible = false
	panel_derrota.visible = false
	panel_notificacao.visible = false
	panel_intro.visible = true
	get_tree().paused = true
	label_bioma.text = "🌴 Floresta Tropical"
	label_objetivo.text = "Elimine invasoras | plantas≥4, herbívoros≥2, carnívoros≥1 | 60s"
	GameManager.pontos_atualizados.connect(_on_pontos_atualizados)
	atualizar_ui()

func _process(delta: float) -> void:
	if fase_completa or fase_falhou or intro_ativa:
		return
	tempo_total += delta
	renda_timer += delta
	if renda_timer >= 10.0:
		renda_timer = 0.0
		gerar_renda()
	if notificacao_timer > 0.0:
		notificacao_timer -= delta
		if notificacao_timer <= 0.0:
			panel_notificacao.visible = false
	if not invasora_apareceu and tempo_total >= 35.0:
		spawnar_invasoras()
	verificar_equilibrio(delta)
	verificar_derrota()
	atualizar_ui()

func _unhandled_input(event: InputEvent) -> void:
	if fase_completa or fase_falhou:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1: selecionar_especie("planta")
			KEY_2: selecionar_especie("herbivoro")
			KEY_3: selecionar_especie("carnivoro")
			KEY_4: ativar_remocao()
			KEY_P: toggle_pausa()
			KEY_N: set_velocidade(1.0)
			KEY_R: set_velocidade(3.0)
			KEY_F: set_velocidade(6.0)
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if modo_remocao:
			tentar_remover(event.position)
		else:
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

func tentar_remover(posicao: Vector2) -> void:
	var invasoras: Array = get_tree().get_nodes_in_group("invasoras")
	var mais_perto: Node2D = null
	var menor_dist: float = 60.0
	for inv in invasoras:
		if is_instance_valid(inv):
			var dist: float = posicao.distance_to(inv.global_position)
			if dist < menor_dist:
				menor_dist = dist
				mais_perto = inv
	if mais_perto:
		mais_perto.queue_free()
		GameManager.ganhar_pontos(5)
	else:
		mostrar_notificacao("Clique em uma planta invasora (vermelha) para remover!")

func ativar_remocao() -> void:
	modo_remocao = not modo_remocao
	tipo_selecionado = ""
	botao_planta.button_pressed = false
	botao_herbivoro.button_pressed = false
	botao_carnivoro.button_pressed = false
	botao_remover.button_pressed = modo_remocao
	if modo_remocao:
		mostrar_notificacao("Modo remoção: clique nas invasoras para eliminá-las!")

func spawnar_invasoras() -> void:
	invasora_apareceu = true
	for i in range(3):
		var inv: Node = INVASORA_CENA.instantiate()
		inv.position = Vector2(randf_range(240.0, 1050.0), randf_range(60.0, 580.0))
		organismos.add_child(inv)
	mostrar_notificacao("⚠️ ALERTA: Espécie invasora detectada! Use [4] ou botão Remover para eliminá-las!")

func verificar_equilibrio(delta: float) -> void:
	var n_p: int = get_tree().get_nodes_in_group("comida").size()
	var n_h: int = get_tree().get_nodes_in_group("herbivoros").size()
	var n_c: int = get_tree().get_nodes_in_group("carnivoros").size()
	var n_inv: int = get_tree().get_nodes_in_group("invasoras").size()
	var sem_invasoras: bool = invasora_apareceu and n_inv == 0
	if sem_invasoras and not invasora_eliminada:
		invasora_eliminada = true
		mostrar_notificacao("✅ Invasoras eliminadas! Mantenha o equilíbrio por 60s!")
		GameManager.ganhar_pontos(25)
	var equilibrado: bool = n_p >= 4 and n_h >= 2 and n_c >= 1 and (not invasora_apareceu or sem_invasoras)
	if equilibrado:
		tempo_equilibrio += delta
		if tempo_equilibrio >= TEMPO_META:
			vitoria()
	else:
		tempo_equilibrio = max(0.0, tempo_equilibrio - delta * 0.5)

func verificar_derrota() -> void:
	var n_inv: int = get_tree().get_nodes_in_group("invasoras").size()
	if n_inv >= LIMITE_INVASORAS:
		derrota("As invasoras tomaram conta do bioma!")

func gerar_renda() -> void:
	var n_total: int = get_tree().get_nodes_in_group("comida").size() + \
		get_tree().get_nodes_in_group("herbivoros").size() + \
		get_tree().get_nodes_in_group("carnivoros").size()
	GameManager.ganhar_pontos(max(1, n_total / 3))

func vitoria() -> void:
	if fase_completa: return
	fase_completa = true
	get_tree().paused = true
	panel_vitoria.visible = true
	GameManager.completar_bioma(2)

func derrota(motivo: String) -> void:
	if fase_falhou: return
	fase_falhou = true
	get_tree().paused = true
	label_notificacao.text = motivo
	panel_derrota.visible = true

func mostrar_notificacao(texto: String) -> void:
	label_notificacao.text = texto
	panel_notificacao.visible = true
	notificacao_timer = 4.0

func atualizar_ui() -> void:
	var n_p: int = get_tree().get_nodes_in_group("comida").size()
	var n_h: int = get_tree().get_nodes_in_group("herbivoros").size()
	var n_c: int = get_tree().get_nodes_in_group("carnivoros").size()
	var n_inv: int = get_tree().get_nodes_in_group("invasoras").size()
	label_pontos.text = "🌿 %d BD" % GameManager.pontos_biodiversidade
	label_equilibrio_tempo.text = "Equilíbrio: %.0f/%.0fs" % [tempo_equilibrio, TEMPO_META]
	label_plantas.text = "🌴 Plantas: %d" % n_p
	label_herbivoros.text = "🦌 Herbívoros: %d" % n_h
	label_carnivoros.text = "🐆 Carnívoros: %d" % n_c
	label_invasoras.text = "☠️ Invasoras: %d/%d" % [n_inv, LIMITE_INVASORAS]
	barra_equilibrio.value = (tempo_equilibrio / TEMPO_META) * 100.0

func selecionar_especie(esp: String) -> void:
	tipo_selecionado = esp
	modo_remocao = false
	botao_planta.button_pressed = (esp == "planta")
	botao_herbivoro.button_pressed = (esp == "herbivoro")
	botao_carnivoro.button_pressed = (esp == "carnivoro")
	botao_remover.button_pressed = false

func toggle_pausa() -> void: get_tree().paused = not get_tree().paused
func set_velocidade(v: float) -> void: Engine.time_scale = v; get_tree().paused = false
func _on_pontos_atualizados(_p: int) -> void: atualizar_ui()
func _on_botao_planta_pressed() -> void: selecionar_especie("planta")
func _on_botao_herbivoro_pressed() -> void: selecionar_especie("herbivoro")
func _on_botao_carnivoro_pressed() -> void: selecionar_especie("carnivoro")
func _on_botao_remover_pressed() -> void: ativar_remocao()
func _on_botao_pausar_pressed() -> void: toggle_pausa()
func _on_botao_normal_pressed() -> void: set_velocidade(1.0)
func _on_botao_rapido_pressed() -> void: set_velocidade(3.0)
func _on_botao_muito_rapido_pressed() -> void: set_velocidade(6.0)

func _on_botao_mapa_pressed() -> void:
	get_tree().paused = false; Engine.time_scale = 1.0
	get_tree().change_scene_to_file("res://scenes/mapa_mundo.tscn")

func _on_botao_vitoria_continuar_pressed() -> void:
	get_tree().paused = false; Engine.time_scale = 1.0
	get_tree().change_scene_to_file("res://scenes/mapa_mundo.tscn")

func _on_botao_derrota_reiniciar_pressed() -> void:
	get_tree().paused = false; Engine.time_scale = 1.0
	get_tree().reload_current_scene()

func _on_botao_notificacao_ok_pressed() -> void:
	panel_notificacao.visible = false; notificacao_timer = 0.0

func _on_botao_intro_comecar_pressed() -> void:
	intro_ativa = false
	panel_intro.visible = false
	get_tree().paused = false
