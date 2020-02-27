import numpy as np

def containsCategory(categories, check):
    return check & categories != 0

def quantize(n, low, high, bits):
    n = np.clip(n, low, high)
    prec = (high - low) / (2 ** bits - 1)
    invPrec = 1/prec
    return int((n - low) * invPrec)

def pad(s, l, w, left = True):
    if left:
        s = w * (l - len(s)) + s
    else:
        s += w * (l - len(s))

 