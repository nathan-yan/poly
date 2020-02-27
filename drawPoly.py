import pyxel as px
import numpy as np

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
    for y in range (min_y , max_y):
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

def drawPolygon(shape, ox, oy, col = 1, fill = 3):
    transformedVertices = []

    vertices = shape.get_vertices()
    for i, v in enumerate(vertices):
        current = v

        current = current.rotated(shape.body.angle + 0.001) + shape.body.position
        current[0] += ox
        current[1] = px.height - current[1] + oy

        transformedVertices.append(current)

    # get endpoints
    if fill:
        endpoints = getScanline(transformedVertices)
        for e in endpoints:
            if len(e) == 2:
                px.line(e[0][0] + 0.5, e[0][1], e[1][0] - 0.5, e[1][1], fill)
    
    for i in range (len(vertices)):
        px.line(*transformedVertices[i], *transformedVertices[i - 1], col)

if __name__ == "__main__":
    px.init(256, 200)

    angle = 0
    def update():
        global angle
        angle += 0.1

    def draw():
        global angle
        px.cls(7)

        points = np.array([[100,90],
    [90,97],
    [94,108],
    [106,108],
    [110,97]]) * 0.5

        mid = np.mean(points)
        t = points - mid

        p = np.array([t[:, 0] * np.cos(angle) - t[:, 1] * np.sin(angle) + mid, t[:, 0] * np.sin(angle) + t[:, 1] * np.cos(angle) + mid])
        print(p)
        print(p.T)
        

        drawPolygon(p.T)

    px.run(update, draw)