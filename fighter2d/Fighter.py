## Fighter
## Clase principal del juego
##
## Author: Santiago Faci
## Version 4.0
##
## Todos los elementos se han animado con la utilidad egg-texture-cards
## Uso: egg-texture-cards -o animacion.egg -fps 10 animacion*.png
##
## Una vez empaquetada la aplicacion con packp3d los .egg se reemplazan
## automaticamente por .bam (estan mas optimizados), por lo que no se recomienda 
## utilizar la extension .egg a la hora de cargar modelos
## packp3d -o Fighter2D.p3d -d Fighter2D -m Fighter.py -r audio -r sqlite -r ai
##
## Si se quiere firmar para hacerla disponible desde una pagina web
## primero hay que crear un certificado
## openssl genrsa 1024 > micertificado.pem
## openssl req -new -x509 -nodes -sha1 -days 365 -key micertificado.pem >> micertificado.pem 
##
## Y posteriormente firmar la aplicacion con el certificado generado
## packp3d -S micertificado.pem -o Fighter2D.p3d -d Fighter2D -m Fighter.py -r audio -r sqlite -r ai
##
## Para empaquetar la aplicacion es necesario instalar Panda3D Runtime
## Se puede crear un instalador para cada plataforma con la siguiente aplicacion:
## pdeploy -s -N "Fighter2D" -v 1.0 Fighter2D.p3d installer
##
## Tambien se puede crear un ejecutable con la siguiente utilidad:
## pdeploy Fighter2D.p3d standalone
##
## TODO Multijugador
## TODO Que disparen los enemigos
## TODO Que los enemigos se muevan diferente
## TODO Anadir aceleracion a la nave

import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectWaitBar
from direct.gui.DirectGui import DirectEntry
import sys
import sqlite3

from Menu import Menu
from Ship import Ship
from InputManager import InputManager

class Fighter(DirectObject):
    def __init__(self):
        
        base.disableMouse()

        # Carga el fondo del juego
        self.bg = loader.loadModel("models/plane")
        self.bg.reparentTo(camera)
        self.bg.setPos(0, 200, 0)
        self.bg.setScale(300, 0, 146)
        self.bg.setTexture(loader.loadTexture("models/Backgrounds/farback.png"), 1)
        
        # Inicializa el gestor de teclado y los objetos del juego
        self.inputManager = InputManager()

        # Inicializa el menu del juego
        self.inicializarMenu()

        self.marcador = None
        self.barraEnergia = None
        self.marcadorFinalNP = None
        self.entrada = None
        self.rankingNP = None

        self.mostrarMenuJuego()
        self.accept("m", self.cambiarMenuJuego)
        self.accept("q", self.salir)

    # Inicializa el menu
    def inicializarMenu(self):
        self.menuGraphics = loader.loadModel("models/MenuGraphics")
        self.fonts = {"silver" : loader.loadFont("fonts/LuconSilver"),
                      "blue" : loader.loadFont("fonts/LuconBlue"),
                      "orange" : loader.loadFont("fonts/LuconOrange")}
        self.menu = Menu(self.menuGraphics, self.fonts, self.inputManager)
        self.menu.initMenu([0, None, 
            ["Nueva Partida", "Salir"],
            [[self.nuevaPartida], [self.salir]],
            [[None], [None]]])

    # Comienza una partida
    def nuevaPartida(self):
        
        if (not self.marcadorFinalNP is None):
            self.marcadorFinalNP.detachNode()
            self.marcadorFinalNP.remove()

        if (not self.rankingNP is None):
            self.rankingNP.detachNode()
            self.rankingNP.remove()

        self.ship = Ship(self.inputManager)
        self.mostrarInfo()

        taskMgr.add(self.actualizarInfo, "Actualizar Puntuacion")

    # Inicializa y muestra el marcador del jugador
    def mostrarInfo(self):

        self.marcador = TextNode("Marcador")
        self.marcador.setText("Puntos: " + str(self.ship.puntos))
        self.marcador.setCardColor(0, 0, 0, 1)
        self.marcador.setCardDecal(True)
        self.marcador.setCardAsMargin(0.4, 0.4, 0.4, 0.4)
        self.marcadorNP = aspect2d.attachNewNode(self.marcador)
        self.marcadorNP.reparentTo(base.a2dTopLeft)
        self.marcadorNP.setPos(0.02, 0, -0.05)
        self.marcadorNP.setScale(0.07)

        self.barraEnergia = DirectWaitBar(text = "Energia", value = 5, 
            range = 5, scale = 0.3, pos = (0, 0, 0.95))

    # Actualiza la puntuacion del jugador en pantalla
    def actualizarInfo(self, tarea):
        self.marcador.setText("Puntos: " + str(self.ship.puntos))
        self.barraEnergia["value"] = self.ship.vida
        self.barraEnergia.setValue()

        # Termina la partida
        if (self.ship.terminarPartida):
            self.terminarPartida()
            return tarea.done

        return tarea.cont

    # Termina partida liberando recursos para poder empezar una nueva
    # sin reiniciar el juego
    def terminarPartida(self):
        # Solicita al usuario un nombre para la tabla de puntuaciones
        self.entrada = DirectEntry(width = 15, numLines = 1, scale = 0.07,
            cursorKeys = 1, frameSize = (0, 15, 0, 1), command = self.almacenarPuntuacion,
            pos = (-0.3, 0, 0.1), focus = True, text_pos = (0.2, 0.2))
        self.puntos = self.ship.puntos

        self.ship.ship.detachNode()
        self.ship.ship.remove()
        taskMgr.remove("Mover Nave")
        taskMgr.remove("Generar Enemigos")
        taskMgr.remove("Comprobar Impactos")
        taskMgr.remove("Actualizar Puntuacion")
        taskMgr.remove("Explosionar*")

        self.mostrarFinPartida()

        # Libera los recursos de la partida que ha terminado
        self.ship.eliminarObjetos()
        del self.ship
        del self.menuGraphics
        del self.menu
        self.marcadorNP.detachNode()
        self.marcadorNP.remove()
        self.barraEnergia.destroy()
        del self.marcador
        del self.barraEnergia

        #self.inicializarMenu()

    # Almacena la puntuacion del jugador
    def almacenarPuntuacion(self, valor):

        self.crearBDD()

        db = sqlite3.connect("datos.db")
        cursor = db.cursor()
        parametros = (valor, self.puntos)
        cursor.execute("insert into puntuaciones values (?, ?)", parametros)
        db.commit()
        cursor.close()

        self.entrada.destroy()

        self.mostrarTopPuntuacion()

        self.inicializarMenu()

    # Crea la Base de Datos si no existe ya
    def crearBDD(self):
        db = sqlite3.connect("datos.db")
        cursor = db.cursor()
        args = ("puntuaciones",)
        cursor.execute("select name from sqlite_master where name = ?", args)
        if len(cursor.fetchall()) == 0:
            cursor.execute("create table puntuaciones (nombre text, puntuacion numeric)")
            db.commit()
        cursor.close()

    # Muestra las 10 mejores puntuaciones
    def mostrarTopPuntuacion(self):
        # Extrae las 10 mejores puntuaciones de la base de datos
        db = sqlite3.connect("datos.db")
        cursor = db.cursor()
        cursor.execute("select nombre, puntuacion from puntuaciones order by puntuacion desc limit 10")
        puntuaciones = cursor.fetchall()
        cursor.close()
        resultado = "-- MEJORES PUNTUACIONES --\n-Jugador-  -Puntuacion-\n\n"
        for nombre, puntuacion in puntuaciones:
            resultado += nombre + " " + str(puntuacion) + "\n"

        # Muestra las 10 mejores puntuaciones
        self.ranking = TextNode("Ranking")
        self.ranking.setText(resultado)
        self.ranking.setCardColor(0, 0, 0, 1)
        self.ranking.setCardDecal(True)
        self.ranking.setCardAsMargin(0.4, 0.4, 0.4, 0.4)
        self.rankingNP = aspect2d.attachNewNode(self.ranking)
        self.rankingNP.reparentTo(base.a2dTopLeft)
        self.rankingNP.setPos(1, 0, -1)
        self.rankingNP.setScale(0.07)

    # Muestra el mensaje de fin de partida
    def mostrarFinPartida(self):
        self.marcadorFinal = TextNode("Marcador Final")
        self.marcadorFinal.setText("Game Over!\nPuntuacion: " + str(self.ship.puntos) +"\n\n" +
            "Escribe tu nombre:")
        self.marcadorFinal.setCardColor(0, 0, 0, 1)
        self.marcadorFinal.setCardDecal(True)
        self.marcadorFinal.setCardAsMargin(0.4, 0.4, 0.4, 0.4)
        self.marcadorFinalNP = aspect2d.attachNewNode(self.marcadorFinal)
        self.marcadorFinalNP.setPos(-0.3, 0, 0.5)
        self.marcadorFinalNP.setScale(0.07)

    # Muestra un menu con las opciones durante el juego
    def mostrarMenuJuego(self):
        self.textoMenu = {}
        self.textoMenu["titulo"] = OnscreenText(text = "", pos = (0, 0.92), scale = 0.08, 
            fg = (1, 1, 1, 1), bg = (0, 0, 1, 0.7))
        self.textoMenu["descripcion"] = OnscreenText(text = "", pos = (0, 0.84), scale = 0.05,
            fg = (1, 1, 0, 1), bg = (0, 0, 0, 0.5))
        self.textoMenu["opciones"] = OnscreenText(text = "", pos = (-1.3, 0), scale = 0.05,
            fg = (1, 1, 1, 1), bg = (1, 0.3, 0, 0.6), align=TextNode.ALeft, wordwrap = 15)

        self.textoMenu["opciones"].setText("** OPCIONES **\n" + 
            "m = ocultar menu\n" +
            "q = salir")

        # Inicialmente el menu se deja oculto
        for linea in self.textoMenu.values():
            linea.hide()

    # Muestra / Oculta el menu de juego
    def cambiarMenuJuego(self):
        for linea in self.textoMenu.values():
            if linea.isHidden():
                linea.show()
            else:
                linea.hide()

    # Sale del juego
    def salir(self):
        print("Saliendo . . .")
        sys.exit()

fighter = Fighter()
run()
