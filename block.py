import numpy as np
import pymunk
import constants

# In n-gon all polygons are convex and are regular (with the exception of rectangles). The center of mass is therefore the average of all the vertices

def lineIntersection(s1, e1, s2, e2):
    # s1, e1 is the scanline
    # the return value t will be the position on the polygon segment. That value of t must be within 0 and 1
    v1 = (e1 - s1).astype(float)
    v2 = (e2 - s2).astype(float)

    a = s2[1] - s1[1] - (v1[1] * s2[0] - v1[1] * s1[0]) / v1[0]
    b = (v1[1] * v2[0] - v2[1] * v1[0]) / (v1[0])

    t = (a / b)
    s = (s2[0] + t * v2[0] - s1[0]) / v1[0]

    if t > 1 or t < 0:
        return False
    else:
        return s2 + v2 * t, 1     

def getScanline(vertices):
    max_y = vertices[0][1]
    min_y = vertices[0][1]
    max_x = vertices[0][0]
    min_x = vertices[0][0]

    for v in vertices:
        if v[1] > max_y:
            max_y = v[1]
        
        if v[1] < min_y:
            min_y = v[1]
        
        if v[0] > max_x:
            max_x = v[0]
        
        if v[1] < min_y:
            min_y = v[1]
        
    min_y = int(np.floor(min_y))
    max_y = int(np.ceil(max_y))
    min_x = int(np.floor(min_x))
    max_x = int(np.ceil(max_x))
    
    segments = []
    for i, v in enumerate(vertices):
        segments.append(np.array([vertices[i - 1], vertices[i]]))
        
    endpoints = []
    for y in range (min_y, max_y):
        scanline = np.array([[min_x, y], [max_x, y]])

        collisions = []
        c = 0
        for s in segments:
            res = lineIntersection(scanline[0], scanline[1], s[0], s[1])
            
            if res:
                res = res[0]
                if len(collisions) == 0 or res[0] > collisions[0][0]:
                    collisions.append(res)
                else:
                    collisions.insert(0, res)
                
                c += 1

                if c == 2:
                    break;
        
        endpoints.append(collisions)

    return endpoints

#print(getScanline( [
#[-2, -3.5], [2, -3.5], [4, 0], [2, 3.5], [-2, 3.5], #[-4, 0]]))

class Block:
    def __init__(self, w, h, x, y, friction = 4, elasticity = 0.5):
        self.shape = pymunk.Poly.create_box(None, (w, h), radius = 0.5)
        area = self.shape.area
        self.shape.friction = friction
        self.shape.elasticity = elasticity

        mass = constants.DENSITY * area
        moment = pymunk.moment_for_box(mass, (w, h)) * 5

        self.body = pymunk.Body(mass, moment)
        self.body.position = x, y
        self.shape.body = self.body
    
    def add(self, space):
        space.add(self.body, self.shape)
    
    def draw(self, px, ox, oy):
        vertices = self.shape.get_vertices()
        for i, v in enumerate(vertices):
            current = v
            prev = vertices[i - 1]

            current = current.rotated(self.body.angle) + self.body.position
            prev = prev.rotated(self.body.angle) + self.body.position

            current[1] = px.height - current[1]
            prev[1] = px.height - prev[1]

            px.line(*(current + (ox, oy)), *(prev + (ox, oy)), 1)

class Platform:
    def __init__(self, w, h, x, y, friction = 6, elasticity = 0.5): 
        self.body = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.shape = pymunk.Poly.create_box(self.body, (w, h), radius = 0.5)

        self.shape.friction = friction
        self.shape.friction = elasticity

        self.x = x
        self.y = y 
        self.w = w
        self.h = h

        self.body.position = x, y

    def add(self, space):
        space.add(self.body, self.shape)
    
    def draw(self, px, ox, oy):
        px.rect(self.x - self.w / 2 + ox, px.height - (self.y) - self.h / 2 + oy, self.w, self.h, 0)
