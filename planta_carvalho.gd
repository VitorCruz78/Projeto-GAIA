extends Area2D

@export var custo_biodiversidade: int = 10
@export var tipo: String = "Produtor"
@export var intervalo_crescimento: float = 14.0
@export var max_plantas: int = 20
@export var resistencia_seca: float = 0.0

var tempo_crescimento: float = 0.0
var idade: float = 0.0

func _ready():
	add_to_group("comida")
	add_to_group("plantas")
	tempo_crescimento = randf_range(10.0, intervalo_crescimento)

func _process(delta: float) -> void:
	idade += delta
	tempo_crescimento -= delta
	if tempo_crescimento <= 0.0:
		espalhar()
		tempo_crescimento = intervalo_crescimento

func espalhar() -> void:
	if get_tree().get_nodes_in_group("comida").size() >= max_plantas:
		return
	var nova: Node = load(scene_file_path).instantiate()
	var offset: Vector2 = Vector2(randf_range(-80.0, 80.0), randf_range(-80.0, 80.0))
	nova.position = position + offset
	nova.position.x = clampf(nova.position.x, 20.0, 1132.0)
	nova.position.y = clampf(nova.position.y, 20.0, 628.0)
	get_parent().add_child(nova)
