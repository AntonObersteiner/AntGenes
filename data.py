#!/usr/bin/env python3

from data_1 import *

StartHome   = [d[0][0] for d in DATA]
StartFood   = [d[0][1] for d in DATA]
WalkWander  = [d[0][2] for d in DATA]
WalkStraight= [d[0][3] for d in DATA]
WalkTrail   = [d[0][4] for d in DATA]
DecayTrail  = [d[0][5] for d in DATA]
Score       = [d[1]    for d in DATA]

from matplotlib import pyplot as P

# P.plot(Score, WalkTrail, "+"); P.show()
# P.plot(StartFood, StartHome, "+:b"); P.show()

from Vector import Vec2d, Vec3d
import turtle as T

def mapped(Values, index):
    return (Values[i] - min(Values)) / (max(Values) - min(Values))
T.tracer(0, 0)
T.delay(0)
T.ht()
T.pu()
for i in range(len(DATA)):
    color = Vec3d(
        mapped(WalkWander, i),
        mapped(WalkStraight, i),
        mapped(WalkTrail, i)
    )
    T.pencolor(color.val)
    x = 1000 * mapped(Score, i) - 500
    y = 600 * mapped(DecayTrail, i) - 300
    T.goto(x, y)
    T.pd()
T.update()
input("[ENTER] to quit")
