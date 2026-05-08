extends Area2D

@export var intervalo_crescimento: float = 6.0
@export var max_invasoras: int = 25

var tempo_crescimento: float = 0.0

func _ready():
	add_to_group("comida")
	add_to_group("plantas")
	add_to_group("invasoras")
	tempo_crescimento = randf_range(3.0, intervalo_crescimento)

func _process(delta: float) -> void:
	tempo_crescimento -= delta
	if tempo_crescimento <= 0.0:
		espalhar()
		tempo_crescimento = intervalo_crescimento

func espalhar() -> void:
	if get_tree().get_nodes_in_group("invasoras").size() >= max_invasoras:
		return
	var nova: Node = load(scene_file_path).instantiate()
	var offset: Vector2 = Vector2(randf_range(-70.0, 70.0), randf_range(-70.0, 70.0))
	nova.position = position + offset
	nova.position.x = clampf(nova.position.x, 20.0, 1132.0)
	nova.position.y = clampf(nova.position.y, 20.0, 628.0)
	get_parent().add_child(nova)

func remover() -> void:
	queue_free()
