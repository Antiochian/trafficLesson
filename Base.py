import os
import pygame

class IDGenerator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.id_counter = 0
        return cls._instance

    def get_next_id(self):
        self.id_counter += 1
        return self.id_counter
        
def load_image(name):
    path = os.path.join(os.getcwd(), name)
    return pygame.image.load(path).convert_alpha()


class WorldObject:
    def loadSprite(self):
        return

    def tick(self, deltatime, simulation):
        return

    def isDestroyed(self):
        return False
    
    def draw(self, screen):
        return