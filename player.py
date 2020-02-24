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

class Player:
    def __init__(self, x, y, app):
        self.x = x
        self.y = y

        self.forceX = 0
        self.forceY = 0

        self.app = app
        self.space = app.space
        self.px = app.px

        self.jumpCool = 0

        self.health = 65
        self.maxHealth = 100
        self.energy = 100

        self.flip = 1

        # will probably want to improve this in the future
        self.player = pymunk.Body(2, pymunk.inf)

        self.player.position = x, y
        
        self.hitbox = [pymunk.Poly.create_box(self.player, [11, 17]), pymunk.Segment(self.player, [-1, -9], [-5.5, -7], 1), pymunk.Segment(self.player, [1, -9], [5.5, -7], 1), pymunk.Segment(self.player, [-1, -9.1], [1, -9.1], 0.5)]

        self.hitbox[0].friction = 0
        self.hitbox[1].friction = 0
        self.hitbox[2].friction = 0
        self.hitbox[3].friction = 1

        for h in self.hitbox:
            h.filter = pymunk.ShapeFilter(categories = constants.MASK_PLAYER)

        self.feet = pymunk.Segment(self.player, [-1, -10.5], [1, -10.5], 0.2)
        self.feet.friction = 1
        self.feet.filter = pymunk.ShapeFilter(categories = constants.MASK_PLAYER)

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

        self.flip = np.sign(px.mouse_x - self.player.position[0] - self.app.offsetX)

        self.state['headCenter'] = self.player.position[0] + 2 * self.flip, self.player.position[1] + 3

        self.jumpCool -= 1
        if self.jumpCool < 0:
            self.jumpCool = 0
        
        self.state['grabCooldown'] = np.clip(self.state['grabCooldown'] - 1, 0, 10)

        # check if player is on a surface
        for k in self.state['nc']:
            self.state['nc'][k] = False
        
        for k in self.state['no']:
            self.state['no'][k] = True

        onSurface = self.space.shape_query(self.feet)
        for i in range (len(onSurface) - 1, -1, -1):
            if onSurface[i].shape.sensor:
                del onSurface[i]

        if len(onSurface) != 0:
            self.state['nc']['onSurface'] = onSurface[0]

        if self.px.btn(self.px.KEY_D):
            self.state['nc']['walking'] = 1
        
        if self.px.btn(self.px.KEY_A):
            self.state['nc']['walking'] = -1

        if self.px.btnp(self.px.KEY_W) and self.state['nc']['onSurface']:

            self.state['persistent']['lastJumpImpulse'] = 0
        
        vec = np.array([px.mouse_x - (self.state['headCenter'][0] + self.app.offsetX ), px.mouse_y - (px.height - self.player.position[1] + self.app.offsetY - 3)])
        vec /= np.linalg.norm(vec)
        self.state['lookAt'] = vec

        if self.px.btn(self.px.MOUSE_RIGHT_BUTTON) or (self.px.btnr(self.px.MOUSE_RIGHT_BUTTON) and not self.state['persistent']['releasedRight']):
            if self.state['persistent']['holding']:
                # charge the emitter
                self.state['emitterCharge'] = np.clip(self.state['emitterCharge'] + 1, 0, 100)

            else:
                # Query the space
                
                query = self.space.segment_query(
                    [ self.state['headCenter'][0],               self.state['headCenter'][1]],
                    [ self.state['headCenter'][0] + self.state['lookAt'][0] * self.state['emitterLength'], self.state['headCenter'][1] - self.state['lookAt'][1] * self.state['emitterLength']],
                    1,
                    pymunk.ShapeFilter(mask = pymunk.ShapeFilter.ALL_MASKS ^ constants.MASK_PLATFORM ^ constants.MASK_PLAYER)
                )

                #print(query)

                if query: 
                    self.state['nc']['emitter'] = {
                        "pointingAt" : query[0]
                    }
                else:
                    self.state['nc']['emitter'] = {
                        "pointingAt" : None 
                    }
        
        if self.px.btnr(self.px.MOUSE_RIGHT_BUTTON) and not self.state['persistent']['releasedRight']:
            #print(self.state['lookAt'], self.state['emitterCharge'], 'CHARGE')

            if self.state['persistent']['holding']:
                # fire the object
                # the impulse imparted on the object is proportional to the emitter charge

                # revoke sensor status
                holding = self.state['persistent']['holding']
                                # reset holding
                self.state['persistent']['holding'] = None

                holding.shape.sensor = False

                holding.shape.body.position = [self.state['headCenter'][0] + self.state['lookAt'][0] * 15, 
                                                                      self.state['headCenter'][1] - self.state['lookAt'][1] * 15]
                holding.shape.body.velocity = self.player.velocity[0], self.player.velocity[1]
                
                self.space.reindex_shapes_for_body(holding.shape.body)

                # reset velocity
                newVel = self.state['lookAt'] * np.sqrt(self.state['emitterCharge']) * 50
                #print(self.state['lookAt'], self.state['emitterCharge'], 'charges')
                newVel[1] = -newVel[1]

                #holding.shape.body.velocity = newVel 
                # impart impulse
                #impulseVec = self.state['lookAt'] * self.state['emitterCharge'] * 100
                #impulseVec[1] = -impulseVec[1]
                #print(newVel)
                holding.shape.body.apply_impulse_at_world_point(newVel, holding.shape.body.position)

                # reset player mass
                self.player.mass = 2

                # set charge back to zero
                self.state['emitterCharge'] = 0
                self.state['grabCooldown'] = 10

            if self.state['nc']['emitter'] and self.state['nc']['emitter']['pointingAt']:
                self.state['persistent']['holding'] = self.state['nc']['emitter']['pointingAt']
                # make that body into a sensor
                self.state['persistent']['holding'].shape.sensor = True
                self.player.mass += np.clip(np.sqrt(self.state['persistent']['holding'].shape.body.mass), 0, 5)
        
        if self.state['persistent']['holding']:
            # body position should be at head center + 10 distance
            self.state['persistent']['holding'].shape.body.position = [self.state['headCenter'][0] + self.state['lookAt'][0] * 15, 
                                                                      self.state['headCenter'][1] - self.state['lookAt'][1] * 15]
            self.state['persistent']['holding'].shape.body.angle += 0.01

        walkState = self.state['nc']['walking']
        if self.state['nc']['onSurface']:
            self.walkingCounter += 1

            if self.px.btn(self.px.KEY_W) and self.jumpCool <= 0:
                self.jumpCool = 20
                self.player.velocity = self.player.velocity[0], 0

                self.player.apply_impulse_at_local_point((0, 400), (0, 0))

                # apply a force to object player is standing on
                
            if self.px.btn(self.px.KEY_D):
                if (self.player.velocity[0] < 70 * (5 - self.player.mass + 2)/5):        # max velocity is limited by the player's mass
                    # originally, friction of surface is 6, player mass is 2, so total force is 12 * 400 = 4800
                    # the 1.5 multiplier originally is an addition of 2400
                    self.forceX += self.state['nc']['onSurface'].shape.friction * self.player.mass * 400 * 1.5
                else:
                    self.forceX += self.state['nc']['onSurface'].shape.friction * self.player.mass * 400

            elif self.px.btn(self.px.KEY_A):
                if (self.player.velocity[0] > -70 * (5 - self.player.mass + 2)/5):
                    self.forceX -= self.state['nc']['onSurface'].shape.friction * self.player.mass * 400 * 1.5
                else:
                    self.forceX -= self.state['nc']['onSurface'].shape.friction * self.player.mass * 400
        else:
            if (self.px.btn(self.px.KEY_D) and self.player.velocity[0] < 25):
                self.forceX += 400
            elif (self.px.btn(self.px.KEY_A) and self.player.velocity[0] > -25):
                self.forceX -= 400
        
        if abs(self.player.velocity[0]) > 100:
            self.player.velocity = self.player.velocity[0] * 0.92, self.player.velocity[1]

        #if self.state['nc']['emitter']:
            #vec = np.array([px.mouse_x - (self.player.position[0] + ox + 2 * flip), px.mouse_y - (px.height - self.player.position[1] + oy - 5)])
            #vec /= np.linalg.norm(vec)


        self.player.apply_force_at_local_point((self.forceX, self.forceY), (0, 0))

        if px.btnr(px.MOUSE_RIGHT_BUTTON):
            self.state['persistent']['releasedRight'] = True

    def reset(self):
        self.state['persistent']['releasedRight'] = False

    def draw(self, ox, oy):

        walkState = self.state['nc']['walking']
        if walkState and self.state['nc']['onSurface']:
            walkFrame = (self.walkingCounter // 6) % 12

            self.px.blt(self.player.position[0] - 7 + ox, np.round(self.px.height - self.player.position[1] - 8, 2) + oy, 0, 1 + (15 + 2+ 1) * (1 + (walkState * self.flip  * walkFrame % 12)), 1, self.flip * 15, 19)

        else:
            # Player is still
            self.px.blt(self.player.position[0] - 7 + ox, self.px.height - self.player.position[1] - 8 + oy, 0, 1, 1, self.flip * 15, 19)
        
        if self.state['nc']['emitter']:

            top = self.state['lookAt']

            drawX = self.state['headCenter'][0] + ox 
            drawY = px.height - self.state['headCenter'][1] + oy

            px.line(drawX + top[0] * 5, drawY + top[1] * 5, drawX + top[0] * self.state['emitterLength'], drawY + top[1] * self.state['emitterLength'], 12)
        
        if self.state['persistent']['holding']:
            
            drawX = self.state['headCenter'][0] + ox 
            drawY = px.height - self.state['headCenter'][1] + oy

            px.line(drawX + self.state['lookAt'][0] * 5, drawY + self.state['lookAt'][1] * 5, drawX + self.state['lookAt'][0] * 15, drawY + self.state['lookAt'][1] * 15, 13)
            
            # draw charge line
            px.line(drawX + self.state['lookAt'][0] * 5, 
                    drawY + self.state['lookAt'][1] * 5, 
                    
                    drawX + self.state['lookAt'][0] * (10 * self.state['emitterCharge']/100 + 5), 
                    drawY + self.state['lookAt'][1] * (10 * self.state['emitterCharge']/100 + 5), 2)


        #draw(self.player, self.hitbox)
        #drawLine(self.player, self.feet)
        #draw(self.player, self.hitbox[0])
        #drawLine(self.player, self.hitbox[1])
        #drawLine(self.player, self.hitbox[2])
        #drawLine(self.player, self.hitbox[3])
        #drawLine(self.player, self.sides[1])