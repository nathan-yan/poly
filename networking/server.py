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

class App:
    def __init__(self):
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

"""
localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = 1024

msgFromServer       = "Hello UDP Client"
bytesToSend         = str.encode(msgFromServer)

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
 
# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

# Listen for incoming datagrams
while(True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    clientMsg = "Message from Client:{}".format(message)
    clientIP  = "Client IP Address:{}".format(address)
    
    print(clientMsg)
    print(clientIP)

    # Sending a reply to client
    UDPServerSocket.sendto(bytesToSend, address)
"""