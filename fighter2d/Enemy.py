## Enemy
## Clase que implementa un tipo de enemigo
##
## Author: Santiago Faci
## Version: 2.0

from direct.showbase.DirectObject import DirectObject
import random

VELOCIDAD = -4
VELOCIDAD_MISIL = 10
Y = 55
FRECUENCIA_DISPARO = 0.2
PUNTOS = 100
VIDA = 2

class Enemy(DirectObject):
	def __init__(self, x0, z0, modelo):
		
		self.ship = loader.loadModel(modelo)
		self.ship.setTransparency(1)
		self.ship.setPos(x0, Y, z0)
		self.ship.setScale(2, 1, 1.5)
		self.ship.reparentTo(camera)

		self.ia = False
		self.vida = VIDA
		self.puntos = PUNTOS
		self.velocidad = VELOCIDAD

	# Destructor del objeto
	def __del__(self):
		pass;