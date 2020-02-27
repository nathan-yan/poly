import numpy as np

class Platform:
    def __init__(self, x, y, w, h, friction = 0.9, elasticity = 0.9):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.friction = friction
        self.elasticity = elasticity

    def draw(self, px, ox, oy):
        px.rect(self.x + ox, self.y + oy, self.w, self.h, 1 )
    
    def within(self, x, y):
        return self.x - 1 <= x <= self.x + self.w + 1 and self.y - 1 <= y <= self.y + self.h + 1

    def checkPlayerCollision(self, playerX, playerY, hitboxW, hitboxH):
        return [self.within(playerX, playerY), self.within(playerX + hitboxW, playerY), self.within(playerX, playerY + hitboxH), self.within(playerX + hitboxW, playerY + hitboxH)]
        # top left, top right, bottom left, bottom right