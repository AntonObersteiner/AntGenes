
from math import sin, cos
from Vector import Vector, Vec2d, Vec3d, randomVec2d

class AntHill(object):
    def __init__(self,
        ant_num,
        home,               #Vec2d, where the ants bring the food
        field,              #the field in which this hill operates
        home_start = 3,     #how many seconds an ant will mark that it was near home
        food_start = 1,     #how long it will mark that is found food
        walk_wander = .4,   #weight of random walking
        walk_straight=.7,   #weight of straight walking
        walk_trail  = .05,  #weight of the trail
        decay_trail = .8    #exponential decay of trails
    ):
        super(AntHill, self).__init__()
        self.ant_num = ant_num
        self.home = home
        self.home_start = home_start
        self.food_start = food_start
        self.walk_wander = walk_wander
        self.walk_straight = walk_straight
        self.walk_trail = walk_trail
        self.decay_trail = decay_trail
        self.eaten = 0
        self.field = field
        self.normalize_walk()
        self.clamp_decay()
    def normalize_walk(self):
        walk = Vec3d(self.walk_wander, self.walk_straight, self.walk_trail)
        walk.normalize()
        self.walk_wander    = walk[0]
        self.walk_straight  = walk[1]
        self.walk_trail     = walk[2]
    def clamp_decay(self):
        self.decay_trail    = max(0, min(1, self.decay_trail))
    def to_vector(self):
        return Vector([
            self.home_start, self.food_start,
            self.walk_wander, self.walk_straight, self.walk_trail,
            self.decay_trail
        ])
    def from_vector(self, vec):
        self.home_start     = vec[0]
        self.food_start     = vec[1]
        self.walk_wander    = vec[2]
        self.walk_straight  = vec[3]
        self.walk_trail     = vec[4]
        self.decay_trail    = vec[5]
        self.normalize_walk()
        self.clamp_decay()
    def to_dict(self):
        return {
            "ant_num": self.ant_num,
            "home": self.home,
            "home_start": self.home_start,
            "food_start": self.food_start,
            "walk_wander": self.walk_wander,
            "walk_straight": self.walk_straight,
            "walk_trail": self.walk_trail,
            "decay_trail": self.decay_trail,
            "eaten": self.eaten
        }
    def show(self, T, scale):
        #home circle
        T.color(0, 0, 0)
        T.pu()
        T.goto(
            scale * (self.home[0] - .5),
            scale * (self.home[1] - 3.5)
        )
        T.pd()
        T.setheading(0)
        T.circle(3 * scale)
        T.pu()
        T.back(.5 * scale)
        T.write(round(self.eaten, 1))
        #parameters on the right
        line = 1
        D = self.to_dict()
        for key in D.keys():
            T.goto(
                scale * (self.field.size.x() + 1.5),
                scale * (self.field.size.y() - 1.5 * line)
            )
            T.write("%s: %s" % (key, D[key]))
            line += 1

class Ant(object):
    def __init__(self, field, hill, pos = (0, 0)):
        super(Ant, self).__init__()
        self.field = field
        self.hill = hill
        try:
            self.pos = Vec2d(pos[0], pos[1])
        except:
            raise ValueError("Argument pos (type '%s') is not usable for a 2D-Vector (valid are: tuple, list or Vector)!" % type(pos))
        self.food = 0
        self.food_ago = 0
        self.home_ago = self.hill.home_start
        self.dir = Vec2d(0, 0) #current direction
    def move(self, dt = 1):
        #dt = time step
        #sample field
        if(not self.food):
            #check to see food
            near_food = self.field.food_close(self.pos)
            if(near_food != None):
                self.food = self.field.take_food(near_food)
                self.food_ago = self.hill.food_start
                self.home_ago = 0
        elif(self.food and self.pos.dist(self.hill.home) < 3):
            #check to bring food home
            self.hill.eaten += self.food
            self.food = 0
            self.home_ago = self.hill.home_start
            self.food_ago = 0

        #determine move direction
        dir_trail = self.field.follow_trail(self.pos, self.dir, self.food)
        self.dir = (
            self.dir *      self.hill.walk_straight +
            dir_trail *     self.hill.walk_trail +
            randomVec2d() * self.hill.walk_wander
        )
        self.dir.normalize()
        self.pos += self.dir * dt

        if(self.home_ago > 0):
            self.field[self.pos][0] += self.home_ago * dt
            self.home_ago -= dt
        if(self.food_ago > 0):
            self.field[self.pos][1] += self.food_ago * dt
            self.home_ago -= dt

        self.pos %= self.field.size
    def show(self, T, scale):
        if(self.home_ago > 0):
            color = Vec3d(.5, 0, 0) * (self.home_ago / self.hill.home_start)
        elif(self.food_ago > 0):
            color = Vec3d(0, .5, 0) * (self.food_ago / self.hill.food_start)
        else:
            color = Vec3d(.5, .5, .5)
        T.color(color.val)
        T.pu()
        T.goto((self.pos * scale).val)
        T.pd()
        T.goto(((self.pos +- self.dir) * scale).val)
