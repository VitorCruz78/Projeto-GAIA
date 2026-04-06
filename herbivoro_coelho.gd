extends Area2D

const LIMITE_X_MIN: float = 20.0
const LIMITE_X_MAX: float = 1132.0
const LIMITE_Y_MIN: float = 20.0
const LIMITE_Y_MAX: float = 628.0

@export var velocidade: float = 80.0
@export var velocidade_vagando_fator: float = 0.4
@export var fome_maxima: float = 20.0

var alvo_comida: Node2D = null
var fome: float = 0.0
var direcao_vagando: Vector2 = Vector2.ZERO
var tempo_troca_direcao: float = 0.0

func _ready() -> void:
	add_to_group("herbivoros")
	direcao_vagando = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)).normalized()
	tempo_troca_direcao = randf_range(1.0, 3.0)
	escolher_alvo()

func _process(delta: float) -> void:
	fome += delta
	if fome >= fome_maxima:
		morrer()
		return

	if alvo_comida and is_instance_valid(alvo_comida):
		var direcao: Vector2 = (alvo_comida.global_position - global_position).normalized()
		global_position += direcao * velocidade * delta
		if global_position.distance_to(alvo_comida.global_position) < 15.0:
			comer()
	else:
		escolher_alvo()
		_vagar(delta)

func _vagar(delta: float) -> void:
	tempo_troca_direcao -= delta
	if tempo_troca_direcao <= 0.0:
		direcao_vagando = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)).normalized()
		tempo_troca_direcao = randf_range(1.5, 4.0)

	global_position += direcao_vagando * (velocidade * velocidade_vagando_fator) * delta
	# Mantém o herbívoro dentro dos limites do cenário
	global_position.x = clampf(global_position.x, LIMITE_X_MIN, LIMITE_X_MAX)
	global_position.y = clampf(global_position.y, LIMITE_Y_MIN, LIMITE_Y_MAX)

func escolher_alvo() -> void:
	var plantas: Array = get_tree().get_nodes_in_group("comida")
	if plantas.is_empty():
		alvo_comida = null
		return

	var mais_perto: Node2D = null
	var menor_distancia: float = INF
	for planta in plantas:
		if is_instance_valid(planta):
			var dist: float = global_position.distance_to(planta.global_position)
			if dist < menor_distancia:
				menor_distancia = dist
				mais_perto = planta
	alvo_comida = mais_perto

func comer() -> void:
	fome = 0.0
	if alvo_comida and is_instance_valid(alvo_comida):
		alvo_comida.queue_free()
	alvo_comida = null

func morrer() -> void:
	queue_free()
