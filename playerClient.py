import numpy as np

class Player:
    def __init__(self, idx, x, y, state):
        self.idx = idx
        self.x = x 
        self.y = y
        self.state = state

        # get flip status using the lookAt vector
        self.state['flip'] = np.sign(self.state['lookAt'][0])

        self.state['headCenter'] = self.x + 2 * self.state['flip'], self.y + 3
    
    @staticmethod
    def interpolate(start, end, t, td = 2):
        """
            interpolation of a frame with another
        """
        ts = td

        x = start.x + (end.x - start.x) / ts * t
        y = start.y + (end.y - start.y) / ts * t
        
        state = start.state.copy()
        state['lookAt'] = [start.state['lookAt'][0] + (end.state['lookAt'][0] - start.state['lookAt'][0]) / ts * t,
        start.state['lookAt'][1] + (end.state['lookAt'][1] - start.state['lookAt'][1]) / ts * t
        ]

        return Player(start.idx, x, y, state)