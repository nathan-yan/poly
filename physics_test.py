import pymunk               # Import pymunk..
import pyxel as px

px.init(256, 256, fps = 60, scale = 4)

px.load("ngon_resources.pyxres")

space = pymunk.Space()      # Create a Space which contain the simulation
space.gravity = 0,-200     # Set its gravity

moment = pymunk.moment_for_box(200, (20, 10))
large = pymunk.Body(200, moment)
large.position = 120, 80
large_poly = pymunk.Poly.create_box(large, (20, 10))
#space.add(large, large_poly)

mass = 1
moment = pymunk.moment_for_box(mass, (10, 5))

body = pymunk.Body(mass, moment)  # Create a Body with mass and moment
body.position = 112,100      # Set the position of the body

body2 = pymunk.Body(mass, moment)
body2.position = 85, 150

ground = pymunk.Segment(space.static_body, [-100, -5], [300, -5], 5)
print(ground.friction)
ground.friction = 4
ground.elasticity = 0.5
print(ground.friction )

space.add(ground)

poly = pymunk.Poly.create_box(body, (10, 5)) # Create a box shape and attach to body
poly.friction = 0.3
poly.elasticity = 0.5
poly2 = pymunk.Poly(body2, [
(-2, -3.5), (2, -3.5), (4, 0), (2, 3.5), (-2, 3.5), (-4, 0)])
poly2.friction = 0.3 
space.add(body, poly, body2, poly2)       # Add both body and shape to the simulation

moment = pymunk.moment_for_box(2, (15, 20))
player = pymunk.Body(2, pymunk.inf)
player_poly = pymunk.Poly.create_box(player, (15, 20))

feet = pymunk.Segment(player, [-7.4, -10.1], [7.4, -10.1], 0.09)
feet.friction = 1
space.add(feet)

player_poly.friction = 1
space.add(player, player_poly)

def draw(body, shape):
    vertices = shape.get_vertices()

    opx_, opy_ = vertices[0].rotated(body.angle) + body.position

    px_ = opx_
    py_ = opy_

    for v in vertices[1:]:
        x, y = v.rotated(body.angle) + body.position
        
        px.line(px_, 256 - py_, x, 256 - y, 9)
        
        px_, py_ = x, y

    px.line(px_, 256 - py_, opx_, 256 - opy_, 9)

def drawLine(body, segment):
    x1, y1 = segment.a.rotated(body.angle) + body.position
    x2, y2 = segment.b.rotated(body.angle) + body.position

    px.line(x1, 256-y1, x2, 256-y2, 9)

px.mouse(True)
velWalkHorz = 0
velVert = 0
c = 0
walking = 0

prev_x = 0
while True: 
    onGround = True
    c += 1  

    space.step(1/180.)
    space.step(1/180.)
    space.step(1/180.)

    px.cls(7)


    

    body2.apply_force_at_world_point((15, 0), poly2.get_vertices()[0].rotated(body2.angle) + body2.position)

    x, y= poly2.get_vertices()[0].rotated(body2.angle) + body2.position
    px.pix(x, 256 - y, 8)

    velWalkHorz = 0
    velVert = 0

    walking = False
    if c > 5:
        if px.btn(px.KEY_D):
            walking = 1
        if px.btn(px.KEY_A):
            walking = -1

        if px.btnp(px.KEY_W) and onGround:
            player.apply_impulse_at_local_point((0, 200), (0, 0))

    # for 5 frames the player's friction is set to 0, and a force proportional to the friction force between the player (when not 0) and surface is exerted 

    if walking:
        if (c % 7 == 0):
            # friction = 1, 35
            # friction = 2, 70

            player.apply_impulse_at_local_point((walking * 35 * 2.5, 22), (0, 0))    
    
            dx = player.position[0] - prev_x
            print(dx)
            prev_x = player.position[0]

    walk_frame = (c // 5) % 12 
    px.blt(player.position[0] - 7, 256 - player.position[1] - 10, 0, 1 + (15 + 2 + 1) * (1 + (walking * walk_frame % 12)), 1, 1 * 15, 19)

    draw(body, poly)
    draw(body2, poly2)
    draw(player, player_poly)
    draw(large, large_poly)
    drawLine(player, feet)
    #player.apply_force_at_local_point((velWalkHorz, velVert), (0, 0))
    
    res = space.shape_query(feet)
    if res:
        print(res[0].shape.friction)

    px.flip()

    #print(body2.position, body2.angle)