extends Node

signal pontos_atualizados(pontos: int)
signal bioma_completo(bioma_id: int)
signal especie_desbloqueada(especie_id: String)

var pontos_biodiversidade: int = 150
var biomas_desbloqueados: Array[int] = [1]
var bioma_concluido: Array[bool] = [false, false, false]
var paginas_codice: Array[String] = []
var especies_desbloqueadas: Array[String] = ["planta_carvalho", "herbivoro_coelho"]

func ganhar_pontos(qtd: int) -> void:
	pontos_biodiversidade += qtd
	pontos_atualizados.emit(pontos_biodiversidade)

func gastar_pontos(qtd: int) -> bool:
	if pontos_biodiversidade >= qtd:
		pontos_biodiversidade -= qtd
		pontos_atualizados.emit(pontos_biodiversidade)
		return true
	return false

func completar_bioma(bioma_id: int) -> void:
	if bioma_id >= 1 and bioma_id <= 3:
		bioma_concluido[bioma_id - 1] = true
		if bioma_id < 3 and not (bioma_id + 1) in biomas_desbloqueados:
			biomas_desbloqueados.append(bioma_id + 1)
		bioma_completo.emit(bioma_id)
	if bioma_id == 1:
		desbloquear_especie("planta_palmeira")
		desbloquear_especie("herbivoro_gazela")
		desbloquear_especie("carnivoro_lobo")
		ganhar_pontos(50)
	elif bioma_id == 2:
		desbloquear_especie("planta_cactus")
		desbloquear_especie("herbivoro_lagartixa")
		desbloquear_especie("carnivoro_onca")
		ganhar_pontos(75)
	elif bioma_id == 3:
		desbloquear_especie("carnivoro_serpente")
		ganhar_pontos(100)

func desbloquear_especie(especie_id: String) -> void:
	if especie_id not in especies_desbloqueadas:
		especies_desbloqueadas.append(especie_id)
		especie_desbloqueada.emit(especie_id)

func desbloquear_pagina_codice(pagina: String) -> void:
	if pagina not in paginas_codice:
		paginas_codice.append(pagina)

func is_bioma_desbloqueado(bioma_id: int) -> bool:
	return bioma_id in biomas_desbloqueados
