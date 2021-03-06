# World is an ordered list of chunks.
# current chunk is where the current player is
# simulate the current, previous and next chunks

from entity import Entity
from panda3d.core import Point2, Point3, BoundingBox, BoundingSphere, Vec3
from panda3d.core import PerlinNoise2
from panda3d.core import TransformState
from player import Player
from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletConvexHullShape 
from panda3d.bullet import BulletRigidBodyNode

from math import hypot 
import utilities
from random import randint
from items import Flame
from copy import copy
from chunks import Block, Chunk
from genworld import genBox, genFillBox

from path import buildMap, printMap
from enemies import Catcher, Enemy
#from ai.path import createCollisionMap


worldsize = Point2(200,200)

class World():
    CULLDISTANCE = 10
    def __init__(self, size):
        self.bw = BulletWorld()
        self.bw.setGravity(0,0,0)
        self.size = size
        self.perlin = PerlinNoise2()

        #utilities.app.accept('bullet-contact-added', self.onContactAdded) 
        #utilities.app.accept('bullet-contact-destroyed', self.onContactDestroyed) 

        self.player = Player(self)
        self.player.initialise()

        self.entities = list()
        self.bgs = list()
        self.makeChunk(Point2(0,0), Point2(3.0, 3.0)) 

        self.cmap = buildMap(self.entities, self.player.location)

        self.mps = list()

        self.entities.append(Catcher(Point2(10, 10), self.player, self.cmap, self))

    def update(self, timer):
        dt = globalClock.getDt()
        self.bw.doPhysics(dt, 5, 1.0/180.0)
        
        self.doHits(Flame)

        self.doHits(Catcher)

        for entity in self.entities:
            if entity.remove == True:
                entity.destroy()
                self.entities.remove(entity)

        self.player.update(dt)
        self.cmap = buildMap(self.entities, self.player.location)

        for entity in self.entities:
            entity.update(dt)

    def doHits(self, hit_type):
        for entity in self.entities:
            if isinstance(entity, hit_type):
                ctest = self.bw.contactTest(entity.bnode)
                if ctest.getNumContacts() > 0:
                    entity.removeOnHit()
                    mp =  ctest.getContacts()[0].getManifoldPoint()
                    if isinstance(ctest.getContacts()[0].getNode0().getPythonTag("entity"), hit_type):
                        ctest.getContacts()[0].getNode1().getPythonTag("entity").hitby(hit_type, mp.getIndex0())
                    else:    
                        ctest.getContacts()[0].getNode0().getPythonTag("entity").hitby(hit_type, mp.getIndex0())

    def makeChunk(self, pos, size):
        self.bgs.append(utilities.loadObject("stars", depth=100, scaleX=200, scaleY=200.0, pos=Point2(pos.x*worldsize.x,pos.y*worldsize.y)))
        genFillBox(self, Point2(5,5), 3, 6, 'metalwalls')
        genBox(self, Point2(10,5), 2, 2, 'metalwalls')
        #self.entities[0].bnode.applyTorque(Vec3(0,50,10))

    def addEntity(self, entity):
        self.entities.append(entity)

    def onContactAdded(self, node1, node2):
        e1 = node1.getPythonTag("entity")
        e2 = node2.getPythonTag("entity")

        if isinstance(e1, Flame):
            e1.remove = True
        if isinstance(e2, Flame):
            e2.remove = True

        print "contact"
    
    def onContactDestroyed(self, node1, node2):
        return

def distance(p1, p2):
    return hypot(p1.x-p2.x, p1.y - p2.y) 

def printMatrix(matrix):
    astr = ""
    for i in range(0, len(matrix)):
        tstr = ""
        for j in range(0, len(matrix[0])):
            tstr = tstr +  str(matrix[i][j]) + " "
        astr = tstr + '\n' + astr
    print astr    
