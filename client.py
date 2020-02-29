import pyxel as px
import numpy as np
import pymunk
import time
import socket
import queue

import constants 

from block import Block, Platform, BlockPoly     
from player import Player
from enemy import Drifter, Teleporter
from frame import Frame
from utils import quantize, unquantize

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
        px.load("resources/ngon_resources4.pyxres")

        self.px = px

        self.frameBuffer = queue.Queue(maxsize = 20)
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
            self.offsetX = -100 + px.width/2

            self.offsetY = +20 - px.height/4 

        """
        self.space.step(1/180.)    

        playerPos = self.player["position"] 
        diffX = px.mouse_x - playerPos[0]
        offsetXTarget = -playerPos[0] + px.width/2 - np.sign(diffX) * np.sqrt(abs(diffX)) * 3

        diffY = px.mouse_y - playerPos[1]
        offsetYTarget = +playerPos[1] - px.height/4 - np.sign(diffY) * np.sqrt(abs(diffY)) * 3 

        self.offsetX = (0.95) * self.offsetX + 0.05 * offsetXTarget
        self.offsetY = (0.95) * self.offsetY + 0.05 * offsetYTarget
        """

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
        
        # send inputs to server
        self.sock.sendto((inps).to_bytes(1, byteorder = 'big'), self.serverAddressPort)
        
        # receive simulation data
        frames = []
        while True:
            message, address = None, None
            try: 
                payload = self.sock.recvfrom(self.bufSize)
                payload = payload[0]

                # parse the payload
                c, idx, p, players, blocks = self._parsePayload(payload)
                if idx < self.prevFrameIdx: # the indices have reset
                    self.frameIdxResets += 1
                self.prevFrameIdx = idx
                
                idx += self.frameIdxResets * 512

                frames.append(Frame(
                idx,
                players,
                blocks,
                ))

                #print(self.frameBuffer)

            except BlockingIOError:
                break;
                #print("no packet received")
            except ConnectionResetError:
                print("server dropped")
                break;
        
        # add frames one by one
        frames = frames[-3 : ]      # only include the most recent 3 frames
        for f in frames:
            if not self.frameBuffer.full():
                self.frameBuffer.put(f)


    def _parsePayload(self, payload):
        # get code and frame index first
        PS = constants.POS_SIZE
        AS = constants.ANGLE_SIZE
        IS = constants.IDX_SIZE
        FS = constants.FRAME_IDX_SIZE
        CS = constants.CODE_SIZE
        PIS = constants.PLAYER_IDX_SIZE
        PSS = constants.PLAYER_STATE_SIZE

        PS_M = 2 ** PS - 1
        AS_M = 2 ** AS - 1
        IS_M = 2 ** IS - 1
        FS_M = 2 ** FS - 1
        CS_M = 2 ** CS - 1
        PIS_M = 2 ** PIS - 1
        PSS_M = 2 ** PSS - 1

        payload = int.from_bytes(payload, byteorder = 'big')

        code = payload & 0b111
        payload >>= 3

        frameIdx = payload & FS_M
        payload >>= FS

        numPlayers = payload & PIS_M
        payload >>= PIS

        players = []
        for p in range (numPlayers):
            playerX = unquantize(payload & PS_M, -1000, 1000, PS)
            payload >>= PS

            playerY = unquantize(payload & PS_M, -1000, 1000, PS)
            payload >>= PS

            playerState = payload & PSS_M
            payload >>= PSS

            walking = (playerState & 0b11) - 1

            players.append([playerX, playerY, walking])

        blocks = []
        while payload > 0:
            bx = unquantize(payload & PS_M, -1000, 1000, PS)
            payload >>= PS
            by = unquantize(payload & PS_M, -1000, 1000, PS)
            payload >>= PS

            br = unquantize(payload & AS_M, 0, np.pi * 2, AS)
            payload >>= AS

            bidx = payload & IS_M
            payload >>= IS
        
            blocks.append([bidx, br, bx,by])
        
        #print(code, frameIdx, numPlayers)
        return code, frameIdx, numPlayers, players, blocks

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
            walkState = self.players[0][-1]
            if walkState:
                walkFrame = (self.ticks // 2) % 12

                self.px.blt(self.players[0][0] - 7 + self.offsetX, np.round(self.px.height - self.players[0][1] - 8, 2) + self.offsetY, 0, 1 + (15 + 2+ 1) * (1 + (walkState * 1  * walkFrame % 12)), 1, 1* 15, 19)

            else:
                # Player is still
                self.px.blt(self.players[0][0] - 7 + self.offsetX, self.px.height - self.players[0][1] - 8 + self.offsetY, 0, 1, 1, 1 * 15, 19)
            

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

            #px.rect(self.players[0][0] - 5 + self.offsetX, px.height - self.players[0][1] - 5 + self.offsetY , 10, 10, 3)
                
App()

