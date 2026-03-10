extends Node2D

const PLANTA_CENA = preload("res://planta_carvalho.tscn")
const HERBIVORO_CENA = preload("res://herbivoro_coelho.tscn") # Nova linha

var tipo_selecionado = "planta" # Variável para saber o que colocar
var pontos_biodiversidade: int = 100

func _input(event):
	# Alternar seleção
	if Input.is_key_pressed(KEY_1): tipo_selecionado = "planta"
	if Input.is_key_pressed(KEY_2): tipo_selecionado = "herbivoro"

	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		spawn_organismo(event.position)

func spawn_organismo(posicao):
	var nova_instancia = null
	var custo = 0
	
	if tipo_selecionado == "planta":
		nova_instancia = PLANTA_CENA.instantiate()
		custo = 10
	elif tipo_selecionado == "herbivoro":
		nova_instancia = HERBIVORO_CENA.instantiate()
		custo = 25 # Herbívoros são mais caros no GDD
	
	if pontos_biodiversidade >= custo:
		pontos_biodiversidade -= custo
		nova_instancia.position = posicao
		$Organismos.add_child(nova_instancia)
		print("Criado: ", tipo_selecionado, " | Pontos: ", pontos_biodiversidade)
