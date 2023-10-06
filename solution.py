from trafficSim import *


def solution(s):
    s.setLight("green", True, "A")
    s.setLight("red", True, "B")
    s.wait(1)
    s.setLight("green", False, "A")
    s.setLight("yellow", True, "A")
    s.setLight("yellow", True, "B")
    s.wait(1)
    s.setLight("yellow", False, "A")
    s.setLight("red", True, "A")
    s.setLight("yellow", False, "B")
    s.setLight("red", False, "B")
    s.setLight("green", True, "B")
    s.wait(1)
    s.setLight("yellow", True, "A")
    s.setLight("yellow", True, "B")
    s.setLight("green", False, "B")
    s.wait(1)
    s.setLight("yellow", False, "B")
    s.setLight("yellow", False, "A")
    s.setLight("red", False, "A")
    return

def allGreen(s):
    s.setLight("green", True, "A")
    s.wait(1)

def allRed(s):
    s.setLight("green", False, "A")
    s.setLight("red", True, "A")
    s.wait(6)
    s.setLight("green", True, "A")
    s.setLight("red", False, "A")
    s.wait(2)
levelOne.run(solution, 15)