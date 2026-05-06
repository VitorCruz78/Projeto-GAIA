extends Control

func _ready() -> void:
	$Panel/VBox/LabelTitulo.text = "PROJETO GAIA"

func _on_botao_novo_jogo_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/cutscene_intro.tscn")

func _on_botao_codice_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/codice_gaia.tscn")

func _on_botao_sair_pressed() -> void:
	get_tree().quit()
