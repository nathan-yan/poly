import numpy as np
import pymunk
import constants

import time

import drawPoly

# In n-gon all polygons are convex and are regular (with the exception of rectangles). The center of mass is therefore the average of all the vertices


class Block:
    def __init__(self, w, h, x, y, app, friction = 4, elasticity = 0.5):
        self.shape = pymunk.Poly.create_box(None, (w, h), radius = 0.5)
        area = self.shape.area
        self.shape.friction = friction
        self.shape.elasticity = elasticity
        self.shape.filter = pymunk.ShapeFilter(categories = constants.MASK_MOBDAMAGABLE | constants.MASK_PLAYERDAMAGABLE | constants.MASK_BLOCK)

        mass = constants.DENSITY * area
        moment = pymunk.moment_for_box(mass, (w, h)) * 5

        self.body = pymunk.Body(mass, moment)
        self.body.position = x, y
        self.shape.body = self.body

        self.app = app 
    
    def add(self, space):
        space.add(self.body, self.shape)
    
    def draw(self, col = 1, fill = None):
        drawPoly.drawPolygon(self.shape,  self.app.offsetX, self.app.offsetY, col, fill)

class BlockPoly(Block):
    def __init__(self, x, y, vertices, app, friction = 4, elasticity = 0.5):
        self.shape = pymunk.Poly(None, vertices, radius = 0.5)
        area = self.shape.area
        self.shape.friction = friction
        self.shape.elasticity = elasticity
        self.vertices = vertices 
        self.shape.filter = pymunk.ShapeFilter(categories = constants.MASK_MOBDAMAGABLE | constants.MASK_PLAYERDAMAGABLE | constants.MASK_BLOCK)

        mass = constants.DENSITY * area
        moment = pymunk.moment_for_poly(mass, self.vertices) * 5

        self.body = pymunk.Body(mass, moment)
        self.body.position = x, y
        self.shape.body = self.body

        self.app = app 
                    
class Platform:
    def __init__(self, w, h, x, y, friction = 6, elasticity = 0.5): 
        self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.shape = pymunk.Poly.create_box(self.body, (w, h), radius = 0.5)
        self.shape.filter = pymunk.ShapeFilter(categories = constants.MASK_PLATFORM)

        self.shape.friction = friction
        self.shape.elasticity = elasticity

        self.x = x
        self.y = y 
        self.w = w
        self.h = h

        self.body.position = x, y

    def add(self, space):
        space.add(self.body, self.shape)
    
    def draw(self, px, ox, oy):
        px.rect(self.x - self.w / 2 + ox, px.height - (self.y) - self.h / 2 + oy, self.w, self.h, 0)
