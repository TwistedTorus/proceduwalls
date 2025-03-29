from segments import Segment, crumbling_edge
from mpl_toolkits import mplot3d

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


def verify_wall_code(wall_code):
    # invalid build codes, cant have multiple nodes along a corner index
    return True, []
def verify_floor_code(floor_code):
    return True, []

def equiv(n1, n2):
    return n1.x == n2.x and n1.y == n2.y and n1.z == n2.z

class Node:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"node({self.x},{self.y},{self.z})"
    def __repr__(self):
        return str(self)

def nodes_to_edges(nodes):
    edges = []
    for i in range(len(nodes) - 1):
        n1, n2 = nodes[i], nodes[i+1]
        edges.append((n1, n2))
    return edges

def edge_match(e1, e2):
    #print("comparing", e1[0],e1[1],e2[0],e2[1])
    return (equiv(e1[0], e2[0]) and equiv(e1[1], e2[1])) or (equiv(e1[0], e2[1]) and equiv(e1[1], e2[0]))

def create_connector(edge):
    n1, n2 = edge
    dx = n2.x - n1.x
    dy = n2.y - n1.y
    dz = n2.z - n1.z

    cn1 = Node(n1.x + dx/4, n1.y + dy/4, n1.z + dz/4)
    cn2 = Node(n1.x + 3*dx/4, n1.y + 3*dy/4, n1.z + 3*dz/4)

    return (n1, cn1), (cn1, cn2), (cn2,n2)

class Wall:

    def __init__(self, top_wall_nodes, bottom_wall_nodes):

        self.wall_nodes = top_wall_nodes+bottom_wall_nodes[::-1]


        self.twn = top_wall_nodes
        self.bwn = bottom_wall_nodes

        # derive a list of edges (which we can make into segments and crumbling edges eventually)
        self.wall_edges = nodes_to_edges(self.wall_nodes)
        # connecting edges. Connecting edges will have a standard format, 4 square cuts?
        self.connecter_edges = []
        # the edges which constitue part of a wall base.
        self.base_edges = nodes_to_edges(bottom_wall_nodes)

    def detect_floor_connection(self, floor):
        fl = floor.floor_level
        tfn = [ Node(n.x,n.y,fl) for n in self.bwn ]
        this_floor_edges = nodes_to_edges(tfn)
        for f1_edge in this_floor_edges:
            for f2_edge in floor.edges:
                if edge_match(f1_edge, f2_edge):
                    pre_c, c, post_c = create_connector(f1_edge)
                    self.connecter_edges.append(c)
                    floor.connecter_edges.append(c)
                    floor.replace_edge(f2_edge, [pre_c, c, post_c])
                    if not f2_edge in floor.non_free_edges:
                        floor.non_free_edges.append(f2_edge)
                        floor.non_free_edges.append(pre_c)
                        floor.non_free_edges.append(post_c)

    def sketch_3d(self, ax, opacity):
        x = [n.x for n in self.wall_nodes]
        y = [n.y for n in self.wall_nodes]
        z = [n.z for n in self.wall_nodes]
        ax.plot3D(x, y, z, 'green', alpha = opacity)

        for ce in self.connecter_edges:
            x = [n.x for n in ce]
            y = [n.y for n in ce]
            z = [n.z+3 for n in ce]
            ax.plot3D(x,y,z,'red', alpha = opacity)


    def __str__(self):
        s = "Wall(\n"
        for node in self.wall_nodes:
            s += f"  {str(node)}"
        return s + ")"
    def __repr__(self):
        return str(self)

class Floor:

    def __init__(self, nodes):
        self.nodes = nodes
        self.edges = nodes_to_edges(nodes)
        self.floor_level = nodes[0].z

        self.connecter_edges = []
        self.free_edges = []
        self.non_free_edges = []

    def __str__(self):
        s = "Floor(\n"
        for node in self.nodes:
            s += f"  {str(node)}"
        return s + ")"
    def __repr__(self):
        return str(self)

    def sketch_3d(self, ax, opacity):
        x = [n.x for n in self.nodes]
        y = [n.y for n in self.nodes]
        z = [n.z for n in self.nodes]
        ax.plot3D(x, y, z, 'grey', alpha = opacity)

        for ce in self.connecter_edges:
            x = [n.x for n in ce]
            y = [n.y for n in ce]
            z = [n.z+1.5 for n in ce]
            ax.plot3D(x,y,z,'yellow', alpha = opacity)
        for fe in self.free_edges:
            x = [n.x for n in fe]
            y = [n.y for n in fe]
            z = [n.z+1.5 for n in fe]
            ax.plot3D(x,y,z,'blue', alpha = opacity)

    def detect_free_edges(self):
        for edge in self.edges:
            if not edge in self.non_free_edges and not edge in self.connecter_edges:
                self.free_edges.append(edge)

    def replace_edge(self, edge, replacemnet_edges):
        new_edges = []
        for e in self.edges:
            if e != edge:
                new_edges.append(e)
            else:
                new_edges += replacemnet_edges
        self.edges = new_edges

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

        v_1 = (0,0)
        v_2 = (dimensions[0],0)
        v_3 = (dimensions[0],dimensions[1])
        v_4 = (0,dimensions[1])

        verts = [ v_1, v_2, v_3, v_4, v_1 ]

        self.corner_node_indexs = [ index for index in range(4*n_floors + 1) if index % n_floors == 0 ]
        self.base_nodes = []
        self.wall_bases = { 0:[], 1:[], 2:[], 3:[] }

        for i in range(4):
            vert = verts[i]
            from_to = verts[i], verts[i+1]
            dx = (verts[i+1][0] - verts[i][0])/n_floors
            dy = (verts[i+1][1] - verts[i][1])/n_floors
            for j in range(n_floors):
                x = vert[0] + j * dx
                y = vert[1] + j * dy
                z = 0
                bn = Node(x,y,z)
                self.base_nodes.append(bn)
                self.wall_bases[i].append(bn)

        n_x = self.base_nodes[0].x
        n_y = self.base_nodes[0].y
        n_z = self.base_nodes[0].z
        self.base_nodes.append(Node(n_x,n_y,n_z))
        for i, wb in self.wall_bases.items():
            if i == len(self.wall_bases.keys())-1:
                wb.append(self.wall_bases[0][0])
            else:
                wb.append(self.wall_bases[i+1][0])


    def wall_code_to_walls(self,wall_code):

        code_is_valid, errors = verify_wall_code(wall_code)
        if not code_is_valid:
            errors_str = str(errors)
            raise Exception( "Invalid Wall Code: " + errors_str )

        wall_node_codes = wall_code.split("-")
        wall_nodes = { 0:[], 1:[], 2:[], 3:[] }
        for wnc in wall_node_codes:

            nis, fis = wnc.split("/")
            node_index = int(nis)
            floor_index = int(fis)
            bn = self.base_nodes[node_index]
            z = floor_index * self.df
            wall_node = Node(bn.x,bn.y,z)
            print(wnc)
            print(wall_node)

            for wi,wall_base in self.wall_bases.items():
                if bn in wall_base:
                    wall_nodes[wi].append(wall_node)

        # now we have the node floor indexs,
        walls = []
        for i in range(4):
            print("wall",i)
            wn = wall_nodes[i]
            bn = self.wall_bases[i]
            if i == 3:
                wn = wn[1:] + [wn[0]]
            print(wn)
            print(bn)
            if len(wn) > 1:
                w = Wall(wn, bn)
                walls.append(w)
                print(w.wall_nodes)

        return walls

    def floor_code_to_floor(self, floor_code):

        code_is_valid, errors = verify_floor_code(floor_code)
        if not code_is_valid:
            errors_str = str(errors)
            raise Exception("Invalid Floor Code: "+errors_str)

        level_str, code_str = floor_code.split("-")
        nodes = [self.base_nodes[int(x)] for x in code_str.split("/")]
        level = int(level_str[1:])
        floor_nodes = []
        for n in nodes:
            floor_node = Node(n.x,n.y,level*self.df)
            floor_nodes.append(floor_node)
        return Floor(floor_nodes)

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

    def fit_walls_and_floors(self):

        for floor in self.floors:
            for wall in self.walls:
                wall.detect_floor_connection(floor)
            floor.detect_free_edges()



    def sketch_3d(self, ax, opacity=0.5):
        for wall in self.walls:
            wall.sketch_3d(ax, opacity)
        for floor in self.floors:
            floor.sketch_3d(ax, opacity)

        for i,bn in enumerate(self.base_nodes):
            if i == len(self.base_nodes)-1:
                dz = 8
            else:
                dz = 0
            ax.text(bn.x,bn.y,bn.z+dz,f"{str(i)}",color="black")

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

wc = "0/0-1/2-2/2-4/0-5/1-5/2-6/1-7/1-8/0"
fc1 = "f0-0/1/2/3/4/0"
fc2 = "f1-1/2/3/1"
fc3 = "f1-5/6/7/5"

b = Ruin( (200,100,100), 3)
b.generate_from_build_code(wc,[fc1,fc2,fc3])
b.fit_walls_and_floors()

ax = plt.axes(projection ='3d')

b.sketch_3d(ax)
plt.show()
