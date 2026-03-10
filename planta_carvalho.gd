extends Area2D

# Variáveis baseadas no GDD para a Fase 1
@export var custo_biodiversidade: int = 10
@export var tipo: String = "Produtor"

func _ready():
	# Isso facilita para o Herbívoro saber que isso é comida
	add_to_group("comida")
