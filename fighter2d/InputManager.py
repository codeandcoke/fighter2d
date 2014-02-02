## InputManager
## Clase que implementa un gestor de teclado para un juego
##
## Author: Santiago Faci
## Version 1.0

import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject

class InputManager(DirectObject):

    def __init__(self):
        self.keyMap = {"up" : False,
                       "down" : False,
                       "right" : False,
                       "left" : False,
                       "fire" : False}


        self.accept("arrow_up", self.setKey, ["up", True])
        self.accept("arrow_down", self.setKey, ["down", True])
        self.accept("arrow_left", self.setKey, ["left", True])
        self.accept("arrow_right", self.setKey, ["right", True])
        self.accept("space", self.setKey, ["fire", True])
        self.accept("arrow_up-up", self.setKey, ["up", False])
        self.accept("arrow_down-up", self.setKey, ["down", False])
        self.accept("arrow_left-up", self.setKey, ["left", False])
        self.accept("arrow_right-up", self.setKey, ["right", False])
        self.accept("space-up", self.setKey, ["fire", False])

    def setKey(self, tecla, valor):
        self.keyMap[tecla] = valor
