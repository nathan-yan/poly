import numpy as np
import pymunk
import pyxel as px

import constants

def draw(body, shape):
    vertices = shape.get_vertices()

    opx_, opy_ = vertices[0].rotated(body.angle) + body.position

    px_ = opx_
    py_ = opy_

    for v in vertices[1:]:
        x, y = v.rotated(body.angle) + body.position
        
        px.line(px_, 200 - py_, x, 200 - y, 9)
        
        px_, py_ = x, y

    px.line(px_, 200 - py_, opx_, 200 - opy_, 9)

def drawLine(body, segment):
    x1, y1 = segment.a.rotated(body.angle) + body.position
    x2, y2 = segment.b.rotated(body.angle) + body.position

    px.line(x1, 200-y1, x2, 200-y2, 9)

class Box:
    def __init__(self, x, y, app):
        self.x = x
        self.y = y

        self.forceX = 0
        self.forceY = 0

        self.app = app
        self.space = app.space
        self.px = app.px

        self.health = 100
        self.maxHealth = 100
        
        # will probably want to improve this in the future
        self.body = pymunk.Body(2, pymunk.inf)

        self.body.position = x, y
        

        
        self.state = {
            "nc" : {
                "walking" : 0,      # 0 - static, 1 - forward, -1 - backward, 2 - jumping
                "onSurface" : False,
                "crouching": False,
                "emitter" : False
            },
            "no": {},
            "toggle": {},
            "persistent" : {
                'lastJumpImpulse': 0,    # -1, leftward, 1 - rightward
                'holding': None,
                'releasedRight': False
            },
            "lookAt" : None,
            "headCenter" : None,
            "emitterCharge" : 0,
            "grabCooldown" : 0,
            "emitterLength": 40
        }

        self.walkingCounter = 0

    def add(self):
        self.space.add(self.player, self.feet, *self.hitbox)
    
    def update(self):
        self.forceX = 0
        self.forceY = 0


        self.player.apply_force_at_local_point((self.forceX, self.forceY), (0, 0))

       

    def draw(self, ox, oy):

        


        #draw(self.player, self.hitbox)
        #drawLine(self.player, self.feet)
        #draw(self.player, self.hitbox[0])
        #drawLine(self.player, self.hitbox[1])
        #drawLine(self.player, self.hitbox[2])
        #drawLine(self.player, self.hitbox[3])
        #drawLine(self.player, self.sides[1])