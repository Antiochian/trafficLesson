from Path import *


class Spawner(WorldObject):
    spacing = 100
    def __init__(self, entryPath : Path):
        self.entryPath : Path = entryPath
    
    def tick(self, deltatime, simulation):
        dist = self.entryPath.getNextObstacleDistFrac(0)
        if dist < 0 or dist > self.spacing:
            # spawn
            newCar = Car(self.entryPath)
            newCar.loadSprite()
            simulation.tickables.append(newCar)
            simulation.drawables.append(newCar)

        
class Car(WorldObject):
    sprite_size = pygame.math.Vector2(64, 64)
    currPath = None
    max_speed = 50
    spacing = 70 # STOP when this close to a car ahead
    accel = 10

    def __init__(self, initial_path : Path, initial_displ = 0):
        self.currPath = initial_path
        self.id = IDGenerator().get_next_id()
        self.prev_sprite_idx = -1

        self.curr_speed = self.max_speed

        self.currPath.registerCar(self.id)
        if initial_displ:
            self.currPath = self.currPath.advance(self.id, initial_displ)

    def getPos(self):
        if self.currPath:
            return self.currPath.getWorldPos(self.id)
        else:
            return None
    
    def isFinished(self):
        return bool(self.currPath)
    
    def isDestroyed(self):
        return (self.currPath == None)

    def tick(self, deltatime, simulation):
        if self.currPath:
            next_obstacle = self.currPath.getNextObstacleDist(self.id)
            
            if next_obstacle < 0:
                # unobstructed, speed up
                self.curr_speed += self.accel*deltatime
            elif next_obstacle < self.spacing:
                # stop!
                self.curr_speed = 0
            else:
                # Calculate the slowing distance based on current speed, acceleration, and next obstacle distance
                slowing_dist = (self.curr_speed*self.curr_speed) / (2 * self.accel) 
                if next_obstacle < slowing_dist + self.spacing:
                    # Slow down
                    self.curr_speed -= self.accel*deltatime
                else:
                    # unobstructed, speed up
                    self.curr_speed += self.accel*deltatime
            
            self.curr_speed = min(self.max_speed, max(self.curr_speed, 0))
            self.currPath = self.currPath.advance(self.id, self.curr_speed*deltatime)
        
    def draw(self, screen):
        if self.currPath is None:
            return

        pos = self.getPos()
        orig_angle = self.currPath.getAngle(self.id)
        angle = (orig_angle + 360) % 360

        sprite_idx = int((angle + 22.5 )/ 45)
        if sprite_idx == 8:
            sprite_idx = 0
        if sprite_idx != self.prev_sprite_idx:
            print(f"Original angle: {orig_angle} -> normalised: {angle} -> spriteIDX: {sprite_idx}")
            self.prev_sprite_idx = sprite_idx
        if pos is not None:
            screen.blit(self.sprite,  pos -  self.sprite_size/2, pygame.Rect((sprite_idx * self.sprite_size[0], 0), self.sprite_size))

    def loadSprite(self):
        path = os.path.join(os.getcwd(), "car.png")
        self.sprite = pygame.image.load(path).convert_alpha()
