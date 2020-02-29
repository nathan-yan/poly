class Frame:
    def __init__(self, idx, players, blocks, enemies = None):
        self.idx = idx
        self.players = players 
        self.blocks = blocks
    
    @staticmethod
    def interpolate(start, end, t, td = 2):
        """
            interpolation of a frame with another
        """
        ts = td

        idx = start.idx + t
        #t = 0

        players = []
        for p, p_ in zip(start.players, end.players):
            players.append([p[0] + (p_[0] - p[0]) / ts * t, 
                            p[1] + (p_[1] - p[1]) / ts * t,
                            p[2]])
        
        blocks = []
        for b, b_ in zip(start.blocks, end.blocks):
            blocks.append([b[0], 
                           b[1] + (b_[1] - b[1]) / ts * t, 
                           b[2] + (b_[2] - b[2]) / ts * t,
                           b[3] + (b_[3] - b[3]) / ts * t])
         
        
        return Frame(idx, players, blocks)