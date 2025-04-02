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

    def shift_nodes(trace, node_shifts, connecter_points, free_points):
        new_trace = []
        new_connecter_points = set()
        new_free_points = set()
        new_connecter_normals = {}
        for point in trace:
            x,y = point
            if point in node_shifts:
                for shift in node_shifts[point]:
                    x += shift[0]
                    y += shift[1]
                new_connecter_normals[(x,y)] = node_shifts[point]
            new_point = (x,y)
            new_trace.append(new_point)
            if point in connecter_points:
                new_connecter_points.add(new_point)
            if point in free_points:
                new_free_points.add(new_point)
        return new_trace, new_connecter_points, new_free_points, new_connecter_normals

    def remove_dupes(trace):
        new_trace = [trace[0]]
        for point in trace:
            if point != new_trace[-1]:
                new_trace.append(point)
        return new_trace

    def points_to_edges(points):
        edges = []
        for i in range(len(points)-1):
            p1 = points[i]
            p2 = points[i+1]
            edges.append((p1,p2))
        return edges

    def edges_to_points(edges):
        trace = []
        for edge in edges:
            if type(edge) == Segment:
                trace += edge.points
            else:
                p1, p2 = edge
                trace += [p1, p2]
        return remove_dupes(trace)

    def to_connecter_edges(edge, shift_set):
        edges = []
        n = 5
        p1, p2 = edge
        dr = (p2[0]-p1[0],p2[1]-p1[1])
        for shift in shift_set:
            normal = (-shift[0],-shift[1])
            for i in range(n):
                dx1 = i/n *dr[0]
                dx2 = (i+1)/n * dr[0]
                dy1 = i/n * dr[1]
                dy2 = (i+1)/n * dr[1]
                if i%2 == 0:
                    np1 = (p1[0]+normal[0]+dx1, p1[1]+normal[1]+dy1)
                    np2 = (p1[0]+normal[0]+dx2, p1[1]+normal[1]+dy2)
                else:
                    np1 = (p1[0]+dx1, p1[1]+dy1)
                    np2 = (p1[0]+dx2, p1[1]+dy2)
                edges.append((np1,np2))
            return edges


    trace = []
    d = 3
    node_shifts = {}
    connecter_points = []
    connecter_normal = {}
    free_points = []
    for edge in floor.edges:
        n1, n2 = edge
        p1, p2 = (n1.x, n1.y),(n2.x,n2.y)
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
                    connecter_points.append(p)
        if edge in floor.free_edges:
            for n in [n1,n2]:
                p = (n.x,n.y)
                if not p in free_points:
                    free_points.append(p)

        trace.append(p1)
        trace.append(p2)
    new_trace = remove_dupes(trace)
    new_trace, new_connecter_points, new_free_points, new_connecter_normals = shift_nodes(new_trace,node_shifts,connecter_points,free_points)
    new_edges = points_to_edges(new_trace)
    nn_edges = []
    for edge in new_edges:
        p1,p2 = edge
        if p1 in new_connecter_points and p2 in new_connecter_points:
            connecter_edges = to_connecter_edges(edge, new_connecter_normals[p1])
            nn_edges +=  connecter_edges
        elif p1 in new_free_points and p2 in new_free_points:
            #nn_edges.append(edge)
            nn_edges.append(crumbling_edge(p1, p2))
        else:
            nn_edges.append(edge)

    new_trace = edges_to_points(nn_edges)
    #use edges to shift + their normal wall direction,
    # generate a little block patter along that bit.

    return [new_trace]


