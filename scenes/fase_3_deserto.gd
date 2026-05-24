extends Node2D

const PLANTA_CENA = preload("res://organismos/planta_cactus.tscn")
const HERBIVORO_CENA = preload("res://organismos/herbivoro_lagartixa.tscn")
const CARNIVORO_CENA = preload("res://organismos/carnivoro_serpente.tscn")

const CUSTO_PLANTA: int = 10
const CUSTO_HERBIVORO: int = 25
const CUSTO_CARNIVORO: int = 50
const CUSTO_EVOLUCAO: int = 40

var tipo_selecionado: String = ""
var tempo_total: float = 0.0
var fase_completa: bool = false
var fase_falhou: bool = false
var intro_ativa: bool = true
var renda_timer: float = 0.0
var notificacao_timer: float = 0.0
var secas_sobrevividas: int = 0
var seca_ativa: bool = false
var seca_timer: float = 0.0
var seca_duracao: float = 20.0
var proxima_seca: float = 25.0
var segunda_seca_programada: bool = false
var evolutiou: bool = false

@onready var organismos: Node2D = $Organismos
@onready var label_pontos: Label = $UI_Layer/TopBar/HBox/LabelPontos
@onready var label_bioma: Label = $UI_Layer/TopBar/HBox/LabelBioma
@onready var label_objetivo: Label = $UI_Layer/TopBar/HBox/LabelObjetivo
@onready var label_equilibrio_tempo: Label = $UI_Layer/TopBar/HBox/LabelEquilibrioTempo
@onready var label_plantas: Label = $UI_Layer/LeftPanel/VBox/LabelPlantas
@onready var label_herbivoros: Label = $UI_Layer/LeftPanel/VBox/LabelHerbivoros
@onready var label_carnivoros: Label = $UI_Layer/LeftPanel/VBox/LabelCarnivoros
@onready var barra_equilibrio: ProgressBar = $UI_Layer/LeftPanel/VBox/BarraEquilibrio
@onready var label_secas: Label = $UI_Layer/LeftPanel/VBox/LabelEstacao
@onready var panel_vitoria: Panel = $UI_Layer/PanelVitoria
@onready var panel_derrota: Panel = $UI_Layer/PanelDerrota
@onready var panel_notificacao: Panel = $UI_Layer/PanelNotificacao
@onready var label_notificacao: Label = $UI_Layer/PanelNotificacao/VBox/LabelNotificacao
@onready var botao_planta: Button = $UI_Layer/BottomBar/HBox/BotaoPlanta
@onready var botao_herbivoro: Button = $UI_Layer/BottomBar/HBox/BotaoHerbivoro
@onready var botao_carnivoro: Button = $UI_Layer/BottomBar/HBox/BotaoCarnivoro
@onready var botao_evolucao: Button = $UI_Layer/BottomBar/HBox/BotaoRemover
@onready var panel_intro: Panel = $UI_Layer/PanelIntro

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	panel_vitoria.visible = false
	panel_derrota.visible = false
	panel_notificacao.visible = false
	panel_intro.visible = true
	get_tree().paused = true
	label_bioma.text = "🌵 Deserto"
	label_objetivo.text = "Sobreviva a 2 secas | plantas≥2, herbívoros≥2, carnívoros≥1"
	if botao_evolucao:
		botao_evolucao.text = "🧬 Evoluir\n(40BD)"
	GameManager.pontos_atualizados.connect(_on_pontos_atualizados)
	atualizar_ui()

func _process(delta: float) -> void:
	if fase_completa or fase_falhou or intro_ativa:
		return
	tempo_total += delta
	renda_timer += delta
	if renda_timer >= 12.0:
		renda_timer = 0.0
		gerar_renda()
	if notificacao_timer > 0.0:
		notificacao_timer -= delta
		if notificacao_timer <= 0.0:
			panel_notificacao.visible = false
	processar_secas(delta)
	verificar_derrota()
	atualizar_ui()

func processar_secas(delta: float) -> void:
	if seca_ativa:
		seca_timer += delta
		if seca_timer >= seca_duracao:
			terminar_seca()
	else:
		if tempo_total >= proxima_seca and secas_sobrevividas < 2:
			iniciar_seca()

func iniciar_seca() -> void:
	seca_ativa = true
	seca_timer = 0.0
	var intensidade: float = 0.0 if evolutiou else 1.0
	for planta in get_tree().get_nodes_in_group("plantas"):
		if planta.has_method("aplicar_seca"):
			planta.aplicar_seca(true)
	mostrar_notificacao("🌡️ SECA INTENSA! As plantas crescem mais devagar. %s" % ("Evolução reduz o impacto!" if evolutiou else ""))

func terminar_seca() -> void:
	seca_ativa = false
	secas_sobrevividas += 1
	for planta in get_tree().get_nodes_in_group("plantas"):
		if planta.has_method("aplicar_seca"):
			planta.aplicar_seca(false)
	mostrar_notificacao("💧 Chuva! Seca terminada. Secas sobrevividas: %d/2" % secas_sobrevividas)
	if secas_sobrevividas == 1 and not segunda_seca_programada:
		segunda_seca_programada = true
		proxima_seca = tempo_total + 45.0
	elif secas_sobrevividas >= 2:
		verificar_vitoria()

func verificar_vitoria() -> void:
	var n_p: int = get_tree().get_nodes_in_group("comida").size()
	var n_h: int = get_tree().get_nodes_in_group("herbivoros").size()
	var n_c: int = get_tree().get_nodes_in_group("carnivoros").size()
	if n_p >= 2 and n_h >= 2 and n_c >= 1:
		vitoria()
	else:
		derrota("O ecossistema não resistiu às secas!")

func verificar_derrota() -> void:
	if seca_ativa:
		var n_p: int = get_tree().get_nodes_in_group("comida").size()
		var n_h: int = get_tree().get_nodes_in_group("herbivoros").size()
		if n_p == 0 or n_h == 0:
			derrota("O ecossistema colapsou durante a seca!")

func evoluir_especies() -> void:
	if evolutiou:
		mostrar_notificacao("Espécies já foram evoluídas!")
		return
	if not GameManager.gastar_pontos(CUSTO_EVOLUCAO):
		mostrar_notificacao("Pontos insuficientes para evolução (40 BD)!")
		return
	evolutiou = true
	for planta in get_tree().get_nodes_in_group("plantas"):
		if "resistencia_seca" in planta:
			planta.resistencia_seca = 1.0
	for herb in get_tree().get_nodes_in_group("herbivoros"):
		if "resistencia_seca" in herb:
			herb.resistencia_seca = 1.0
	for carn in get_tree().get_nodes_in_group("carnivoros"):
		if "resistencia_seca" in carn:
			carn.resistencia_seca = 1.0
	if botao_evolucao:
		botao_evolucao.text = "✅ Evoluído!"
		botao_evolucao.disabled = true
	mostrar_notificacao("🧬 Evolução concluída! Espécies mais resistentes à seca!")
	GameManager.desbloquear_pagina_codice("evolucao_deserto")

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

func gerar_renda() -> void:
	var n_total: int = get_tree().get_nodes_in_group("comida").size() + \
		get_tree().get_nodes_in_group("herbivoros").size() + \
		get_tree().get_nodes_in_group("carnivoros").size()
	GameManager.ganhar_pontos(max(1, n_total / 4))

func vitoria() -> void:
	if fase_completa: return
	fase_completa = true
	get_tree().paused = true
	panel_vitoria.visible = true
	GameManager.completar_bioma(3)

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
	label_pontos.text = "🌿 %d BD" % GameManager.pontos_biodiversidade
	label_equilibrio_tempo.text = "Secas: %d/2%s" % [secas_sobrevividas, " | SECA ATIVA!" if seca_ativa else ""]
	label_plantas.text = "🌵 Plantas: %d" % n_p
	label_herbivoros.text = "🦎 Herbívoros: %d" % n_h
	label_carnivoros.text = "🐍 Carnívoros: %d" % n_c
	label_secas.text = "🌡️ SECA (%.0fs)" % (seca_duracao - seca_timer) if seca_ativa else "☀️ Aguardando seca"
	barra_equilibrio.value = (float(secas_sobrevividas) / 2.0) * 100.0

func selecionar_especie(esp: String) -> void:
	tipo_selecionado = esp
	botao_planta.button_pressed = (esp == "planta")
	botao_herbivoro.button_pressed = (esp == "herbivoro")
	botao_carnivoro.button_pressed = (esp == "carnivoro")

func toggle_pausa() -> void: get_tree().paused = not get_tree().paused
func set_velocidade(v: float) -> void: Engine.time_scale = v; get_tree().paused = false
func _on_pontos_atualizados(_p: int) -> void: atualizar_ui()
func _on_botao_planta_pressed() -> void: selecionar_especie("planta")
func _on_botao_herbivoro_pressed() -> void: selecionar_especie("herbivoro")
func _on_botao_carnivoro_pressed() -> void: selecionar_especie("carnivoro")
func _on_botao_remover_pressed() -> void: evoluir_especies()
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
