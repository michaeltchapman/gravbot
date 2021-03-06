from math import degrees, sin, cos
from panda3d.core import Point2, BoundingSphere, Vec3, Point3, BitMask32
from entity import Entity
from panda3d.bullet import BulletBoxShape,BulletRigidBodyNode
from inspect import getmembers

import utilities

class Item(object):
    """
    The thing that holds the thing that things come out the end of
    """
    def __init__(self, world, player, charges = 1):
        self.charges = charges
        self.obj = None 
        self.world = world 
        self.player = player

    def initialise(self):
        self.obj.reparentTo(self.player.obj) 

    #fired when the player clicks
    def activate(self):
        return True

    def update(self):
        return True

    def equip(self):
        self.obj.show()
        return True

    def unequip(self):
        self.obj.hide()
        return True

class Blowtorch(Item):
    """
    The thing you hold
    """
    def __init__(self, world, player):
        super(Blowtorch, self).__init__(world, player)
        self.obj = utilities.loadObject("blowtorch", scaleX = 1, scaleY = 1, depth = 0.5)
        self.obj.hide()

    def activate(self):
        #add a flame projectile
        self.world.addEntity(Flame(self.world, self.player.obj.getPos(utilities.app.render), self.player.obj.getHpr()))
        return True

    def update(self, timer):
        return

class Flame(Entity):
    """
    The thing that comes out the end of the thing you hold
    """
    animspeed = 0.1 
    depth = 20 
    playerWidth = 3
    speed = 30 
    maxlife = 10
    damage = 30

    def __init__(self, world, pos, hpr):
        super(Flame, self).__init__()

        self.shape = BulletBoxShape(Vec3(0.1,0.05,0.05))
        self.bnode = BulletRigidBodyNode()
        self.bnode.setMass(0.00001)
        self.bnode.addShape(self.shape)

        self.np = utilities.app.render.attachNewNode(self.bnode)

        self.remove = False

        self.world =world 
        self.anim = list()
        self.anim.append(utilities.loadObject("flame1", depth=0))
        self.anim.append(utilities.loadObject("flame2", depth=0))
        self.anim.append(utilities.loadObject("flame3", depth=0))
        world.bw.attachRigidBody(self.bnode)

        self.curspr = 0
        self.livetime = 0
        self.delta = 0

        self.pos = pos
        self.pos.y = Flame.depth
        self.hpr = hpr
        self.vel = Point2()
        self.vel.x = cos(world.player.angle)*Flame.speed
        self.vel.y = sin(world.player.angle)*Flame.speed

        tv = Vec3(self.vel.x, 0, self.vel.y)
        # this makes the shot miss the target if the player has any velocity
        tv += world.player.bnode.getLinearVelocity()

        self.bnode.setLinearVelocity(tv)

        tv.normalize()

        # initial position of RB and draw plane
        self.np.setHpr(hpr)
        self.np.setPos(pos+tv/2)

        self.bnode.setAngularFactor(Vec3(0,0,0))
        self.bnode.setLinearFactor(Vec3(1,0,1))
        self.bnode.setGravity(Vec3(0,0,0))

        #self.bnode.setCcdMotionThreshold(1e-7)
        #self.bnode.setCcdSweptSphereRadius(0.50)

        self.bnode.notifyCollisions(True)
        self.bnode.setIntoCollideMask(BitMask32.bit(1))
        self.bnode.setPythonTag("Entity", self)
        self.noCollideFrames = 4

        for a in self.anim:
            a.hide()
            a.reparentTo(self.np)
            a.setScale(0.25, 1, 0.25)
            a.setPos(0, -0.1,0)

        self.obj = self.anim[self.curspr]
        self.obj.show() 

        self.bnode.setPythonTag("entity", self)

    def update(self, timer):
        #animation
        self.delta += timer
        self.livetime += timer

        if self.remove:
            self.obj.hide()
            return

        if self.noCollideFrames == 0:
            self.bnode.setIntoCollideMask(BitMask32.allOn())

        if self.noCollideFrames > -1:
            self.noCollideFrames -= 1

        if self.delta > Flame.animspeed:
            self.delta = 0
            self.obj.hide()
            self.curspr += 1
        if self.curspr > len(self.anim)-1:
            self.curspr = 0
        self.obj = self.anim[self.curspr]
        self.obj.show()

        if self.livetime > Flame.maxlife:
            self.remove = True

    def hitby(self, index, projectile):
        return

    def destroy(self):
        self.remove = True
        self.obj.hide()
        for model in self.anim:
            model.remove()
        self.world.bw.removeRigidBody(self.bnode)    

    def removeOnHit(self):
        self.remove = True

class Grenade(Item):
    """
    'Nades
    """
    def __init__(self, world, player):
        super(Grenade, self).__init__(world, player)
        self.obj = utilities.loadObject("grenade", scaleX = 1, scaleY = 1)
        self.obj.hide()

    def activate(self):
        return True
    
class LightLaser(Item):
    """
    Pew pew pew
    """
    def __init__(self, world, player):
        super(LightLaser, self).__init__(world, player)
        self.obj = utilities.loadObject("lightlaser", scaleX = 1, scaleY = 1, depth=0.5)
        self.obj.hide()

    def activate(self):
        return True
   
    def update(self, timer):
        return
