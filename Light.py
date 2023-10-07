from Base import *
from Path import *


class LightPath(LinePath):
    def __init__(self, light, start, end):
        super().__init__(start, end)
        self.light : Light= light
        self.color = pygame.Color("green") if self.canGo() else pygame.Color("red")


    def tick(self, deltatime, simulation):
        self.color = pygame.Color("green") if self.canGo() else pygame.Color("red")

    def canGo(self):
        r = self.light.state["red"]
        y = self.light.state["yellow"]
        g = self.light.state["green"]
        return (g and not r)

    def advance(self, carId, dist):
        if self.canGo() or self.lineContainer.get_position(carId) > 0:
            # go
            return super().advance(carId, dist)
        else:
            # stop
            return self

    def getNextObstacleDist(self, objId):
        return self.getNextObstacleDistFrac(self.lineContainer.get_position(objId))
    
    def getNextObstacleDistFrac(self, frac):
        if not self.canGo() and frac == 0:
            return (self, 0)
        return super().getNextObstacleDistFrac(frac)

    def getAngle(self, objId):
        return super().getAngle(objId)
                

class Light(WorldObject):
    def __init__(self, pos, name):
        self.pos = {}
        self.state = {}

        self.pos["root"] = pos
        self.pos["red"] = [pos[0] + 11, pos[1] + 18]
        self.pos["yellow"] = [self.pos["red"][0], self.pos["red"][1] + 20]
        self.pos["green"] = [self.pos["red"][0], self.pos["red"][1] + 40]

        self.state["red"] = False
        self.state["yellow"] = False
        self.state["green"] = False

        self.name = name
       
    def loadSprite(self):
         self.sprite = load_image("trafficLight.png")

    def draw(self, screen):
        screen.blit(self.sprite,  self.pos["root"])
        if self.state["red"]:
            col = pygame.color.Color("firebrick1")
            pygame.draw.circle(screen, col , self.pos["red"], 8, 0)
        if self.state["yellow"]:
            col = pygame.color.Color("gold1")
            pygame.draw.circle(screen, col , self.pos["yellow"], 8, 0)
        if self.state["green"]:
            col = pygame.color.Color("chartreuse1")
            pygame.draw.circle(screen, col , self.pos["green"], 8, 0)

    def setColor(self, color, on):
        if color in self.state:
            self.state[color] = on
        else:
            raise Exception(f"Invalid light color: '{color}'. Valid values are: {self.state.keys()}")