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
        self.msgFromClient       = "Hello UDP Server"

        self.bytesToSend         = str.encode(self.msgFromClient)

        self.serverAddressPort   = ("127.0.0.1", 20001)
        self.bufferSize          = 1024

        # Create a UDP socket at client side
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPClientSocket.sendto(str.encode("join"), self.serverAddressPort)

        px.init(512, 400, scale = 2, fps = 60, caption = 'ngon', palette = constants.PALETTE)

        self.px = px

        self.offsetX = 0 
        self.offsetY = 0
        
        px.run(self.update, self.draw)
    
    def update(self):
        
        if px.btn(px.KEY_W):
            pass
            #self.player.velocity = (0, 60)
        if px.btn(px.KEY_A):
            pass
            #self.player.velocity = (-60, 0)
        if px.btn(px.KEY_S):
            pass
            #self.player.velocity = (0, -60)
        if px.btn(px.KEY_D):
            pass
            #self.player.velocity = (60, 0)

        # receive simulation data
        msgFromServer = UDPClientSocket.recvfrom(self.bufferSize)
        print(msgFromServer)

    def draw(self):
        px.cls(7)

App()
