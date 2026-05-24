extends Area2D

const LIMITE_X_MIN: float = 20.0
const LIMITE_X_MAX: float = 1132.0
const LIMITE_Y_MIN: float = 20.0
const LIMITE_Y_MAX: float = 628.0

@export var velocidade: float = 100.0
@export var velocidade_vagando_fator: float = 0.45
@export var fome_maxima: float = 65.0
@export var intervalo_reproducao: float = 18.0

var alvo_comida: Node2D = null
var fome: float = randf_range(0.0, 6.0)
var direcao_vagando: Vector2 = Vector2.ZERO
var tempo_troca_direcao: float = 0.0
var tempo_reproducao: float = 0.0

func _ready() -> void:
	add_to_group("herbivoros")
	direcao_vagando = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)).normalized()
	tempo_troca_direcao = randf_range(1.0, 3.0)
	tempo_reproducao = randf_range(8.0, intervalo_reproducao)
	escolher_alvo()

func _process(delta: float) -> void:
	fome += delta
	if fome >= fome_maxima:
		morrer()
		return
	tempo_reproducao -= delta
	if tempo_reproducao <= 0.0 and fome < fome_maxima * 0.4:
		reproduzir()
		tempo_reproducao = intervalo_reproducao
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
	global_position.x = clampf(global_position.x, LIMITE_X_MIN, LIMITE_X_MAX)
	global_position.y = clampf(global_position.y, LIMITE_Y_MIN, LIMITE_Y_MAX)

func escolher_alvo() -> void:
	if fome < fome_maxima * 0.4:
		alvo_comida = null
		return
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

func reproduzir() -> void:
	if get_tree().get_nodes_in_group("herbivoros").size() >= 15:
		return
	var filhote: Node = load(scene_file_path).instantiate()
	filhote.position = position + Vector2(randf_range(-40.0, 40.0), randf_range(-40.0, 40.0))
	filhote.fome = fome_maxima * 0.2
	get_parent().add_child(filhote)

func morrer() -> void:
	queue_free()
