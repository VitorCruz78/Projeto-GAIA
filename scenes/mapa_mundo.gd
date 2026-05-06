extends Control

@onready var botao_bioma1: Button = $Panel/VBox/BiomaBtns/BotaoBioma1
@onready var botao_bioma2: Button = $Panel/VBox/BiomaBtns/BotaoBioma2
@onready var botao_bioma3: Button = $Panel/VBox/BiomaBtns/BotaoBioma3
@onready var label_pontos: Label = $Panel/TopHBox/LabelPontos
@onready var label_status: Label = $Panel/VBox/LabelStatus

func _ready() -> void:
	GameManager.bioma_completo.connect(_on_bioma_completo)
	GameManager.pontos_atualizados.connect(_on_pontos_atualizados)
	atualizar_estado()

func atualizar_estado() -> void:
	botao_bioma1.text = ("✓ " if GameManager.bioma_concluido[0] else "") + "🌲 Floresta Temperada\n[DESBLOQUEADO]"
	botao_bioma2.disabled = not GameManager.is_bioma_desbloqueado(2)
	botao_bioma2.text = ("✓ " if GameManager.bioma_concluido[1] else "") + "🌴 Floresta Tropical\n" + ("[DESBLOQUEADO]" if GameManager.is_bioma_desbloqueado(2) else "[BLOQUEADO]")
	botao_bioma3.disabled = not GameManager.is_bioma_desbloqueado(3)
	botao_bioma3.text = ("✓ " if GameManager.bioma_concluido[2] else "") + "🌵 Deserto\n" + ("[DESBLOQUEADO]" if GameManager.is_bioma_desbloqueado(3) else "[BLOQUEADO]")
	label_pontos.text = "Pontos de Biodiversidade: %d" % GameManager.pontos_biodiversidade

	var concluidos: int = GameManager.bioma_concluido.count(true)
	if concluidos == 3:
		label_status.text = "🎉 Todos os biomas restaurados! Gaia agradece!"
	elif concluidos == 0:
		label_status.text = "Selecione um bioma para começar a restauração."
	else:
		label_status.text = "Biomas restaurados: %d/3. Continue a jornada!" % concluidos

func _on_bioma_completo(_bioma_id: int) -> void:
	atualizar_estado()

func _on_pontos_atualizados(_pontos: int) -> void:
	label_pontos.text = "Pontos de Biodiversidade: %d" % GameManager.pontos_biodiversidade

func _on_botao_bioma1_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/fase_1_floresta.tscn")

func _on_botao_bioma2_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/fase_2_tropical.tscn")

func _on_botao_bioma3_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/fase_3_deserto.tscn")

func _on_botao_menu_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/menu_principal.tscn")

func _on_botao_codice_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/codice_gaia.tscn")
