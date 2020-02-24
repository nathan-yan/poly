import pyxel as px
import numpy as np
import pymunk

import constants 

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
        px.init(256, 200, scale = 3, fps = 60, caption = 'ngon', palette = constants.PALETTE)
        px.load("ngon_resources3.pyxres")

        self.px = px

        self.space = pymunk.Space()
        self.space.gravity = 0, -400

        self.ground = pymunk.Segment(self.space.static_body, [-1000, -5], [1000, -5], 5)
        self.ground.friction = 6
        self.ground.elasticity = 0.5
        self.ground.filter = pymunk.ShapeFilter(categories = constants.MASK_PLATFORM)

        self.space.add(self.ground)

        self.blocks = [Block(10, 10, 50, 50), Block(30, 40, 80, 100), Block(10, 10, 80, 150)]
        for b in self.blocks:
            b.add(self.space)
        
        self.platforms = [Platform(100, 90, 300, 00), Platform(100, 200, 380, 00), Platform(100, 200, 300, 200)]
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

        self.player.reset()

        playerPos = self.player.player.position
        diffX = px.mouse_x - playerPos[0]
        offsetXTarget = -playerPos[0] + px.width/2 - np.sign(diffX) * np.sqrt(abs(diffX)) * 3

        diffY = px.mouse_y - playerPos[1]
        offsetYTarget = +playerPos[1] - px.height/4 - np.sign(diffY) * np.sqrt(abs(diffY)) * 3 

        self.offsetX = (0.95) * self.offsetX + 0.05 * offsetXTarget
        self.offsetY = (0.95) * self.offsetY + 0.05 * offsetYTarget

    def draw(self):
        px.cls(7)
        self.player.draw(self.offsetX, self.offsetY)

        # draw ground
        px.rect(0, px.height + self.offsetY, px.width, 150, 0)

        for b in self.blocks:
            # if block is queried by the player, color it a different color
            col = 1
            fill = 13

            if self.player.state['nc']['emitter']:
                emitter = self.player.state['nc']['emitter']
                if emitter['pointingAt'] and emitter['pointingAt'].shape == b.shape:
                    col = 2
                    fill = 15
            
            if self.player.state['persistent']['holding'] and self.player.state['persistent']['holding'].shape == b.shape:
                fill = False

            b.draw(px, self.offsetX, self.offsetY, col = col, fill = fill)
        
        for p in self.platforms:
            p.draw(px, self.offsetX, self.offsetY)
        
        # draw crosshair
        px.line(px.mouse_x - 1, px.mouse_y, px.mouse_x + 1, px.mouse_y, 1)
        px.line(px.mouse_x, px.mouse_y - 1, px.mouse_x, px.mouse_y + 1, 1)

        px.rectb(10, 5, self.player.maxHealth + 2, 6, 0)
        px.rect(11, 6, self.player.health, 4, 14)

        px.text(px.width - 70, 5, "field emitter", 10)

        if debug:
            options = pymunk.SpaceDebugDrawOptions()

            _screen.fill((255, 255, 255))
            self.space.debug_draw(_draw_options)
            pygame.display.flip()

        
App()

