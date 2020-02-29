import numpy as np

DENSITY = 0.01
MASK_PLATFORM =        0b1
MASK_BLOCK =           0b10
MASK_PLAYER =          0b100
MASK_INVISIBLE =       0b10000
MASK_ENEMY =           0b100000
MASK_MOBDAMAGABLE =    0b1000000   # damagable to mobs
MASK_PLAYERDAMAGABLE = 0b10000000

POS_SIZE = 14
ANGLE_SIZE = 11
IDX_SIZE = 9
FRAME_IDX_SIZE = 12      # rolling buffer of frame indices
CODE_SIZE = 4       # 1000 is acknowledgement, 1001 is simulation data
PLAYER_IDX_SIZE = 3
PLAYER_STATE_SIZE = 3

PENTAGON_VERTICES = np.array([[  0.,  10.],
       [-10.,   3.],
       [ -6.,  -8.],
       [  6.,  -8.],
       [ 10.,   3.]]) * 0.2

TRIANGLE_VERTICES = np.array([[0,-100],
[-87,50],
[87,50,]]).astype(float) / 100.

t = ["000000", "2b335f", "7e2072", "19959c", 
     "8b4852", "395c98", "a9c1ff", "fafafa", 
     "d4186c", "d38441", "e9c35b", "70c6a9",
     "7696de", "a3a3a3", "ff9798", "edc7b0"]
PALETTE = [int(c, 16) for c in t]