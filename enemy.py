import numpy as np
import pymunk
import pyxel as px

import constants
import drawPoly

import utils

# eventually gonna want to add inheritance

def noGravity(body, gravity, damping, dt):
    pymunk.Body.update_velocity(body, (0, 0), damping, dt)

    l = body.velocity.length
    if l > 60:
        scale = 60 / l
        body.velocity = body.velocity * scale

class Enemy:
    def __init__(self, vertices, x, y, app, size = 5, resistance = 1, color = 9, damage = 10):
        self.x = x
        self.y = y

        self.forceX = 0
        self.forceY = 0

        self.damage = damage

        self.app = app
        self.space = app.space
        self.px = app.px

        self.health = 100
        self.resistance = 0.1 # 0 is infinite resistance
        self.maxHealth = 100

        self.size = size

        # drifer's shape is a pentagon
        self.vertices = vertices * size
        
        self.hitboxVertices = vertices * (size + 2)

        # will probably want to improve this in the future
        self.body = pymunk.Body(2 * size, pymunk.inf)
        self.body.velocity_func = noGravity
        self.body.angular_velocity = np.random.uniform(-0.5, 0.5)
        
        self.hitbox = pymunk.Poly(self.body, self.hitboxVertices, radius = 1)
        self.hitbox.filter = pymunk.ShapeFilter(categories = constants.MASK_ENEMY)
        self.hitbox.sensor = True

        self.shape = pymunk.Poly(self.body, self.vertices, radius = 1)
        self.shape.filter = pymunk.ShapeFilter(categories = constants.MASK_ENEMY)

        self.body.position = x, y
        self.color = color
        
        self.state = {
            "seePlayer": False,
            "memory" : 0,
            "lookAt" : None,
            "lookAtNorm" : None,
            "collisions" : {},
            "dead" : False,
            "ticks" : 0
        }

    def add(self):
        self.space.add(self.shape, self.body)

    def move(self):
        pass
    
    def update(self):
        self.forceX = 0
        self.forceY = 0

        self.state['ticks'] += 1

        # query the hitbox
        collision = self.space.shape_query(self.hitbox)

        toDelete = []
        for obj in self.state["collisions"]:
            self.state["collisions"][obj] -= 1
            if self.state["collisions"][obj] <= 0:
                toDelete.append(obj)
            
        for obj in toDelete:
            del self.state["collisions"][obj]

        for obj in collision:
            # for each object that has collided with the mob, find the object's velocity, and also check if it is a sensor

            if obj.shape.sensor or not utils.containsCategory(constants.MASK_MOBDAMAGABLE, obj.shape.filter.categories):
                continue
            
            # deal damage proportional to the velocity and mass, but only if the velocity is greater than some threshold
            vel = obj.shape.body.velocity
            mass = obj.shape.body.mass
            mag = vel.length

            exists = self.state["collisions"].get(obj.shape.body)
            
            #print(exists)
            if not exists:
                exists = 0
            if (mag > 40) and exists <= 0:
                self.health = np.clip(self.health - (mag - 40) * self.resistance * mass, 0, 100)
                print((mag - 40) * self.resistance * mass)

                if utils.containsCategory(constants.MASK_BLOCK, obj.shape.filter.categories):                
                    # If this is a block, add it to a list of collisions
                    # no block that has dealt damage to a mob can deal damage until at least 5 ticks later

                    self.state["collisions"][obj.shape.body] = 30

        if (self.health <= 0):
            self.remove()
    
    def remove(self):
        self.state['dead'] = True
        self.space.remove(self.shape, self.body)

    def draw(self, ox, oy):
        if self.health < self.maxHealth:
            # draw a small health bar
            bodyPos = self.body.position
            bodyPos[1] = px.height - bodyPos[1]

            px.rect(bodyPos[0] + ox - 5, 
                    bodyPos[1] + oy - self.size * 2 - 5, 
                    self.health/100 * 10, 2, 14)
            px.rect(bodyPos[0] + ox - 5 + self.health/100 * 10,
                    bodyPos[1] + oy - self.size * 2 - 5,
                    (1 - self.health/100) * 10, 2, 13)

        if (self.state['seePlayer'] or self.state['memory'] > 0):
            fill = self.color 
        else:
            fill = 7

        drawPoly.drawPolygon(self.shape, self.app.offsetX, self.app.offsetY, col = self.color, fill =  fill)

class Drifter(Enemy):
    def __init__(self, vertices, x, y, app, size = 5, resistance = 1, color = 9, damage = 10):
        super().__init__(vertices, x, y, app, size, resistance, color, damage)
        self.state['targetPos'] = None

    def move(self):
        vec = self.state['lookAt']

        if self.state['memory'] > 0 or self.state['seePlayer']:
            self.forceX += vec[0] * 1000
            self.forceY += vec[1] * 1000

        else:
            self.body.velocity = 0.99 * (self.body.velocity)
    
    def update(self):
        super().update()
        vec = np.array(self.app.player.player.position - self.body.position)
        vec /= np.linalg.norm(vec)

        self.state['lookAt'] = vec
        
        # First check if player is in line of sight.
        blocks = self.space.segment_query(self.app.player.player.position, 
                                 self.body.position, 
                                 1, pymunk.ShapeFilter(mask = constants.MASK_PLATFORM | constants.MASK_BLOCK))
        
        if not blocks:
            self.state['seePlayer'] = True
            self.state['memory'] = 120
        
        else:
            self.state['seePlayer'] = False
            self.state['memory'] = np.clip(self.state['memory'] - 1, 0, 1000)

        self.move()

        self.body.apply_force_at_world_point((self.forceX, self.forceY), self.body.position)


class Teleporter(Enemy):
    def __init__(self, vertices, x, y, app, size = 5, resistance = 1, color = 9, damage = 10):
        super().__init__(vertices, x, y, app, size, resistance, color, damage)
        self.state['spinDirection'] =  (np.random.randint(0, 2) * 2 - 1)

    def checkCollision(self):
        collisions = self.space.shape_query(self.shape)
        for obj in collisions:
            if utils.containsCategory(constants.MASK_PLAYER, obj.shape.filter.categories):
                print(obj)
                self.app.player.damage(self.damage)

    def move(self):
        vec = self.state['lookAt']

        # First check if player is in line of sight.
        blocks = self.space.segment_query(self.app.player.player.position, 
                                 self.body.position, 
                                 1, pymunk.ShapeFilter(mask = constants.MASK_PLATFORM | constants.MASK_BLOCK))

        if self.state['memory'] > 0 or self.state['seePlayer']:
            if self.state['ticks'] % 400 == 100:
                self.state['spinDirection'] = (np.random.randint(0, 2) * 2 - 1)

            if self.state['ticks'] % 400 < 12:
                self.state['targetPos'] = [self.body.position[0] + vec[0] * 20, self.body.position[1] + vec[1] * 20]

                self.body.velocity = vec[0] * 1000, vec[1] * 1000

            self.body.angular_velocity = self.state['spinDirection'] * (self.state['ticks'] % 400) * 0.03
        else:
            self.body.velocity = 0.97 * (self.body.velocity)
    
    def update(self): 
        super().update()
        vec = np.array(self.app.player.player.position - self.body.position)
        vec /= np.linalg.norm(vec)
        
        b = 5

        self.state['lookAt'] = vec
        
        # First check if player is in line of sight.
        blocks = self.space.segment_query(self.app.player.player.position, 
                                 self.body.position, 
                                 1, pymunk.ShapeFilter(mask = constants.MASK_PLATFORM | constants.MASK_BLOCK))
        
        if not blocks:
            self.state['seePlayer'] = True
            self.state['memory'] = 120
        
        else:
            self.state['seePlayer'] = False
            self.state['memory'] = np.clip(self.state['memory'] - 1, 0, 1000)
        
        self.move()
        self.checkCollision()
        
        self.body.apply_force_at_world_point((self.forceX, self.forceY), self.body.position)