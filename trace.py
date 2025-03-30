from segments import Segment, crumbling_edge

def flatten_node(node, normal):
    norm = (int(round(i)) for i in normal)
    v = (node.x, node.y, node.z)
    r = []
    flip = False
    for n,x in zip(norm, v):
        if n == 0:
            r.append(x)
        if n == -1:
            flip = True
    if flip:
        r[0] = -r[0]
    return (r[0],r[1])

def flatten(edge, normal):
    return tuple([flatten_node(n,normal) for n in edge])

def wall_to_trace(wall):

    print(wall.normal)
    segments = []
    #for edge in wall.wall_edges:
    #    flat_edge = Segment(*flatten(edge, wall.normal))
    #    segments.append(flat_edge)

    # handling the outline:
    # handle wall connecting edges (will be zigified).
    # handle base edges (kept straight).
    # handle free edges (add crumble effect).

    # cuts for extra bits:

    free_edges = []
    connecting_edges = []
    base_edges = []

    for edge in wall.free_edges:
        free_edge = crumbling_edge(*flatten(edge, wall.normal))
        free_edges.append(free_edge)
    for edge in wall.base_edges:
        base_edge = Segment(*flatten(edge, wall.normal))
        base_edges.append(base_edge)
    for edge in wall.wall_connecter_edges:
        connecting_edge = Segment(*flatten(edge,wall.normal))
        connecting_edge.zigify(2.5)
        connecting_edges.append(connecting_edge)

    # floor connection and windows.

    return free_edges + connecting_edges + base_edges
