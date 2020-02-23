import numpy as np
import pymunk
import pyxel as px

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

class Player:
    def __init__(self, x, y, app):
        self.x = x
        self.y = y

        self.forceX = 0
        self.forceY = 0

        self.space = app.space
        self.px = app.px

        self.jumpCool = 0

        self.health = 100
        self.energy = 100
    
        # will probably want to improve this in the future
        self.player = pymunk.Body(2, pymunk.inf)

        self.player.position = x, y
        
        self.hitbox = [pymunk.Poly.create_box(self.player, [11, 17]), pymunk.Segment(self.player, [-1, -9], [-5.5, -7], 1), pymunk.Segment(self.player, [1, -9], [5.5, -7], 1), pymunk.Segment(self.player, [-1, -9.1], [1, -9.1], 0.5)]

        self.hitbox[0].friction = 0
        self.hitbox[1].friction = 0
        self.hitbox[2].friction = 0
        self.hitbox[3].friction = 1

        self.feet = pymunk.Segment(self.player, [-1, -10.5], [1, -10.5], 0.2)
        self.feet.friction = 1

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
                'lastJumpImpulse': 0    # -1, leftward, 1 - rightward
            }
        }

        self.walkingCounter = 0

    def add(self):
        self.space.add(self.player, self.feet, *self.hitbox)
    
    def update(self):
        self.forceX = 0
        self.forceY = 0

        self.jumpCool -= 1
        if self.jumpCool < 0:
            self.jumpCool = 0

        # check if player is on a surface
        for k in self.state['nc']:
            self.state['nc'][k] = False
        
        for k in self.state['no']:
            self.state['no'][k] = True

        onSurface = self.space.shape_query(self.feet)

        if len(onSurface) != 0:
            self.state['nc']['onSurface'] = onSurface[0]

        if self.px.btn(self.px.KEY_D):
            self.state['nc']['walking'] = 1
        
        if self.px.btn(self.px.KEY_A):
            self.state['nc']['walking'] = -1

        if self.px.btnp(self.px.KEY_W) and self.state['nc']['onSurface']:

            self.state['persistent']['lastJumpImpulse'] = 0
        
        walkState = self.state['nc']['walking']
        if self.state['nc']['onSurface']:
            self.walkingCounter += 1

            if self.px.btn(self.px.KEY_W) and self.jumpCool <= 0:
                self.jumpCool = 20
                self.player.velocity = self.player.velocity[0], 0

                self.player.apply_impulse_at_local_point((0, 400), (0, 0))

                # apply a force to object player is standing on
                
            if self.px.btn(self.px.KEY_D):
                if (self.player.velocity[0] < 50):
                    self.forceX += self.state['nc']['onSurface'].shape.friction * 800 * 1.5
                else:
                    self.forceX += self.state['nc']['onSurface'].shape.friction * 800

            elif self.px.btn(self.px.KEY_A):
                if (self.player.velocity[0] > -50):
                    self.forceX -= self.state['nc']['onSurface'].shape.friction * 800 * 1.5
                else:
                    self.forceX -= self.state['nc']['onSurface'].shape.friction * 800
        else:
            if (self.px.btn(self.px.KEY_D) and self.player.velocity[0] < 25):
                self.forceX += 400
            elif (self.px.btn(self.px.KEY_A) and self.player.velocity[0] > -25):
                self.forceX -= 400
        
        if abs(self.player.velocity[0]) > 100:
            self.player.velocity = self.player.velocity[0] * 0.92, self.player.velocity[1]

        self.player.apply_force_at_local_point((self.forceX, self.forceY), (0, 0))
                

    def draw(self, ox, oy):
        flip = np.sign(px.mouse_x - self.player.position[0] - ox)

        walkState = self.state['nc']['walking']
        if walkState and self.state['nc']['onSurface']:
            walkFrame = (self.walkingCounter // 6) % 12

            self.px.blt(self.player.position[0] - 7 + ox, np.round(self.px.height - self.player.position[1] - 10, 2) + oy, 0, 1 + (15 + 2+ 1) * (1 + (walkState * flip  * walkFrame % 12)), 1, flip * 15, 19)

        else:
            # Player is still
            self.px.blt(self.player.position[0] - 7 + ox, self.px.height - self.player.position[1] - 10 + oy, 0, 1, 1, flip * 15, 19)
        
        #draw(self.player, self.hitbox)
        #drawLine(self.player, self.feet)
        #draw(self.player, self.hitbox[0])
        #drawLine(self.player, self.hitbox[1])
        #drawLine(self.player, self.hitbox[2])
        #drawLine(self.player, self.hitbox[3])
        #drawLine(self.player, self.sides[1])