import pyxel as px
import numpy as np
import pymunk
import time
import socket
import queue
import threading

import constants 

from networking.networking import clientMain

from block import Block, Platform, BlockPoly     
from player import Player
from enemy import Drifter, Teleporter
from frame import Frame
from utils import quantize, unquantize

lock = threading.Lock()

class App:
    def __init__(self):
        self.serverAddressPort   = ("192.168.0.14", 5001)
        self.bufSize          = 1024

        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    
        self.sock.sendto(str.encode("join"), self.serverAddressPort)

        print("Waiting 5 seconds for ack...")
        self.sock.settimeout(5)
        
        msg = self.sock.recvfrom(self.bufSize)
        print(msg)
        print("Received ack!")

        self.sock.setblocking(False)

        self.toSocket = queue.Queue()
        self.frameBuffer = queue.Queue(maxsize = 20)    # frameBuffer stores sent frames from the socket
        self.infoBuffer = queue.Queue()     # infoBuffer stores any game information sent from the socket. This needs to be separate from the frameBuffer to prevent a precious frame being wasted on processing an information packet

        # networking thread should be daemonized because it should stop as soon as the main client stops
        self.networkingThread = threading.Thread(target = clientMain, args = (self.sock, self.serverAddressPort, self.toSocket, self.frameBuffer, self.infoBuffer, self.bufSize, ), daemon = True) 

        self.networkingThread.start()
        
        px.init(512, 400, scale = 2, fps = 60, caption = 'ngon', palette = constants.PALETTE)
        px.load("resources/ngon_resources4.pyxres")

        self.px = px

        self.prevFrameIdx = 0 
        self.frameIdxResets = 0
        self.frameInterpolationTicks = 0
        self.tickDifference = 0
        self.bufferInitialized = False

        self.blockSizes = [[10, 10], [30, 40], [10, 10]]
        self.blocks = []
        self.players = []
        self.playerIdx = 0

        self.offsetX = 0
        self.offsetY = 0

        self.ticks = 0

        self.time = time.time()

        px.run(self.update, self.draw)
    
    def update(self):
        self.ticks += 1

        if self.players:
            #self.offsetX = -100 + px.width/2

            #self.offsetY = +20 - px.height/4 

        
        #self.space.step(1/180.)    

            playerPos = self.players[0] 
            diffX = px.mouse_x - playerPos[0]
            offsetXTarget = -playerPos[0] + px.width/2 - np.sign(diffX) * np.sqrt(abs(diffX)) * 3

            diffY = px.mouse_y - playerPos[1]
            offsetYTarget = +playerPos[1] - px.height/4 - np.sign(diffY) * np.sqrt(abs(diffY)) * 3 

            self.offsetX = (0.95) * self.offsetX + 0.05 * offsetXTarget
            self.offsetY = (0.95) * self.offsetY + 0.05 * offsetYTarget
            
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

        # put player lookat vector
        #vec = np.array([px.mouse_x - (self.state['headCenter'][0] + self.app.offsetX ), px.mouse_y - (px.height - self.player.position[1] + self.app.offsetY - 3)])
        #vec /= np.linalg.norm(vec)
        #self.state['lookAt'] = vec
        
        #if px.btn(px.MOUSE_RIGHT_BUTTON):
        #    inps += 0b10000
        
        # place inps in outbound queue
        # eventually each inps is all unacked inps, but for now we assume no packets are dropped

        if not self.toSocket.full():
            self.toSocket.put(inps.to_bytes(1, byteorder = 'big'))

    def draw(self):
        if self.ticks % 2 == 0:
            print(self.frameBuffer.qsize(), 'size')

        # For each frame, pop the earliest frame from the queue
        if not self.bufferInitialized and not self.frameBuffer.empty():
            self.refFrame = self.frameBuffer.get()
            self.targetFrame = self.refFrame
            self.bufferInitialized = True

        if self.ticks > 2:  # let the buffer fill up a little bit
            
            if self.frameInterpolationTicks == self.tickDifference:
                self.frameInterpolationTicks = 0
                self.refFrame = self.targetFrame

                self.targetFrame = self.frameBuffer.get()
                
                if self.frameBuffer.qsize() > 2:
                    self.tickDifference = 1
                else:
                    self.tickDifference = self.targetFrame.idx - self.refFrame.idx

                self.frameInterpolationTicks += 1
                self.currentFrame = Frame.interpolate(self.refFrame, self.targetFrame, self.frameInterpolationTicks, td = self.tickDifference)
            
            elif not self.frameBuffer.empty():
                # interpolate currentFrame
                self.frameInterpolationTicks += 1
                self.currentFrame = Frame.interpolate(self.refFrame, self.targetFrame, self.frameInterpolationTicks, td = self.tickDifference)
            
            px.cls(7)

            self.players = self.currentFrame.players
            self.blocks = self.currentFrame.blocks

            # draw player
            flip = np.sign(px.mouse_x - self.players[0][0] - self.offsetX)
            walkState = self.players[0][-1]
            if walkState:
                walkFrame = (self.ticks // 2) % 12

                self.px.blt(self.players[0][0] - 7 + self.offsetX, np.round(self.px.height - self.players[0][1] - 8, 2) + self.offsetY, 0, 1 + (15 + 2+ 1) * (1 + (walkState * flip  * walkFrame % 12)), 1, flip * 15, 19)

            else:
                # Player is still
                self.px.blt(self.players[0][0] - 7 + self.offsetX, self.px.height - self.players[0][1] - 8 + self.offsetY, 0, 1, 1, flip * 15, 19)

             # draw ground
            px.rect(0, px.height + self.offsetY, px.width, 150, 0)
            

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
                    px.line(vertices[v][0] + self.offsetX, px.height - vertices[v][1] + self.offsetY , vertices[v - 1][0] + self.offsetX, px.height - vertices[v - 1][1] + self.offsetY, 1)
            
            # draw crosshair
            px.line(px.mouse_x - 1, px.mouse_y, px.mouse_x + 1, px.mouse_y, 1)
            px.line(px.mouse_x, px.mouse_y - 1, px.mouse_x, px.mouse_y + 1, 1)

            #px.rect(self.players[0][0] - 5 + self.offsetX, px.height - self.players[0][1] - 5 + self.offsetY , 10, 10, 3)

if __name__ == "__main__": 
    App()

