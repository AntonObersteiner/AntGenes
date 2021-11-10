from random import random

class Vector(object):
    def __init__(self, val = [0, 0]):
        super(Vector, self).__init__()
        self.val = val[:]
    def __repr__(self):
        return "Vector(" + ", ".join([str(v) for v in self.val]) + ")"
    def __str__(self):
        return "(" + ", ".join([str(v) for v in self.val]) + ")"
    def check_size(self, operand):
        if(len(operand.val) != len(self.val)):
            raise ValueError("The operand has size %i, the base has size %i." % (len(operand.val), len(self.val)))
    def __copy__(self):
        return Vector(self.val)
    def __len__(self):
        return len(self.val)
    def __getitem__(self, index):
        return self.val[index]
    def __setitem__(self, index, value):
        self.val[index] = value
    def __neg__(self):
        return self * -1
    def __iadd__(self, other):
        self.check_size(other)
        for i in range(len(self.val)):
            self.val[i] += other.val[i]
        return self
    def __add__(self, other):
        result = self.__copy__()
        result += other
        return result
    def __imul__(self, factor):
        for i in range(len(self.val)):
            self.val[i] *= factor
        return self
    def __mul__(self, factor):
        result = self.__copy__()
        result *= factor
        return result
    def __imod__(self, other):
        self.check_size(other)
        for i in range(len(self.val)):
            self.val[i] %= other.val[i]
        return self
    def __mod__(self, other):
        result = self.__copy__()
        result %= other
        return result
    def dot(self, other):
        self.check_size(other)
        result = 0
        for i in range(len(self.val)):
            result += self.val[i] * other.val[i]
        return result
    def normalize(self, size = 1.0):
        self *= size / abs(self)
    def __abs__(self):
        return self.dot(self)**.5
    def dist(self, other):
        return abs(self +- other)
    def clip(self, lower, upper = None):
        if(upper == None):
            upper = lower
            lower = Vector([0] * len(self.val))
        else:
            self.check_size(lower)
        self.check_size(upper)

        for i in range(len(self.val)):
            if(  self.val[i] < lower[i]):     self.val[i] = lower[i]
            elif(self.val[i] > upper[i]):     self.val[i] = upper[i]
        return self
    def scale(self, other):
        """multiplies the vector with the argument be element"""
        self.check_size(other)
        for i in range(len(self.val)):
            self.val[i] *= other.val[i]
        return self

class Vec2d(Vector):
    def __init__(self, x = [0, 0], y = 0):
        if(type(x) in [list, tuple]):
            super(Vec2d, self).__init__(x)
        elif(type(x) in [Vec2d, Vector]):
            super(Vec2d, self).__init__(x.val)
        else:
            super(Vec2d, self).__init__([x, y])
        if(len(self.val) != 2):
            raise ValueError("2D-Vector initialized with %i values: '%s'" %  (len(self.val), self.val))
    def cmul(self, other):
        self.check_size(other)
        return Vec2d(
            self.val[0] * other.val[0] - self.val[1] * other.val[1],
            self.val[0] * other.val[1] + self.val[1] * other.val[0]
        )
    def x(self):
        return self.val[0]
    def y(self):
        return self.val[1]

class Vec3d(Vector):
    def __init__(self, x = [0, 0, 0], y = 0, z = 0):
        if(type(x) in [list, tuple]):
            super(Vec3d, self).__init__(x)
        elif(type(x) in [Vec3d, Vector]):
            super(Vec3d, self).__init__(x.val)
        elif(type(x) in [Vec2d]):
            super(Vec3d, self).__init__(x.val + [0])
        else:
            super(Vec3d, self).__init__([x, y, z])
        if(len(self.val) != 3):
            raise ValueError("3D-Vector initialized with %i values: '%s'" %  (len(self.val), self.val))
    def cross(self, other):
        self.check_size(other)
        return Vec3d(
            self.val[1] * other.val[2] - self.val[2] * other.val[1],
            self.val[2] * other.val[0] - self.val[0] * other.val[2],
            self.val[0] * other.val[1] - self.val[1] * other.val[0]
        )
    def x(self):
        return self.val[0]
    def y(self):
        return self.val[1]
    def z(self):
        return self.val[2]

def randomVector(n = 3):
    if(n == 2):
        return Vec2d(
            2.0 * random() - 1,
            2.0 * random() - 1
        )
    elif(n == 3):
        return Vec3d(
            2.0 * random() - 1,
            2.0 * random() - 1,
            2.0 * random() - 1
        )
    return Vector([
        2.0 * random() - 1
        for _ in range(n)
    ])
def randomVec2d():
    return Vec2d(
        2.0 * random() - 1,
        2.0 * random() - 1
    )
def randomVec3d():
    return Vec3d(
        2.0 * random() - 1,
        2.0 * random() - 1,
        2.0 * random() - 1
    )

class VectorRange(object):
    def __init__(self, start, stop, step = None):
        super(VectorRange, self).__init__()
        self.len = len(start.val)

        self.start = start
        self.stop = stop
        if(step == None):
            self.step = Vector([1] * self.len)
        else:
            self.step = step

        self.stop.check_size(self.start)
        self.stop.check_size(self.step)

        self.curr = Vector(start)
        self.has_next = True
    def __iter__(self):
        while(self.__hasnext__()):
            yield self.__next__()
    def __next__(self):
        result = Vector(self.curr)
        #"imagine" next step already -> know when has_next should be False before call
        self.curr[self.len - 1] += self.step[self.len - 1]
        for i in range(self.len - 1, -1, -1):
            if((self.step[i] > 0) == (self.curr[i] < self.stop[i])):
                #incrementing didn't result in "overflow"
                break
            else:
                #index curr[i] has gone too far -> "overflows" into next index
                #reset the following indices of the counter
                for j in range(i, self.len):
                    self.curr[j] = self.start[j]
                #check next-highest index
                if(i > 0):
                    self.curr[i - 1] += self.step[i - 1]
                else:
                    self.has_next = False
        return result
    def __hasnext__(self):
        return self.has_next

class Vec2dRange(VectorRange):
    def __init__(self, start, stop, step = None):
        super(Vec2dRange, self).__init__(start, stop, step)
        if(self.len != 2):
            raise ValueError("Vec2dRange was initialized with non-2D Vectors! (start: %s, stop: %s, step: %s)" % (self.start, self.stop, self.step))
    def __iter__(self):
        i = self.start[0]
        while((self.step[0] > 0) == (i < self.stop[0])):
            j = self.start[1]
            while((self.step[1] > 0) == (j < self.stop[1])):
                yield Vec2d(i, j)
                j += self.step[1]
            i += self.step[0]
