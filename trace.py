from segments import Segment, crumbling_edge

def sketch_trace(trace, ax, style = "k"):
    x_points = []
    y_points = []
    for point in trace:
        x_points.append(point[0])
        y_points.append(point[1])
    ax.plot(x_points, y_points, style)

def translate(trace, x, y):

    new_trace = []
    for p in trace:
        np = (p[0]+x,p[1]+y)
        new_trace.append(np)
    return new_trace

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
    #if flip:
    #    r[0] = -r[0]
    return (r[0],r[1])

def flatten(edge, normal):
    return tuple([flatten_node(n,normal) for n in edge])

def box_trace(s,e,h):
    y_top    = s[1] + h/2
    y_bottom = s[1] - h/2
    x_left   = s[0]
    x_right  = e[0]
    tl = (x_left,y_top)
    tr = (x_right,y_top)
    br = (x_right,y_bottom)
    bl = (x_left, y_bottom)
    trace = [tl,tr,br,bl,tl]
    return trace

def edge_to_box_traces(edge, n_boxes, h):
    start, end = edge
    y = start[1]
    box_traces = []
    dx = (end[0] - start[0])/n_boxes
    for i in range(0,n_boxes,2):
        s = (start[0]+i*dx, y)
        e = (start[0]+(i+1)*dx, y)
        box_traces.append(box_trace(s,e,h))
    return box_traces

def segments_to_trace(segments):

    trace = []
    for seg in segments:
        trace += seg.points

    return trace

def wall_to_trace(wall):

    segments = []

    free_edges = []
    right_connecter_edges = []
    left_connecter_edges  = []
    base_edges = []
    point_remapping = {}
    d = 3
    for edge in wall.free_edges:
        #free_edge = Segment(*flatten(edge, wall.normal))
        free_edge = crumbling_edge(*flatten(edge, wall.normal))
        free_edges.append(free_edge)
    for edge in wall.base_edges:
        base_edge = Segment(*flatten(edge, wall.normal))
        base_edges.append(base_edge)

    for edge in wall.left_connecter:
        left_connecter = Segment(*flatten(edge,wall.normal))
        fr , to = left_connecter.start, left_connecter.end
        left_connecter.zigify(d)
        left_connecter_edges.append(left_connecter)
        point_remapping[fr] = left_connecter.start
        point_remapping[to] = left_connecter.end

    for edge in wall.right_connecter:
        right_connecter = Segment(*flatten(edge,wall.normal))
        fr , to = right_connecter.start, right_connecter.end
        right_connecter.zigify(d)
        right_connecter_edges.append(right_connecter)
        point_remapping[fr] = right_connecter.start
        point_remapping[to] = right_connecter.end

    for seg in free_edges + base_edges:
        seg.remap_points(point_remapping)

    box_cut_traces = []
    floor_cut_guides = []
    for fc_edge in wall.floor_connecter_edges:
        rect_cuts_start_end = flatten(fc_edge,wall.normal)
        floor_cut_guides.append(Segment(*rect_cuts_start_end))
        box_cut_traces += edge_to_box_traces(rect_cuts_start_end,5,d)

    wall_outline = segments_to_trace(free_edges + right_connecter_edges + base_edges + left_connecter_edges)

    return [wall_outline] + box_cut_traces

def floor_to_trace(floor):

    def shift_nodes(trace, node_shifts):
        new_trace = []
        for point in trace:
            x,y = point
            if point in node_shifts:
                for shift in node_shifts[point]:
                    x += shift[0]
                    y += shift[1]
            new_point = (x,y)
            new_trace.append(new_point)
        return new_trace

    def remove_dupes(trace):
        new_trace = [trace[0]]
        for point in trace:
            if point != new_trace[-1]:
                new_trace.append(point)
        return new_trace

    trace = []
    d = 3
    for node in floor.nodes:
        trace.append((node.x,node.y))
    node_shifts = {}
    for edge in floor.edges:
        n1, n2 = edge
        if edge in floor.edge_wall_normals:
            norm = floor.edge_wall_normals[edge]
            normal = (-norm[0]*d, -norm[1]*d)
            for n in [n1,n2]:
                p = (n.x,n.y)
                if p in node_shifts:
                    node_shifts[p].add(normal)
                else:
                    node_shifts[p] = {normal}
            if edge in floor.connecter_edges:
                print("must add connection along edge:", edge, normal)

        trace.append((n1.x,n1.y))
        trace.append((n2.x,n2.y))

    new_trace = shift_nodes(trace,node_shifts)

    #use edges to shift + their normal wall direction,
    # generate a little block patter along that bit.

    return [trace, new_trace]


