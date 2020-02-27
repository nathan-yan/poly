import numpy as np

class Player:
    def __init__(self, px):
        self.health = 100
        self.x = 0
        self.y = px.height - 20
    
        self.velVert = 0
        self.velPlayerHorz = 0
        self.velExternalHorz = 0

        # nc - normally close (false)
        # no - normally open (true)
        # t - toggleable
        self.state = {
            "nc": {
                "onGround" : False,
                "walking" : False,
                "emitter" : False
            },
            "no" : {},
            "t" : {}
        }