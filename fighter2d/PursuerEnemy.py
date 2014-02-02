## PursuerEnemy
## Clase que implementa un tipo de enemigo que persigue al jugador
##
## Author: Santiago Faci
## Version: 1.0

from direct.showbase.DirectObject import DirectObject
import random

from Enemy import Enemy

VELOCIDAD = -2
VELOCIDAD_MISIL = 10
Y = 55
FRECUENCIA_DISPARO = 0.2
PUNTOS = 150
VIDA = 2

class PursuerEnemy(Enemy):
	def __init__(self, x0, z0, modelo):
		
		# Invoca al constructor de la clase base
		Enemy.__init__(self, x0, z0, modelo)

		# Inicializa algunos atributos con valores diferentes
		self.ship.setScale(0.07, 0.07, 0.07)
		self.ia = True
		self.vida = VIDA
		self.puntos = PUNTOS
		self.velocidad = VELOCIDAD

	# Destructor del objeto
	def __del__(self):
		pass;