import matplotlib.pyplot as plt
import math
import random

def dot(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1]

def diff(v1, v2):
    return (v1[0]-v2[0], v1[1]-v2[1])

def plus(v1, v2):
    return (v1[0]+v2[0], v1[1]+v2[1])

def perp(vec):
    #[[0, 1]  [x]
    # [1,0]] [y]
    return (vec[1], vec[0])

def magn(vec):
    return (vec[0]**2 + vec[1]**2)**0.5

class Segment:

    def __init__(self, start, end, up = (0,1)):
        self.child_segments = []
        self.start = start
        self.end   = end
        self.up    = up
        self.points = [start, end]

    def sketch(self, ax, line_colour='k-'):
        if self.child_segments == []:
            x_p = [p[0] for p in self.points]
            y_p = [p[1] for p in self.points]
            ax.plot(x_p, y_p, line_colour)
            #ax.plot([x_p[0],x_p[-1]],[y_p[0],y_p[-1]])
        for seg in self.child_segments:
            seg.sketch(ax)

    def chunk(self, n_chunks, noise):
        if 1/n_chunks < noise:
            raise Exception("Error chunk to noise ratio too high.")
        self.child_segments = []
        # step 1: define points along the original segment
        base_points = []
        x_inc = (self.end[0] - self.start[0])/n_chunks
        y_inc = (self.end[1] - self.start[1])/n_chunks
        for i in range(n_chunks-1):
            x = self.start[0] + x_inc*(i+1)
            y = self.start[1] + y_inc*(i+1)
            base_points.append((x,y))
        r1, r2 = self.start, self.end
        L = magn(diff(r1, r2))
        # step 2: nudge the base points off of their original position.
        nudged_points = []
        for bp in base_points:
            a = random.random()
            b = random.random()
            l = a * L * noise
            theta = 2*math.pi*b
            delta = (l*math.cos(theta), l*math.sin(theta))
            np = (bp[0] + delta[0], bp[1] + delta[1])
            nudged_points.append(np)
        # step 3: create new segments
        points = [self.start] + nudged_points + [self.end]
        for i in range(len(points)-1):
            p1,p2 = points[i], points[i+1]
            seg = Segment(p1,p2,self.up)
            self.child_segments.append(seg)

    def recursively_chunk(self, n_chunks, noise):
        if self.child_segments == []:
            self.chunk(n_chunks, noise)
        else:
            for child_seg in self.child_segments:
                child_seg.recursively_chunk(n_chunks, noise)

    def fuse_children(self, show = False):
        # converts all the children into a single bumpy segment
        # may make reading the final result easier.
        if self.child_segments == []:
            return

        self.points = [self.start]
        for child_seg in self.child_segments:
            child_seg.fuse_children()
            self.points += child_seg.points[1:]

        self.child_segments = []

    def brickify(self, brick_l, brick_h):
        # makes the line brickish.
        x1,y1 = self.start
        x2,y2 = self.end
        # step 1 work out the direction to build the wall.
        # brick_l is brick length, bricks are always flat.
        d_h =  [ brick_h * x for x in self.up ]
        d_l =  [ brick_l * x for x in  perp(self.up) ]

        if dot(d_l, diff(self.end, self.start)) < 0:
            d_l = [ -1 * x for x in d_l ]
        if dot(d_h, diff(self.end, self.start)) < 0:
            d_h = [ -1 * x for x in d_h ]

        l_budget = math.floor(abs((x2 - x1)/magn(d_l)))
        h_budget = math.floor(abs((y2 - y1)/magn(d_h)))
        curr_point = (x1,y1)
        brick_points = [curr_point]
        while l_budget > 0 or h_budget > 0:
            p = random.random()
            f = p > 0.5
            if f and l_budget > 0:
                l_budget -= 1
                brick_points.append(plus(curr_point, d_l))
            if not f and h_budget > 0:
                brick_points.append(plus(curr_point, d_h))
                h_budget -= 1
            curr_point = brick_points[-1]
        self.points = [self.start] + brick_points + [self.end]

def crumbling_brick_wall(start, end):
    def roughen(segment, level):
        i = 0
        while i < level:
            i += 1
            segment.recursively_chunk(3,0.2)
    #step 1 break into 5 chunks at noise level 0.1
    N = 6
    base = Segment(start, end)
    base.chunk(N,0.1)
    unit = magn(diff(start,end)) * 0.02
    for i, seg in enumerate(base.child_segments):
        n = random.random()
        if n > 0.5 or i == 0 or i == N-1:
            roughen(seg,2)
            seg.fuse_children()
        else:
            seg.brickify(1*unit,1*unit)
    return base


if __name__=="__main__":

    fig, ax = plt.subplots()

    for i in range(8):
        crumble = crumbling_brick_wall((0,0), (100,100))
        crumble.sketch(ax, line_colour = 'k-')

    plt.show()


