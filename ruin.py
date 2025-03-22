from segments import Segment, crumbling_edge
import matplotlib.pyplot as plt
import svg

## this script generates a corner svg that is very cuttoutable.
#
#seg_1 = crumbling_edge((95,100),(0,0))
#seg_2 = Segment((0,0),(200,0))
#seg_3 = crumbling_edge((200,0),(105,100))
#seg_4 = Segment((105,100),(95,100))
#
#cut = Segment((100,100),(100,0))
#cut.zigify(2.5)
#
#corner_seg = Segment((95,100),(0,0))
#corner_seg.child_segments = [seg_1, seg_2, seg_3, seg_4]
#corner_seg.fuse_children()
#
#print(to_svg([corner_seg.points, cut.points]))


def to_svg(traces):
    elem = []
    for trace in traces:
        p = []
        for t in trace:
            p.append(t[0])
            p.append(t[1])
        trace_polygon = svg.Polyline(
                    points=p,
                    stroke="orange",
                    #fill="transparent",
                    stroke_width=1)
        elem.append(trace_polygon)
    return svg.SVG( width = 250, height = 250, elements = elem)

def verify_wall_code(wall_code):
    # invalid build codes, cant have multiple nodes along a corner index
    return True, []
def verify_floor_code(floor_code):
    return True, []

class Node:
    def __init__(self, x, y, l):
        self.x = x
        self.y = y
        self.l = l

    def __str__(self):
        return f"Node(x:{self.x},y:{self.y},l:{self.l})"
    def __repr__(self):
        return str(self)

def wall_from_segments(segments):
    if segments == []:
        return None
    l1 = (segments[0].start[0],0)
    l2 = (segments[0].start[0],segments[0].start[1])
    left = Segment(l1, l2)

    r1 = (segments[-1].end[0],0)
    r2 = (segments[-1].end[0],segments[-1].end[1])
    right = Segment(r2, r1)

    bottom = Segment(r1, l1)
    top = segments

    return Wall([left], [right], [bottom], top)

class Wall:
    def __init__(self,left,right,bottom,top):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.segments = self.left + self.top + self.right + self.bottom

    def sketch(self, ax):
        for seg in self.segments:
            seg.sketch(ax)

    def __str__(self):
        return f"Wall()"
    def __repr__(self):
        return str(self)

class Floor:
    def __init__(self, nodes, level):
        self.nodes = nodes
        self.level = level

class Ruin:
    '''
    To do: Windows, and interlocking teeth stuff.
    '''
    def __init__(self, dimensions, thickness, floors = 2):
        '''
        dimensions are in x, y, z (z is height)
        creates n_floors * 4 nodes

            0-1-2
            |   |
            7   3
            |   |
            6-5-4

        dimensions defines the outer size of the ruin, so a thickness > 0 will define the size
        of the interlock cuts.

        '''
        self.dimensions = dimensions
        self.n_floors = floors
        n_floors = floors
        self.walls  = []
        self.floors = []

        self.df = dimensions[2]/floors

        l_1 = (0,dimensions[0])
        l_2 = (l_1[1], l_1[1] + dimensions[1])
        l_3 = (l_2[1], l_2[1] + dimensions[0])
        l_4 = (l_3[1], l_3[1] + dimensions[1])

        v_1 = (0,0)
        v_2 = (dimensions[0],0)
        v_3 = (dimensions[0],dimensions[1])
        v_4 = (0,dimensions[1])

        lengs = [ l_1, l_2, l_3, l_4 ]
        verts = [ v_1, v_2, v_3, v_4, v_1 ]

        self.corner_node_indexs = [ index for index in range(4*n_floors + 1) if index % n_floors == 0 ]
        self.nodes = []

        for i in range(4):
            vert = verts[i]
            leng = lengs[i]
            from_to = verts[i], verts[i+1]
            dx = (verts[i+1][0] - verts[i][0])/n_floors
            dy = (verts[i+1][1] - verts[i][1])/n_floors
            dl = (leng[1]-leng[0])/n_floors
            for j in range(n_floors):
                x = vert[0] + j * dx
                y = vert[1] + j * dy
                l = leng[0] + j * dl
                self.nodes.append(Node(x,y,l))
        n_x = self.nodes[0].x
        n_y = self.nodes[0].y
        self.nodes.append(Node(n_x,n_y,l_4[1]))


    def wall_code_to_walls(self,wall_code):

        code_is_valid, errors = verify_wall_code(wall_code)
        if not code_is_valid:
            errors_str = str(errors)
            raise Exception("Invalid Wall Code: "+errors_str)

        wall_node_codes = wall_code.split("-")
        node_floor_indexs = []
        for wnc in wall_node_codes:
            nis, fis = wnc.split("/")
            node_index = int(nis[:])
            floor_index = int(fis[:])
            node_floor_indexs.append((node_index, floor_index))
        # now we have the node floor indexs,

        segments = []
        walls = []
        wall_started = False

        i = 0
        for i in range(len(node_floor_indexs)-1):

            ni1, fi1 = node_floor_indexs[i]
            ni2, fi2 = node_floor_indexs[i+1]
            l1 = self.nodes[ni1].l
            l2 = self.nodes[ni2].l
            h1 = fi1 * self.df
            h2 = fi2 * self.df

            if ni1 in self.corner_node_indexs:
                print("new wall starting from", ni1)
                w = wall_from_segments(segments)
                if w != None:
                    walls.append(w)
                segments = []

            #seg = Segment((l1,h1),(l2,h2))
            seg = crumbling_edge((l1,h1),(l2,h2))
            print(ni1,fi1,ni2,fi2)
            print(seg)
            segments.append(seg)
        if segments != []:
            w = wall_from_segments(segments)
            walls.append(w)

        return walls

    def floor_code_to_floor(self, floor_code):

        code_is_valid, errors = verify_floor_code(floor_code)
        if not code_is_valid:
            errors_str = str(errors)
            raise Exception("Invalid Floor Code: "+errors_str)

        level_str, code_str = floor_code.split("-")
        nodes = [self.nodes[int(x)] for x in code_str.split("/")]
        level = int(level_str[1:])
        return Floor(nodes,level)


    def generate_from_build_code(self, wall_code, floor_codes):
        '''
        wall code 8 point code N0F0,N1F2,N2F2,N3F1
        floor code format: [0,1,2,3,0] we know that 3,0 overhangs empty space

        '''
        self.walls = self.wall_code_to_walls(wall_code)
        self.floors = []
        for fc in floor_codes:
            floor = self.floor_code_to_floor(fc)
            self.floors.append(floor)

'''
basic ruins:
    1. a corner piece with a bit of first floor
    2. a half building with a first floor
    3. a fully enclosed building, with a complete floor on the roof (bunker?)
    4. a two part ruin, a corner and a half building? <- maybe this should be
       considered invalid. Should be defined as two ruins.
'''

# format: Gi/Fi-
wc = "0/0-1/2-2/2-4/0"
#wc = "0/0-1/2-2/2-3/0-4/1"

#wc = "0/0-1/2-2/2-4/0-5/1-5/2-6/1-7/1-8/0"
fc1 = "f0-0/2/4/0"
fc2 = "f1-1/2/3/1"

b = Ruin( (200,100,100), 3)
b.generate_from_build_code(wc,[fc1,fc2])
