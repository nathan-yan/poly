import numpy as np
import sys
sys.path.append('../')

import constants
from frame import Frame
from utils import quantize, unquantize

def clientMain(sock, serverAddr, inQ, frameBuf, infoBuf, bufSize = 1024):
    """
        this is the main networking loop for a client
    
        it accepts a UDP socket and handles the sending and receiving of data.

        inQ and outQ are two queues representing data sent INto the clientMain function and OUT of the clientMain function. Items will be taken out of the queues as fast as they can
    """

    prevFrameIdx = 0
    frameIdxResets = 0

    print("starting client network thread")

    while True:
        # send inputs to server
        if not inQ.empty():
            inps = inQ.get()
            sock.sendto(inps, serverAddr)

        # receive simulation data
        frames = []
        while True:
            message, address = None, None
            try:
                payload = sock.recvfrom(bufSize)
                payload = payload[0]

                c, idx, p, players, blocks = parsePayload(payload)

                if idx < prevFrameIdx:
                    frameIdxResets += 1
                prevFrameIdx = idx 

                idx += frameIdxResets * 512

                frames.append(Frame(
                    idx,
                    players,
                    blocks
                ))
            except BlockingIOError:
                break;
            except ConnectionResetError:
                print("server dropped")
                break;
            
        frames = frames[-3 :]   # only include the most recent 3 frames
        for f in frames:
            if not frameBuf.full():
                frameBuf.put(f)

def parsePayload(payload):
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
            playerIdx = payload & PIS_M
            payload >>= PIS
            
            playerX = unquantize(payload & PS_M, -1000, 1000, PS)
            payload >>= PS

            playerY = unquantize(payload & PS_M, -1000, 1000, PS)
            payload >>= PS

            playerState = payload & PSS_M
            payload >>= PSS

            walking = (playerState & 0b11) - 1

            players.append([playerIdx, playerX, playerY, walking])

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