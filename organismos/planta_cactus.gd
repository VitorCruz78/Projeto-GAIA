extends Area2D

@export var custo_biodiversidade: int = 10
@export var tipo: String = "Produtor"
@export var intervalo_crescimento: float = 22.0
@export var max_plantas: int = 20
@export var resistencia_seca: float = 1.0

var tempo_crescimento: float = 0.0
var em_seca: bool = false

func _ready():
	add_to_group("comida")
	add_to_group("plantas")
	tempo_crescimento = randf_range(15.0, intervalo_crescimento)

func _process(delta: float) -> void:
	var intervalo_atual: float = intervalo_crescimento * (3.0 if em_seca and resistencia_seca < 0.5 else 1.0)
	tempo_crescimento -= delta
	if tempo_crescimento <= 0.0:
		espalhar()
		tempo_crescimento = intervalo_atual

func espalhar() -> void:
	if get_tree().get_nodes_in_group("comida").size() >= max_plantas:
		return
	var nova: Node = load(scene_file_path).instantiate()
	var offset: Vector2 = Vector2(randf_range(-60.0, 60.0), randf_range(-60.0, 60.0))
	nova.position = position + offset
	nova.position.x = clampf(nova.position.x, 20.0, 1132.0)
	nova.position.y = clampf(nova.position.y, 20.0, 628.0)
	get_parent().add_child(nova)

func aplicar_seca(ativa: bool) -> void:
	em_seca = ativa
