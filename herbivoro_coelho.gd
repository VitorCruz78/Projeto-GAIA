extends Area2D

@export var velocidade: float = 80.0
var alvo_comida = null

func _ready():
	add_to_group("herbivoros")
	escolher_alvo()

func _process(delta):
	if alvo_comida and is_instance_valid(alvo_comida):
		# Move o coelho em direção à planta
		var direcao = (alvo_comida.global_position - global_position).normalized()
		global_position += direcao * velocidade * delta
		
		# Se chegar muito perto, "come" a planta
		if global_position.distance_to(alvo_comida.global_position) < 10:
			comer()
	else:
		escolher_alvo()

func escolher_alvo():
	# Procura todas as plantas na cena
	var plantas = get_tree().get_nodes_in_group("comida")
	if plantas.size() > 0:
		alvo_comida = plantas[0] # Foca na primeira planta que encontrar

func comer():
	alvo_comida.queue_free() # Remove a planta do jogo
	alvo_comida = null
	print("O herbívoro comeu uma planta!")
