import numpy as np

def containsCategory(categories, check):
    return check & categories != 0

def quantize(n, low, high, bits):
    n = np.clip(n, low, high)
    prec = (high - low) / (2 ** bits - 1)
    invPrec = 1/prec
    return int((n - low) * invPrec)

def unquantize(n, low, high, bits):
    prec = (high - low) / (2 ** bits - 1)

    return n * prec + low


def getPayload(frameIdx, blocks, playerPos):
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

    payload += quantize(playerPos[0], -1000, 1000, POS_SIZE) << bits
    bits += POS_SIZE
    payload += quantize(playerPos[1], -1000, 1000, POS_SIZE) << bits
    bits += POS_SIZE 

    for idx, b in enumerate(blocks):
        pos = b.body.position
        angle = b.body.angle % (np.pi * 2)
        x, y = pos

        # quantize to 14 bits signed integer
        # 14 bits is 16387
        # field is 2000 wide, gives precision of about 0.12, which is totally fine for what we're doing.
        prec = 2000 / (2 ** POS_SIZE - 1)
        invPrec = 1/prec
        x, y = quantize(x, -1000, 1000, POS_SIZE), quantize(y, -1000, 1000, POS_SIZE)

        payload += x << bits 
        payload += y << (bits + POS_SIZE)
        bits += POS_SIZE * 2

        # quantize angle to 11 bit integer
        # convert angle to positive number and remove redundant angle
        angle %= np.pi * 2
        r = quantize(angle, 0, np.pi * 2, ANGLE_SIZE)

        payload += r << bits
        bits += ANGLE_SIZE

        payload += idx << bits
        bits += IDX_SIZE

    TOTAL_SIZE = bits

    return (payload).to_bytes(TOTAL_SIZE // 8, byteorder = 'big')

def parsePayload(payload):
    payload = int.from_bytes(payload, byteorder = 'big')

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

    # get code and frame idx
    code = payload & CODE_MASK
    payload >>= CODE_SIZE
    frameIdx = payload & FRAME_IDX_MASK
    payload >>= FRAME_IDX_SIZE

    plx = unquantize(payload & POS_MASK, -1000, 1000, POS_SIZE) 
    payload >>= POS_SIZE 
    ply = unquantize(payload & POS_MASK, -1000, 1000, POS_SIZE)
    payload >>= POS_SIZE

    blocks = []
    while payload > 0:
        x = unquantize(payload & POS_MASK, -1000, 1000, POS_SIZE)
        payload >>= POS_SIZE

        y = unquantize(payload & POS_MASK, -1000, 1000, POS_SIZE)
        payload >>= POS_SIZE

        angle = unquantize(payload & ANGLE_MASK, 0, np.pi * 2, ANGLE_SIZE)
        payload >>= ANGLE_SIZE

        idx = payload & IDX_MASK
        payload >>= IDX_SIZE
    
        blocks.append([idx, angle, x, y])

    return code, frameIdx, plx, ply, blocks
 

def pad(s, l, w, left = True):
    if left:
        s = w * (l - len(s)) + s
    else:
        s += w * (l - len(s))

 