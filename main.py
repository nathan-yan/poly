import pyxel as px
import numpy as np
import pymunk

from block import Block, Platform
from player import Player

debug = False

if debug:
    import pygame
    from pygame.locals import *
    import pymunk.pygame_util

    pygame.init()
    _screen = pygame.display.set_mode((600, 600))
    _clock = pygame.time.Clock()

    _draw_options = pymunk.pygame_util.DrawOptions(_screen)

class App:
    def __init__(self):
        px.init(256, 200, scale = 3, fps = 60, caption = 'ngon', palette = [0, 1911635, 8267091, 34641, 11227702, 6248271, 12764103, 16777215, 16711757, 16753408, 16772135, 58422, 2731519, 8615580, 16742312, 16764074])
        px.load("ngon_resources2.pyxres")

        self.px = px

        self.space = pymunk.Space()
        self.space.gravity = 0, -400

        self.ground = pymunk.Segment(self.space.static_body, [-1000, -5], [1000, -5], 5)
        self.ground.friction = 6
        self.ground.elasticity = 0.5

        self.space.add(self.ground)

        self.blocks = [Block(10, 10, 50, 50), Block(30, 40, 80, 100)]
        for b in self.blocks:
            b.add(self.space)
        
        self.platforms = [Platform(100, 20, 100, 30)]
        for p in self.platforms:
            p.add(self.space)

        self.player = Player(20, 20, self)
        self.player.add()

        self.offsetX = 0
        self.offsetY = 0

        px.run(self.update, self.draw)
    
    def update(self):
        self.space.step(1/180.)    
        self.player.update()
        
        self.space.step(1/180.)    
        self.player.update()
        self.space.step(1/180.)    
        self.player.update()

        playerPos = self.player.player.position
        diffX = px.mouse_x - playerPos[0]
        offsetXTarget = -playerPos[0] + px.width/2 - np.sign(diffX) * np.sqrt(abs(diffX)) * 2 

        diffY = px.mouse_y - playerPos[1]
        offsetYTarget = +playerPos[1] - px.height/4 - np.sign(diffY) * np.sqrt(abs(diffY)) * 2 

        self.offsetX = (0.97) * self.offsetX + 0.03 * offsetXTarget
        self.offsetY = (0.97) * self.offsetY + 0.03 * offsetYTarget

    def draw(self):
        px.cls(7)
        self.player.draw(self.offsetX, self.offsetY)

        # draw ground
        px.rect(0, px.height + self.offsetY, px.width, 150, 0)

        for b in self.blocks:
            b.draw(px, self.offsetX, self.offsetY)
        
        for p in self.platforms:
            p.draw(px, self.offsetX, self.offsetY)
        
        # draw crosshair
        px.line(px.mouse_x - 1, px.mouse_y, px.mouse_x + 1, px.mouse_y, 1)
        px.line(px.mouse_x, px.mouse_y - 1, px.mouse_x, px.mouse_y + 1, 1)

        if debug:
            options = pymunk.SpaceDebugDrawOptions()

            _screen.fill((255, 255, 255))
            self.space.debug_draw(_draw_options)
            pygame.display.flip()

        
App()

