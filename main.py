#!/usr/bin/env python3
from Ant import Ant, AntHill
from Field import Field
from Vector import Vector, Vec2d, Vec3d, randomVec2d, randomVector
from random import random, randint
from time import sleep
import turtle as T

def signed_root(x):
    return ((-1)*(x < 0) + (x > 0)) * abs(x)**.5

def T_setup():
    # T.speed(1000)
    T.delay()
    T.ht()
    T.tracer(0, 0)
    T.onkeypress(lambda key: T.bye() if key == 'q' else None)

def draw_diagram(
    scores,
    left_lower = Vec2d(-600, 0),
    right_upper = Vec2d(-50, 300)
):
    if(len(scores) == 0):
        return

    LL = left_lower
    RU = right_upper
    #diagram lines
    T.pensize(1)
    lines = 5
    for i in range(lines + 1):
        height = (
            LL.y() * (lines-i) / lines +
            RU.y() *        i  / lines
        )
        label = i / lines * max(scores)

        T.pu(); T.goto(LL.x(), height)
        T.pd(); T.goto(RU.x(), height)
        T.write(round(label, 1))
    T.pu()
    T.goto(RU.x(), LL.y() - 10)
    T.write("|gen %i" % len(scores))
    #diagram
    T.pensize(2)
    T.pu()
    for i in range(len(scores)):
        t = i / len(scores)
        u = scores[i] / max(scores)
        x = LL.x() * (1 - t) + RU.x() * t
        y = LL.y() * (1 - u) + RU.y() * u
        T.goto(x, y)
        T.pd()
        T.write(round(scores[i]))

def run(
    field,
    ant_hill,
    steps = 10000,
    dt = .1,
    field_interval = 50,
    food_interval = 500,
    food_supply = 5,
    show = True,
    show_field_interval = 200,
    show_ant_interval = 50,
    scores = []
):
    field.clean(lambda i, j: Vec3d(0, 0, 0))
    ants = [
        Ant(field, ant_hill, ant_hill.home + randomVec2d() * 5)
        for _ in range(ant_hill.ant_num)
    ]
    scale = 10

    for s in range(steps):
        #simulate
        if(s % field_interval == 0):
            field.dissolve(
                decay_trail = ant_hill.decay_trail
            ) #smoothe and decay
        if(s % food_interval == 0):
            #place 25 new food
            field.place_food(randomVec2d() * field.size[0], Vec2d(food_supply**.5, food_supply**.5))
        for ant in ants:
            ant.move(dt)
        #visualize
        if(show and s % show_ant_interval == 0):
            if(s % show_field_interval == 0):
                T.clear()
                #draw field and hill
                field.show(T, scale, 1)
                ant_hill.show(T, scale)
                #draw scores
                draw_diagram(scores)
            #draw ants
            T.pensize(3)
            for ant in ants:
                ant.show(T, scale)
            T.update()
            # sleep(.01)
    return ant_hill.eaten

def main(
    ant_num = 20,
    size = 30,
    dt = .1,
    steps = 10000,
    field_interval = 50,
    food_interval = 300,
    food_supply = 9,
    show = True,
    show_field_interval = 1000,
    show_ant_interval = 100,
    alpha = .01
):
    #init
    field = Field(
        (size, size),
        decay_trail = .8,
        decay_food = .95
    )
    ant_hill = AntHill(
        ant_num,
        Vec2d([size / 2] * 2),
        field
    )
    T_setup()

    def run_abbr(ant_hill, scores):
        return run(
            field,
            ant_hill,
            steps,
            dt,
            field_interval,
            food_interval,
            food_supply,
            show,
            show_field_interval,
            show_ant_interval,
            scores
        )

    data = []
    scores = [run_abbr(ant_hill, [])]

    try:
        #read ant hill parameters
        curr = ant_hill.to_vector()
        while True:
            data += [[curr.__copy__(), scores[-1]]]
            #modify parameters
            step = randomVector(len(curr))
            step.scale(Vector([1, 1, .5, .5, .1, .5]))
            curr += step * alpha
            #set parameters
            ant_hill.from_vector(curr)
            ant_hill.eaten = 0
            #getting a new score and adjusting curr
            scores += [run_abbr(ant_hill, scores)]
            follow = signed_root(scores[-1] - scores[-2])
            print("the follow for the last step is: %.10f" % follow)
            curr += step * (
                (
                    follow - 1 #the -1 is for the step already taken
                ) * alpha
            )
            #reset if last score is < 20% of max score
            if(scores[-1] < .2 * max(scores)):
                ant_hill = AntHill(
                    ant_num,
                    Vec2d([size / 2] * 2),
                    field
                )
    except KeyboardInterrupt:
        print()
        print("DATA = [")
        print("\t" + ",\n\t".join([repr(d) for d in data]))
        print("]")

if __name__ == '__main__':
    main()
    input("[ENTER] to quit")
