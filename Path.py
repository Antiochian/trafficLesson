import pygame
from collections import deque
import bisect
import os
import math
from Base import *
INT_MAX = 999999999999999999999999

class LineMap:
    def __init__(self):
        self.objects : dict[ int : [WorldObject, float]]= {} # ID : (Object, position)
        self.sorted_ids : list[tuple[float, int]]= [] # (position, ID)

    def increment(self, objId : int, delta : float) -> (float, bool): # returns fractional distance ACTUALLY moved
        old_position = self.objects.get(objId)[1]

        actual_delta = min(1 - old_position, delta)
        new_position = old_position + actual_delta

        self.objects[objId][1] = new_position
        self.sorted_ids.remove((old_position, objId))
        bisect.insort(self.sorted_ids, (new_position, objId))
        return actual_delta, (actual_delta < delta)

    def add(self, objId : int, object : WorldObject):
        self.objects[objId] = [object, 0]
        bisect.insort(self.sorted_ids, (0, objId))

    def remove(self, objId : int):
        position = self.objects.pop(objId, [None])[1]
        self.sorted_ids.remove((position, objId))
    
    def get_position(self, objId : int) -> float:
        return self.objects[objId][1]
    
    def get_obj_position_tuple(self, objId : int) -> list[WorldObject, float]:
        return self.objects[objId]

    def get_next_from_position(self, position : float) -> list[WorldObject, float]:
        idx = bisect.bisect(self.sorted_ids, (position, INT_MAX))
        return self.sorted_ids[idx][1] if idx < len(self.sorted_ids) else None
    
    def contains(self,  objId : int) -> bool:
        for _, id in self.sorted_ids:
            if objId == id:
                return True
        return False


class Path(WorldObject):
    color = pygame.Color("white")
   
    # slow, use for debug only!!
    def draw(self, screen):
        step = 0.01
        pygame.draw.lines(screen, self.color, False, [self.fracToWorldPos(d/10) for d in range(0, 11)])

    def __init__(self, parametrizeFunc, scale : float):
        self.parametrizeFunc = parametrizeFunc
        self.lineContainer = LineMap()
        self.scale = scale
        self.nextPath = None

    def getAngle(self, objId):
        # get frac position
        frac = self.lineContainer.get_position(objId)
        # test up and down
        t0 = max(0, frac - 0.01)
        t1 = min(1, frac + 0.01)

        return pygame.math.Vector2(0, 1).angle_to(self.parametrizeFunc(t0) - self.parametrizeFunc(t1))
        
    def registerCar(self, car):
        carId = car.getId()
        assert(not self.lineContainer.contains(carId))
        self.lineContainer.add(carId, car)


    def getNextObstacleDist(self, objId) -> (WorldObject, float):
        return self.getNextObstacleDistFrac(self.lineContainer.get_obj_position_tuple(objId)[1])
    
    def getNextObstacleDistFrac(self, frac) -> (WorldObject, float):
        res = self.lineContainer.get_next_from_position(frac)
        if res is None:
            if self.nextPath:
                obj, nextDist = self.nextPath.getNextObstacleDistFrac(-1)
                return (obj, (1-frac)*self.scale + nextDist)
            else:
                return (None, -1)
        (obj, position) = self.lineContainer.get_obj_position_tuple(res)
        return (obj, (position- frac) * self.scale)
    

    def advance(self, carId, dist):
        frac_dist = dist / self.scale
        # convert dist to fractional dist
        frac_moved, finished = self.lineContainer.increment(carId, frac_dist)
        
        if finished:            
            # Car has left this path
            dist_moved = frac_moved * self.scale
            car, _ = self.lineContainer.get_obj_position_tuple(carId)
            self.lineContainer.remove(carId)
            if self.nextPath:
                self.nextPath.registerCar(car)
                return self.nextPath.advance(carId, dist - dist_moved)
            else:
                return None
        return self
        

    def fracToWorldPos(self, frac):
        return self.parametrizeFunc(frac)
    
    def getWorldPos(self, carId):
        return self.fracToWorldPos(self.lineContainer.get_obj_position_tuple(carId)[1])


class LinePath(Path):
    def __init__(self, start : pygame.math.Vector2, end : pygame.math.Vector2):
        scale = start.distance_to(end)
        super().__init__(self.parametrize, scale)
        self.start = start
        self.end = end

    def parametrize(self, frac) -> pygame.math.Vector2:
        return self.start.lerp(self.end, frac)


class BezierPath(Path):
    sample_step = 0.001
    def __init__(self, start: pygame.math.Vector2, end: pygame.math.Vector2, cp1 : pygame.math.Vector2, cp2 : pygame.math.Vector2):
        self.start = start
        self.end = end

        self.cp1 = cp1
        self.cp2 = cp2

        # Calculate the arc length function
        num_samples = 1000
        arc_lengths = [0.0]
        prev_point = self.bezier_parametrize(0)
        t = self.sample_step
        while t <= 1:
            point = self.bezier_parametrize(t)
            arc_lengths.append(arc_lengths[-1] + prev_point.distance_to(point))
            prev_point = point
            t += self.sample_step

        total_length = arc_lengths[-1]

        # Normalize the arc lengths to [0, 1]
        self.normalized_arc_lengths = [length / total_length for length in arc_lengths]

        super().__init__(self.arc_length_parametrize, total_length)

    def arc_length_parametrize(self, s) -> pygame.math.Vector2:
        # Find the closest lower and upper normalized arc lengths
        lower_index = bisect.bisect_right(self.normalized_arc_lengths, s) - 1
        upper_index = lower_index + 1

        if upper_index >= len(self.normalized_arc_lengths):
            lerp = 0
        else:
            weight = (s - self.normalized_arc_lengths[lower_index])/(self.normalized_arc_lengths[upper_index] - self.normalized_arc_lengths[lower_index])
            lerp = pygame.math.lerp(self.normalized_arc_lengths[lower_index], self.normalized_arc_lengths[upper_index], weight)

        # Find the corresponding t value for the interpolated s
        t = lower_index / len(self.normalized_arc_lengths)
        adj_t = t + lerp *  self.sample_step
        return self.bezier_parametrize(adj_t)

    def bezier_parametrize(self, t) -> pygame.math.Vector2:
        return (1 - t)**3 * self.start + 3 * (1 - t)**2 * t * self.cp1 + 3 * (1 - t) * t**2 * self.cp2 + t**3 * self.end
