## BigEnemy
## Clase que implementa un tipo de enemigo mas grande y resistente
##
## Author: Santiago Faci
## Version: 2.0

from direct.showbase.DirectObject import DirectObject
import random

from Enemy import Enemy

VELOCIDAD = -2
VELOCIDAD_MISIL = 10
Y = 55
FRECUENCIA_DISPARO = 0.2
PUNTOS = 200
VIDA = 4

class BigEnemy(Enemy):
	def __init__(self, x0, z0, modelo):
		
		# Invoca al constructor de la clase base
		Enemy.__init__(self, x0, z0, modelo)

		# Inicializa algunos atributos con valores diferentes
		self.ship.setScale(4, 1, 3)
		self.ia = False
		self.vida = VIDA
		self.puntos = PUNTOS
		self.velocidad = VELOCIDAD

	# Destructor del objeto
	def __del__(self):
		pass;