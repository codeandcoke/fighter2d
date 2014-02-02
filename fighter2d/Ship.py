## Ship
## Clase que implementa la nave y algunos de sus movimientos
##
## Author: Santiago Faci
## Version: 3.0

from direct.showbase.DirectObject import DirectObject
from panda3d.ai import *
import random
import sys

from Enemy import Enemy
from BigEnemy import BigEnemy
from PursuerEnemy import PursuerEnemy

VELOCIDAD_NAVE = 6
VELOCIDAD_MISIL = 10
VELOCIDAD_ENEMIGO = -4
Y = 55
FRECUENCIA_DISPARO = 0.2
PUNTOS_DERRIBO = 100
VIDAS_INICIALES = 5

class Ship(DirectObject):
	def __init__(self, inputManager):
		self.inputManager = inputManager

		self.ship = loader.loadModel("models/Ship/ship")
		self.ship.setPos(0, Y, 0)
		self.ship.setScale(3, 1, 1.5)
		self.ship.reparentTo(camera)
		self.ship.setTransparency(1)

		self.tareaMover = taskMgr.add(self.mover, "Mover Nave")
		self.tareaMover.proximoDisparo = 0

		taskMgr.doMethodLater(0.5, self.generarEnemigos, "Generar Enemigos")
		taskMgr.add(self.comprobarImpactos, "Comprobar Impactos")

		self.misiles = []
		self.enemigos = []

		self.puntos = 0
		self.vida = VIDAS_INICIALES
		self.proximoMonstruo = 5
		self.terminarPartida = False

		# Inicializa la IA y lanza un NPC (Non Player Character)
		# que persigue al usuario
		self.mundoIA = None
		self.inicializarIA()

		# Carga otros recursos del juego
		self.cargarSonidos()
		self.cargarRecursos()

	# Actualiza la posicion de los elementos del juego: nave, misiles y enemigos
	def mover(self, tarea):

		dt = globalClock.getDt()
		if (dt > 0.20):
		    return tarea.cont

		# Actualiza la posicion de la nave
		if (self.inputManager.keyMap["up"]):
			self.ship.setZ(self.ship, VELOCIDAD_NAVE * dt)

		if (self.inputManager.keyMap["down"]):
			self.ship.setZ(self.ship, - VELOCIDAD_NAVE * dt)

		if (self.inputManager.keyMap["left"]):
			self.ship.setX(self.ship, - VELOCIDAD_NAVE * dt)

		if (self.inputManager.keyMap["right"]):
			self.ship.setX(self.ship, VELOCIDAD_NAVE * dt)

		# Dispara un misil si ha pasado el tiempo entre disparos sucesivos
		if (self.inputManager.keyMap["fire"]):
			if (tarea.time > tarea.proximoDisparo):
				misil = loader.loadModel("models/plane")
				misil.setTexture(loader.loadTexture("models/bullet.png"))
				misil.setPos(self.ship.getX() + 1, Y, self.ship.getZ())
				misil.reparentTo(camera)
				misil.setTransparency(1)
				misil.setTag("eliminar", str(0))
				self.misiles.append(misil)

				self.sonidoDisparo.play()

				tarea.proximoDisparo = tarea.time + FRECUENCIA_DISPARO

		# Actualiza la posicion de los misiles disparados
		for misil in self.misiles:
			misil.setX(misil, VELOCIDAD_MISIL * dt)

		# Actualiza la posicion de los enemigos
		for enemigo in self.enemigos:
			# Los enemigos con IA se mueven solos, no hay que calcular
			# su posicion
			if (enemigo.ia == False):
				enemigo.ship.setX(enemigo.ship, enemigo.velocidad * dt)
				enemigo.ship.setZ(enemigo.ship, random.uniform(-1, 3) * dt)

		self.comprobarVisibilidad()

		# Comprueba los choques del jugador con otros elementos del juego
		self.comprobarDanos()

		return tarea.cont

	# Comprueba choques con naves enemigas
	def comprobarDanos(self):
		for i in range(len(self.enemigos) - 1, -1, -1):
			if ((self.ship.getPos() - self.enemigos[i].ship.getPos()).lengthSquared() < 
					(((self.ship.getScale().getX() + self.enemigos[i].ship.getScale().getX()) * 0.5) ** 2)):

				self.vida -= 1
				self.sonidoDano.play()
				self.eliminarEnemigo(i)

		if (self.vida == 0):
			self.terminarPartida = True

	# Comprueba que elementos ya no son visibles en el juego, y los elimina
	def comprobarVisibilidad(self):
		for i in range(len(self.misiles) - 1, -1, -1):
			if (self.esVisible(self.misiles[i]) == False):
				self.eliminarMisil(i)

		for i in range(len(self.enemigos) - 1, -1, -1):
			if (self.esVisible(self.enemigos[i].ship) == False):
				self.eliminarEnemigo(i)

	# Genera nuevos enemigos aleatoriamente en la pantalla s
	def generarEnemigos(self, tarea):
		enemigo = Enemy(20, random.uniform(-10, 10), "models/Enemy/enemy")
		self.enemigos.append(enemigo)

		# Cada un tiempo determinado aparece un enemigo diferente
		if (globalClock.getRealTime() > self.proximoMonstruo):
			enemigo = BigEnemy(20, random.uniform(-10, 10), "models/Enemy/enemy")
			self.enemigos.append(enemigo)
			self.proximoMonstruo += 5

		return tarea.again

	# Comprueba los impactos de los enemigos con los misiles lanzados por la nave
	def comprobarImpactos(self, tarea):

		if (len(self.enemigos) == 0):
			return tarea.cont
		# Las listas se recorren al reves. De esa manera es posible eliminar elementos directamente 
		# sin problemas con las posiciones
		for m in range(len(self.misiles) - 1, -1, -1):
			for e in range(len(self.enemigos) - 1, -1, -1):
				if ((self.misiles[m].getPos() - self.enemigos[e].ship.getPos()).lengthSquared() < 
					(((self.misiles[m].getScale().getX() + self.enemigos[e].ship.getScale().getX()) * 0.5) ** 2)):

					# Al enemigo solo le queda una vida
					if (self.enemigos[e].vida == 1):

						# Suma los puntos al jugador y emite el sonido de explosion del enemigo
						self.puntos += self.enemigos[e].puntos
						self.sonidoExplosion.play()

						# Elimina del juego misil y enemigo
						self.eliminarEnemigo(e)
						self.eliminarMisil(m)
										
						# Ya no tiene sentido comprobar el resto de enemigos con este misil, se ha eliminado
						break;
					# Todavia no es la ultima vida del enemigo
					# Se le resta vida al enemigo y se elimina el misil
					else:
						self.enemigos[e].vida -= 1
						self.eliminarMisil(m)
						break;

		return tarea.cont

	# Elimina un misil
	def eliminarMisil(self, i):
		self.misiles[i].detachNode()
		self.misiles[i].remove()
		self.misiles = self.misiles[:i] + self.misiles[i + 1:]

	# Elimina un enemigo
	def eliminarEnemigo(self, i):
		
		# Carga la animacion de la explosion
		explosion = loader.loadModel("explosion/explosion")
		explosion.find("**/+SequenceNode").node().loop(1)
		explosion.setPos(self.enemigos[i].ship.getPos())
		explosion.setTransparency(1)
		explosion.setScale(3, 1, 3)
		explosion.reparentTo(render)

		# La tarea controla el tiempo que se muestra la explosion
		taskMgr.add(self.explosionar, "Explosionar", extraArgs = [explosion], 
			appendTask = True)

		self.enemigos[i].ship.detachNode()
		self.enemigos[i].ship.remove()
		self.enemigos = self.enemigos[:i] + self.enemigos[i + 1:]

	# Controla el tiempo que se muestra cada explosion
	def explosionar(self, explosion, tarea):
		
		# Permite que la explosion se muestre durante 1.5 segundos
		if (tarea.frame < 40):
			return tarea.cont
		# Cuando se sobrepasa el tiempo elimina el nodo explosion del juego
		else:
			explosion.detachNode()
			explosion.remove()
			return tarea.done

	# Comprueba si un objeto es visible en la pantalla
	def esVisible(self, objeto):
		limitesCamara = base.cam.node().getLens().makeBounds()
		limites = objeto.getBounds()
		limites.xform(objeto.getParent().getMat(base.cam))
		return limitesCamara.contains(limites)

	# Inicializa la IA generando un enemigo que persigue al personaje
	def inicializarIA(self):
		self.mundoIA = AIWorld(render)
		pursuer = PursuerEnemy(20, random.uniform(-10, 10), "models/pursuer/fighter")
		pursuer.ship.lookAt(self.ship)
		self.personajeIA = AICharacter("pursuer", pursuer.ship, 100, 0.5, 5)
		self.mundoIA.addAiChar(self.personajeIA)
		self.comportamientoIA = self.personajeIA.getAiBehaviors()
		self.comportamientoIA.pursue(self.ship)

		self.enemigos.append(pursuer)

		# Es necesario actualizar la IA durante el juego
		taskMgr.add(self.actualizarIA, "Actualizar IA")

	# Actualiza la IA
	def actualizarIA(self, tarea):
		self.mundoIA.update()
		return tarea.cont

	# Precarga los sonidos del juego
	def cargarSonidos(self):
		self.sonidoDisparo = loader.loadSfx("sounds/disparo.mp3")
		self.sonidoExplosion = loader.loadSfx("sounds/explosion.mp3")
		self.sonidoDano = loader.loadSfx("sounds/buzz.mp3")

	# TODO Carga algunos recursos necesarios para el juego
	def cargarRecursos(self):
		pass

	# Elimina todos los elementos del juego
	def eliminarObjetos(self):
		for misil in self.misiles:
			misil.detachNode()
			misil.remove()

		for enemigo in self.enemigos:
			enemigo.ship.detachNode()
			enemigo.ship.remove()

		del self.misiles
		del self.enemigos