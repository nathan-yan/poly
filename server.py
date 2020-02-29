import pyxel as px
import numpy as np
import pymunk
import time
import socket

import constants 

from block import Block, Platform, BlockPoly     
from player import Player
from enemy import Drifter, Teleporter

from utils import quantize

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
        self.addr= "127.0.0.1"
        self.port   = 5001
        self.bufSize  = 1024
        self.ticks = 0
        self.addresses = set()

        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        # Bind to address and ip
        self.sock.bind((self.addr, self.port))
        self.sock.setblocking(False)    # no blocking so server doesn't wait for user input

        print("Server up")

        px.init(100, 100, scale = 2, fps = 60, caption = 'ngon', palette = constants.PALETTE)
        px.load("resources/ngon_resources4.pyxres")

        self.px = px

        self.space = pymunk.Space()
        self.space.gravity = 0, -400

        self.ground = pymunk.Segment(self.space.static_body, [-1000, -5], [1000, -5], 5)
        self.ground.friction = 6
        self.ground.elasticity = 0.5
        self.ground.filter = pymunk.ShapeFilter(categories = constants.MASK_PLATFORM)

        self.space.add(self.ground)

        self.blocks = [Block(10, 10, 50, 50, self), Block(30, 40, 80, 100, self), Block(10, 10, 80, 150, self)]
        for b in self.blocks:
            b.add(self.space)
        
        self.platforms = [Platform(100, 90, 300, 00), Platform(100, 200, 380, 00), Platform(100, 200, 300, 200)]
        for p in self.platforms:
            p.add(self.space)
        
        #self.enemies = [Drifter(constants.PENTAGON_VERTICES, 00, 30, self), Drifter(constants.PENTAGON_VERTICES, -20, 20, self, size = 1.5), Teleporter(constants.TRIANGLE_VERTICES, -50, 150, self, size = 3, color = 5)]

        self.enemies = []
        for e in self.enemies:
            e.add()

        self.player = Player(100, 20, self)
        self.player.add()

        self.offsetX = 0
        self.offsetY = 0

        self.ticks = 0

        self.time = time.time()

        px.run(self.update, self.draw)
    
    def updateEnemies(self):
        for i in range(len(self.enemies) - 1, -1, -1):
            e = self.enemies[i]
            if e.state['dead']:
                # add back as block
                self.blocks.append(BlockPoly(*e.body.position, e.shape.get_vertices(), self))
                self.blocks[-1].add(self.space)
                del self.enemies[i]
            else:
                e.update()
    
    def update(self):
        self.ticks += 1

        self.space.step(1/180.)    
        self.player.update()
        self.updateEnemies()
        
        self.space.step(1/180.)    
        self.player.update()
        self.updateEnemies()

        self.space.step(1/180.)    
        self.player.update()
        self.updateEnemies()

        self.player.reset()

        playerPos = self.player.player.position 
        diffX = px.mouse_x - playerPos[0]
        offsetXTarget = -playerPos[0] + px.width/2 - np.sign(diffX) * np.sqrt(abs(diffX)) * 3

        diffY = px.mouse_y - playerPos[1]
        offsetYTarget = +playerPos[1] - px.height/4 - np.sign(diffY) * np.sqrt(abs(diffY)) * 3 

        self.offsetX = (0.95) * self.offsetX + 0.05 * offsetXTarget
        self.offsetY = (0.95) * self.offsetY + 0.05 * offsetYTarget
        
        if (self.ticks % 100 == 0):
            timeElapsed = time.time() - self.time 
            self.time = time.time()    
            print(timeElapsed / 100)
        
        while True:
            message, address = None, None
            try:
                bytesAddressPair = self.sock.recvfrom(self.bufSize)
                message = bytesAddressPair[0]
                address = bytesAddressPair[1]
            except BlockingIOError:
                break;
                #print("no packet received")
            except ConnectionResetError:
                print('user dropped')

            if message:
                # user is joining
                if address not in self.addresses:
                    self.addresses.add(address)
                            
                    # send acknowledgement
                    self.sock.sendto(b"ack", address)
                    print(address)
                    print("user joined @ %s" % address[0] + ':' + str(address[1]))
                else:
                    # is an input
                    inp = int.from_bytes(message, byteorder = 'big')
                    self.w = inp & 1 
                    self.a = inp & 0b10
                    self.s = inp & 0b100
                    self.d = inp & 0b1000

        # send simulation data to client
        # Sending a reply to client
        if self.ticks % 2 == 0:
            for addr in self.addresses:
                payload = self._generateSimulationState()
                self.sock.sendto(payload, addr)
            
        #print(self._generateSimulationState())
        
        #if timeElapsed < 

        # delay to make sure timeElapsed is exactly 1/60

    def _generateSimulationState(self):
        """
        block:
            {
                position: (x, y), - 14 bit integers
                angle: r,         - 11 bit integer
                blockIndex: n     - 9  bit integer  (max 256 entities)
            }
        
        total: 48 bits per block

        player:
            {
                position: (x, y), - 14 bit integers
                playerIndex: n    - 3 bit integer
                playerState: {
                    walking: 0/1,
                    crouching: 0/1,
                    emitter: 0/1,
                }
            }
        
        total: 28 + 3 + 3 = 34 bits per player
    
        mob: 
            {
                tbd
            }
        
        each payload will start with a code signifiying what it represents
        (ack or state). If it is a state payload, the following 3 bits will describe how many players there are in the game, followed by n * 34 bits of player payload data. 

        The following 9 bits will describe how many blocks there are in the game+ the next n * 48 bits of block payload data. 
        """

        PS = constants.POS_SIZE
        AS = constants.ANGLE_SIZE
        IS = constants.IDX_SIZE
        FS = constants.FRAME_IDX_SIZE
        CS = constants.CODE_SIZE
        PIS = constants.PLAYER_IDX_SIZE
        PSS = constants.PLAYER_STATE_SIZE

        bits = 0
        payload = 0

        # 100 for state data
        payload += 0b100 << bits
        bits += 3

        payload += self.ticks % 512 << bits
        bits += FS

        numPlayers = 1
        payload += numPlayers << bits
        payload += 0 << (bits + PIS)
        bits += PIS 

        # this is for one player, this should be in a for loop later
        playerBody = self.player.player
        payload += quantize(playerBody.position[0], -1000, 1000, PS) << bits
        bits += PS
        payload += quantize(playerBody.position[1], -1000, 1000, PS) << bits
        bits += PS

        for idx, b in enumerate(self.blocks):
            pos = b.body.position
            angle = b.body.angle % (np.pi * 2)

            x, y = quantize(pos[0], -1000, 1000, PS), quantize(pos[1], -1000, 1000, PS)

            payload += x << bits
            payload += y << (bits + PS)
            bits += PS * 2

            r = quantize(angle, 0, np.pi * 2, AS)
            payload += r << bits
            bits += AS

            payload += idx << bits
            bits += IS 
        
        TOTAL_SIZE = bits
        return (payload).to_bytes(TOTAL_SIZE // 8, byteorder = 'big')

    def draw(self):
        px.cls(7)

        if debug:
            options = pymunk.SpaceDebugDrawOptions()

            _screen.fill((255, 255, 255))
            self.space.debug_draw(_draw_options)
            pygame.display.flip()

        
App()

