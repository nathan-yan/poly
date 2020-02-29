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
        self.serverAddressPort   = ("127.0.0.1", 5001)
        self.bufSize          = 1024

        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    
        self.sock.sendto(str.encode("join"), self.serverAddressPort)

        print("Waiting 5 seconds for ack...")
        self.sock.settimeout(5)
        
        msg = self.sock.recvfrom(self.bufSize)
        print(msg)
        print("Received ack!")

        self.sock.setblocking(False)

        px.init(512, 400, scale = 2, fps = 60, caption = 'ngon', palette = constants.PALETTE)

        self.px = px

        self.offsetX = 0 
        self.offsetY = 0

        self.blockSizes = [[10, 10], [30, 40], [10, 10]]

        self.plx = 0
        self.ply = 0

        px.run(self.update, self.draw)
        
        self.bufferedInputs = []
    
    def update(self):
        inps = 0

        if px.btn(px.KEY_W):
            inps += 0b1
            pass
            #self.player.velocity = (0, 60)
        if px.btn(px.KEY_A):
            inps += 0b10
            pass
            #self.player.velocity = (-60, 0)
        if px.btn(px.KEY_S):
            inps += 0b100
            pass
            #self.player.velocity = (0, -60)
        if px.btn(px.KEY_D):
            inps += 0b1000

            pass
            #self.player.velocity = (60, 0)

        # receive simulation data
        while True:
            message, address = None, None
            try: 
                payload = self.sock.recvfrom(self.bufSize)
                payload = payload[0]

                # parse the payload
                code, frameIdx, plx, ply, blocks = utils.parsePayload(payload)
                self.blocks = blocks
                self.plx = plx 
                self.ply = ply
                
            except BlockingIOError:
                break;
                #print("no packet received")
            except ConnectionResetError:
                print("server dropped")
                break;
                        
        # send inputs to server
        self.sock.sendto((inps).to_bytes(1, byteorder = 'big'), self.serverAddressPort)

    def draw(self):
        px.cls(7)

        for i, b in enumerate(self.blocks):
            w, h = self.blockSizes[i]
            vertices = np.array([[b[-2] - w/2, b[-1] - h/2],
                                 [b[-2] + w/2 , b[-1] - h/2],
                                 [b[-2] + w/2, b[-1] + h/2],
                                 [b[-2] - w/2, b[-1] + h/2]])
            
            vertices -= np.array([b[-2], b[-1]])

            # rotate vertices
            x = vertices[:, 0] * np.cos(b[1]) - vertices[:, 1] * np.sin(b[1])  
            y = vertices[:, 0] * np.sin(b[1]) + vertices[:, 1] * np.cos(b[1]) 

            vertices[:, 0] = x 
            vertices[:, 1] = y

            vertices += np.array([b[-2], b[-1]])

            for v in range (len(vertices)):
                px.line(vertices[v][0], px.height - vertices[v][1], vertices[v - 1][0], px.height - vertices[v - 1][1], 1)

        px.rect(self.plx - 5, px.height - self.ply - 5, 10, 10, 3)

App()
