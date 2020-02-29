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

def getPayload(frameIdx, blocks):
    POS_SIZE = 14
    ANGLE_SIZE = 11
    IDX_SIZE = 9
    FRAME_IDX_SIZE = 12      # rolling buffer of frame indices
    CODE_SIZE = 4       # 1000 is acknowledgement, 1001 is simulation data

    bits = 0
    payload = 0

    payload += 8 << bits
    bits += CODE_SIZE

    payload += frameIdx << bits
    bits += FRAME_IDX_SIZE

    for idx in range (blocks):
        pos = (100 * idx - 500, 200 * idx)
        angle = 3.1415 * idx / 10
        x, y = pos

        # quantize to 14 bits signed integer
        # 14 bits is 16387
        # field is 2000 wide, gives precision of about 0.12, which is totally fine for what we're doing.
        prec = 2000 / (2 ** POS_SIZE - 1)
        invPrec = 1/prec
        x, y = utils.quantize(x, -1000, 1000, POS_SIZE), utils.quantize(y, -1000, 1000, POS_SIZE)

        payload += x << bits 
        payload += y << (bits + POS_SIZE)
        bits += POS_SIZE * 2

        # quantize angle to 11 bit integer
        # convert angle to positive number and remove redundant angle
        angle %= np.pi * 2
        r = utils.quantize(angle, 0, np.pi * 2, ANGLE_SIZE)

        payload += r << bits
        bits += ANGLE_SIZE

        payload += idx << bits
        bits += IDX_SIZE

    print(len(bin(payload)) - 2)

    TOTAL_SIZE = bits

    return (payload).to_bytes(TOTAL_SIZE // 8, byteorder = 'big')

getPayload(10)

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

 
UDPServerSocket.setblocking(False)

# Listen for incoming datagrams
c = 0
while(True):
    c += 1 
    a = input(">>>")
    if (str(a) == 'q'):
        break;
    
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
        
        print(clientMsg)
        print(clientIP)

    

        # Sending a reply to client

        UDPServerSocket.sendto(getPayload(c), address)
        print(c, 'c')
    except BlockingIOError:
        print('no message recieved')
    except ConnectionResetError:
        print("client dropped")