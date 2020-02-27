import socket
import pyxel as px
import pymunk
import numpy as np

import sys
sys.path.append('../')
from block import Block, Platform
import constants
from player import Player
from enemy import Drifter, Teleporter
import drawPoly 
import utils 


class App:
    def __init__(self):
        # at 100, each 40 bits, maximum of 4000 bits per packet, or roughly 500 bytes
        # to be safe, request 1024 bytes

        self.addr= "127.0.0.1"
        self.port   = 5001
        self.bufSize  = 1024

        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        # Bind to address and ip
        self.sock.bind((self.addr, self.port))
        self.sock.setBlocking(False)    # no blocking so server doesn't wait for user input

        print("Server up")

        px.init(512, 400, scale = 2, fps = 60, caption = 'ngon', palette = constants.PALETTE)

        self.px = px

        self.space = pymunk.Space()
        self.space.gravity = 0, 0

        self.boundsBody = pymunk.Body(body_type = pymunk.Body.STATIC)
        self.bounds = [pymunk.Segment(self.boundsBody, [-200, -200], [200, -200], 2),
                       pymunk.Segment(self.boundsBody, [200, -200], [200, 200], 2), 
                       pymunk.Segment(self.boundsBody, [200, 200], [-200, 200], 2), 
                       pymunk.Segment(self.boundsBody, [-200, 200], [-200, -200], 2)]

        for b in self.bounds:
            b.elasticity = 1
        self.boundsBody.position = 200, 200

        self.player = pymunk.Body(2, pymunk.inf)
        self.hitbox= pymunk.Poly.create_box(self.player, (10, 10), 2)
        self.player.position = 200, 200

        self.space.add(self.player, self.hitbox)

        self.space.add(self.boundsBody, *self.bounds)

        self.offsetX = 0 
        self.offsetY = 0
        self.blocks = [Block(10, 10, 50, 50, self), Block(30, 40, 80, 100, self), Block(10, 10, 80, 150, self)]
        for b in self.blocks:
            b.add(self.space)

        self.addresses = set() 
        
        px.run(self.update, self.draw)
    
    def update(self):
        self.space.step(1/180.)    
        self.space.step(1/180.)    
        self.space.step(1/180.)    
       
        if px.btn(px.KEY_W):
            self.player.velocity = (0, 60)
        if px.btn(px.KEY_A):
            self.player.velocity = (-60, 0)
        if px.btn(px.KEY_S):
            self.player.velocity = (0, -60)
        if px.btn(px.KEY_D):
            self.player.velocity = (60, 0)
        if px.btn(px.KEY_Q):
            self.UDPServerSocket.close()

        message, address = None, None
        try:
            bytesAddressPair = self.UDPServerSocket.recvfrom(self.bufferSize)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]
        except BlockingIOError:
            print("no packet received")
        except ConnectionResetError:
            print('user dropped')

        if message:
            # user is joining
            if address not in self.addresses:
                self.addresses.add(address)
                        
                # send acknowledgement
                self.sock.sendto(b"ack", address)
                print("user joined @ %s" % address)

        # send simulation data to client
        # Sending a reply to client
        for addr in self.addresses:
            payload = self._generateSimulationPayload()
            self.UDPServerSocket.sendto(self.bytesToSend, addr)

    def _generateSimulationPayload(self):
        """
            block payload is as follows

            block:
            {
                position: (x, y), - 14 bit integers
                angle: r,         - 11 bit integer
                blockIndex: n     - 9  bit integer  (max 256 entities)
            }

            total: 28 + 11 + 9 = 48 bits per block
            over ~200 blocks is 10000 bits per frame = 10 kb
            @ 60fps = 600 kb/s

            most blocks probably won't be moving (worst case maybe 100 at a time; mobs + block interactions)
            this brings it down to roughly 300 kb/s on average.
            
            with compression this should be much better, ~100 kb/s

            for this server test, there are only max like 10 blocks, so we keep it down to 500 bits per frame,
            or about 30 kb/s
        
        
            each block is 48 bits in total, so it's 6 bytes
        """

        POS_SIZE = 14
        ANGLE_SIZE = 11
        IDX_SIZE = 9

        payload = 0
        for idx, b in enumerate(self.blocks):
            acc = 0

            pos = b.body.position
            angle = b.body.angle
            
            # quantize to 14 bits signed integer
            # 14 bits is 16387
            # field is 2000 wide, gives precision of about 0.12, which is totally fine for what we're doing.
            prec = 2000 / (2 ** POS_SIZE - 1)
            invPrec = 1/prec
            x, y = utils.quantize(x, -1000, 1000, POS_SIZE), utils.quantize(y, -1000, 1000, POS_SIZE)

            acc = x + (y << POS_SIZE)

            # quantize angle to 11 bit integer
            # convert angle to positive number and remove redundant angle
            angle %= np.pi * 2
            r = utils.quantize(angle, 0, np.pi * 2, ANGLE_SIZE)

            acc += r << (POS_SIZE + POS_SIZE)
            acc += idx << (POS_SIZE + POS_SIZE + ANGLE_SIZE)

            payload += acc << (idx * (POS_SIZE + POS_SIZE + ANGLE_SIZE + IDX_SIZE))        

    def draw(self):
        px.cls(7)

        # draw ground
        px.rect(0, px.height, px.width, 150, 0)

        for b in self.blocks:
            # if block is queried by the player, color it a different color
            col = 1
            fill = 13

            b.draw(col = col, fill = fill)
    
        drawPoly.drawPolygon(self.hitbox, 0, 0)
        
        # draw crosshair
        px.line(px.mouse_x - 1, px.mouse_y, px.mouse_x + 1, px.mouse_y, 1)
        px.line(px.mouse_x, px.mouse_y - 1, px.mouse_x, px.mouse_y + 1, 1)

        px.line(0, 400, 400, 400, 2)
        px.line(400, 400, 400, 0, 2)
        px.line(400, 0, 0, 0, 2)
        px.line(0, 0, 0, 400, 2)

App()

