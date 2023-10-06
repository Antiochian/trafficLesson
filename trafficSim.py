import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pygame.locals import *

from Base import *
from Path import *
from Light import *
from Car import *

        
class Command:
    def __init__(self, name, cmd, *args):
        self.name = name
        self.cmd = cmd
        self.args = args

    def __str__(self):
        return f"{self.name}({', '.join([str(a) for a in self.args])})"
    
    def run(self):
        self.cmd(*self.args)

class TrafficSimulator:
    inst_ptr = 0
    instructions = []
    wait_time_s = 0
    curr_time_s = 0
    screen = None
    
    lights = {}
    def __init__(self, lights, drawables = [], tickables = []):
        for l in lights:
            self.lights[l.name] = l
        self.drawables = drawables
        self.tickables = tickables
        
    def setLight(self, color, on, light=None):
        if light:
            self.instructions.append( Command("setLight", self.__setLightImpl, color, on, light) )
        else:
            self.instructions.append( Command("setLight", self.__setLightImpl, color, on) )

    def wait(self, time):
        self.instructions.append( Command("wait",self.__waitImpl, time ))
    
    def __setLightImpl(self, color, on, name=None):
        if name is None:
            if len(self.lights) == 1:
                self.lights[list(self.lights.keys())[0]].setColor(color, on)
            else:
                raise Exception("Need to provide a name for setLight!")
        else:
            self.lights[name].setColor(color, on)
       

    def __waitImpl(self, time):
        self.wait_time_s = time


    def __nextInst(self):
        if self.inst_ptr < len(self.instructions):
            print(str(self.instructions[self.inst_ptr]))
            self.instructions[self.inst_ptr].run()
            self.inst_ptr += 1
            if self.inst_ptr == len(self.instructions):
                self.inst_ptr = 0
                print("(repeat)")

    def __runInstructions(self, max_time):
        self.curr_time_s = 0
        clock = pygame.time.Clock()

        background = load_image('bg.png')
        while  self.curr_time_s < max_time and ( self.inst_ptr < len(self.instructions) or self.wait_time_ms > 0):
            # seconds deltatime
            deltatime = clock.tick() / 1000
            for event in pygame.event.get():
                if event.type in (QUIT, KEYDOWN):
                    return
            while self.wait_time_s <= 0:
                self.__nextInst()

            i = 0
            while i < len(self.tickables):
                self.tickables[i].tick(deltatime, self)
                if self.tickables[i].isDestroyed():
                    self.tickables.pop(i)
                else:
                    i += 1
            # Draw bg
            self.screen.blit(background, (0, 0))
            # Draw stuff
            i = 0
            while i < len(self.drawables):
                if self.drawables[i].isDestroyed():
                    self.drawables.pop(i)
                else:
                    self.drawables[i].draw(self.screen)
                    i += 1
            for d in self.drawables:
                d.draw(self.screen)
            pygame.display.update()
            
            self.curr_time_s += deltatime
            if self.wait_time_s > 0:
                self.wait_time_s -= deltatime
        print("Finished after {:.1f}s".format(self.curr_time_s))
    
    def run(self, loop_func, max_time):
        loop_func(self)
        # pygame setup code here I guess
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        for d in self.drawables:
            d.loadSprite()   
        # end pygame setup
        self.inst_ptr = 0
        self.__runInstructions(max_time)
         
        pygame.quit()
        sys.exit()


lightA = Light([170, 50], "A")
lightB = Light([430, 50], "B")
lights = [lightA, lightB]

paths = []
path1 = LinePath(pygame.math.Vector2(321, 100), pygame.math.Vector2(321, 235))
path2 = LightPath(lightA, pygame.math.Vector2(321, 235), pygame.math.Vector2(321, 300))
path3 = BezierPath(pygame.math.Vector2(321, 300), pygame.math.Vector2(360, 350), pygame.math.Vector2(321, 350), pygame.math.Vector2(321, 350))
path4 = LinePath(pygame.math.Vector2(360, 350),  pygame.math.Vector2(560, 350))

paths = [path1, path2, path3, path4]
for i in range(len(paths)-1):
    paths[i].nextPath = paths[i+1]

spawner = Spawner(paths[0])

levelOne = TrafficSimulator(lights, drawables=lights + paths + [spawner], tickables=paths + [spawner])

