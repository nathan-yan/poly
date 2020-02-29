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

def parsePayload(payload):
    payload = int.from_bytes(payload, byteorder = 'big')
    print(bin(payload))

    POS_SIZE = 14
    ANGLE_SIZE = 11
    IDX_SIZE = 9
    FRAME_IDX_SIZE = 12      # rolling buffer of frame indices
    CODE_SIZE = 4       # 1000 is acknowledgement, 1001 is simulation data

    POS_MASK = 2 ** POS_SIZE - 1
    ANGLE_MASK = 2 ** ANGLE_SIZE - 1
    IDX_MASK = 2 ** IDX_SIZE - 1 
    FRAME_IDX_MASK = 2 ** FRAME_IDX_SIZE - 1
    CODE_MASK = 2 ** CODE_SIZE - 1
    print(bin(CODE_MASK))

    # get code and frame idx
    code = payload & CODE_MASK
    payload >>= CODE_SIZE
    frameIdx = payload & FRAME_IDX_MASK
    payload >>= FRAME_IDX_SIZE

    while payload > 0:
        x = utils.unquantize(payload & POS_MASK, -1000, 1000, POS_SIZE)
        payload >>= POS_SIZE

        y = utils.unquantize(payload & POS_MASK, -1000, 1000, POS_SIZE)
        payload >>= POS_SIZE

        angle = utils.unquantize(payload & ANGLE_MASK, 0, np.pi * 2, ANGLE_SIZE)
        payload >>= ANGLE_SIZE

        idx = payload & IDX_MASK
        payload >>= IDX_SIZE
    
        print("idx: %s, angle: %s, pos: (%s, %s)" % (idx, angle, x, y))

    print(code, frameIdx)
 

msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20001)

bufferSize          = 1024

 

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket2 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 
UDPClientSocket.setblocking(False)
UDPClientSocket2.setblocking(False)

# Send to server using created UDP socket

UDPClientSocket.sendto(bytesToSend, serverAddressPort)
UDPClientSocket2.sendto(bytesToSend, serverAddressPort)
print('sent message1')
UDPClientSocket.sendto(bytesToSend, serverAddressPort)
UDPClientSocket2.sendto(bytesToSend, serverAddressPort)
print('sent message2')


 
while True:
    a = input(">>>")
    if (str(a) == 'q'):
        break;
    try:
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)

        print(msgFromServer)

        msg = "Message from Server {}".format(msgFromServer[0])
        print(parsePayload(msgFromServer[0]))


        msgFromServer = UDPClientSocket2.recvfrom(bufferSize)

        

        msg = "Message from Server {}".format(msgFromServer[0])

        print(msg)
    except BlockingIOError:
        print('no message recieved')
    except ConnectionResetError:
        print("server dropped")
    except Exception as e:
        print(e)