from Vector import Vector, Vec2d, Vec3d, Vec2dRange
from copy import deepcopy

close_neighbors = [
    Vec2d( 0, 1),
    Vec2d( 1, 0),
    Vec2d( 0,-1),
    Vec2d(-1, 0)
]
more_neighbors = close_neighbors + [
    Vec2d( 1, 1),
    Vec2d( 1,-1),
    Vec2d(-1,-1),
    Vec2d(-1, 1)
]

class Arr2D(object):
    def __init__(self, generate, I, J = None):
        super(Arr2D, self).__init__()
        #function generate: val = [[generate(i, j)]]
        self.generate = generate
        if(type(I) in [int, float]):
            self.size = Vec2d(I, J)
        else:
            self.size = Vec2d(I)

        self.val = [
            [generate(i, j) for j in range(self.size.y())]
            for i in range(self.size.x())
        ]
        self.type = type(self.generate(0, 0))
    def __getitem__(self, pos):
        at_i = int(pos[0]) % self.size.x()
        at_j = int(pos[1]) % self.size.y()
        return self.val[at_i][at_j]
    def clean(self, generate = None):
        if(generate == None):
            generate = self.generate
        self.val = [
            [generate(i, j) for j in range(self.size.y())]
            for i in range(self.size.x())
        ]

class Field(Arr2D):
    """an Ant Field is a 2D-Array of 3D-Vectors (x, y, z): (home trail, food trail, food)"""

    def __init__(self,
        arg = (100, 100),
        decay_trail = .8,
        decay_food = .95,
    ):
        self.decay_trail = decay_trail
        self.decay_food  = decay_food
        if(type(arg) in [list, tuple, Vector]):
            size = Vec2d(arg)
            super(Field, self).__init__(lambda i, j: Vec3d(), size)
        elif(isinstance(arg, (Field, Arr2D))):
            #maybe the argument is a Field or 2D-Array
            super(Field, self).__init__(lambda i, j: arg.__getitem__(Vec2d(i, j)), arg.size)
            if(isinstance(arg, Field)):
                self.decay_trail = arg.decay_trail
                self.decay_food  = arg.decay_food
        else:
            raise TypeError("The argument '%s' could not be used to create a Field object." % (arg))
    def __copy__(self):
        return Field(self)
    def dissolve(self, decay_food = None, decay_trail = None):
        if(decay_food == None):
            decay_food = self.decay_food
        if(decay_trail == None):
            decay_trail = self.decay_trail
        next_trails = Field(self)
        for ij in Vec2dRange(Vec2d(), self.size):
            #only affects home/food trails, not food itself
            for index in [0, 1]:
                next_trails[    ij][index] *= .4 #own previous value
                for dij in close_neighbors:
                    next_trails[ij][index] += self[ij + dij][index] * .15
                next_trails[    ij][index] *= decay_trail #exponential decay of trails
                if(next_trails[ ij][index] < 0.0001):
                    next_trails[ij][index] = 0
            #food
            next_trails[    ij][2] *= decay_food #food, fading exponentially as well
            if(next_trails[ ij][2] < 0.01):
                next_trails[ij][2] = 0
        self.val = next_trails.val
    def food_close(self, pos):
        for nbor in more_neighbors:
            if(self[pos + nbor].z()):
                return pos + nbor
        return None
    def follow_trail(self, pos, dir, has_food):
        result = Vec2d()
        for nbor in more_neighbors:
            if(has_food):
                result += nbor * self[pos + nbor].x() ** 2
            else:
                result += nbor * self[pos + nbor].y() ** 2
        if(abs(result) > 0):
            result.normalize()
        return result
    def take_food(self, pos):
        takable = min(1, self[pos][2])
        self[pos][2] -= takable
        return takable
    def place_food(self, at, size, steps = Vec2d(1, 1)):
        for ij in Vec2dRange(at, at + size, steps):
            self[ij][2] = 1
    def show(self, T, scale, dot = 1.0): #dot is relative to scale
        for ij in Vec2dRange(Vec2d(), self.size):
            color = (
                Vec3d(1, 1, 1) +-
                Vec3d(
                    self[ij][0] * .1,
                    self[ij][1] * .1,
                    self[ij][2]
                )
            )
            color.clip(Vec3d(0, 0, 0), Vec3d(1, 1, 1))
            if(abs(color)):
                T.pencolor(color.val)
                T.pu()
                T.goto(ij * scale)
                T.dot(dot * scale)
        #rectangle around the field
        T.color(0, 0, 0)
        l = -.5 * scale
        b = -.5 * scale
        r = scale * (self.size[0] - .5)
        t = scale * (self.size[1] - .5)
        T.pu()
        T.goto(l, b); T.pd()
        T.goto(r, b)
        T.goto(r, t)
        T.goto(l, t)
        T.goto(l, b)
