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
import time 

class Server:
    def __init__(self):
        # at 100, each 40 bits, maximum of 4000 bits per packet, or roughly 500 bytes
        # to be safe, request 1024 bytes

        self.addr= "127.0.0.1"
        self.port   = 5001
        self.bufSize  = 1024
        self.ticks = 0

        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        # Bind to address and ip
        self.sock.bind((self.addr, self.port))
        self.sock.setblocking(False)    # no blocking so server doesn't wait for user input

        print("Server up")

        #px.init(512, 400, scale = 2, fps = 60, caption = 'ngon', palette = constants.PALETTE)

        #self.px = px

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

        self.w, self.a, self.s, self.d = 0, 0, 0, 0
        
        #px.run(self.update, self.draw)
    
    def update(self):
        self.ticks += 1

        self.space.step(1/180.)    
        self.space.step(1/180.)    
        self.space.step(1/180.)    
       
        if  self.w:
            self.player.velocity = (0, 60)
        if self.a:
            self.player.velocity = (-60, 0)
        if self.s:
            self.player.velocity = (0, -60)
        if self.d:
            self.player.velocity = (60, 0)
        
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
                
                # is an input
                inp = int.from_bytes(message, byteorder = 'big')
                self.w = inp & 1 
                self.a = inp & 0b10
                self.s = inp & 0b100
                self.d = inp & 0b1000

        # send simulation data to client
        # Sending a reply to client
        for addr in self.addresses:
            payload = self._generateSimulationPayload()
            self.sock.sendto(payload, addr)

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

        return utils.getPayload(self.ticks % 2048, self.blocks, self.player.position)   

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

s = Server()
t = time.time()
# keep it 60 fps
while True: 
    s.update()
    elapsedTime = time.time() - t
    if (elapsedTime < 1/60.):
        time.sleep(1/60. - elapsedTime)
    t = time.time()

