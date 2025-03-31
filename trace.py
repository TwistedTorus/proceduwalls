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

    #def select_next_seg(end, remaining_segments):
    #    next_seg = None
    #    flip = False
    #    for seg in remaining_segments:
    #        print(seg.start, end)
    #        if seg.start == end:
    #            next_seg = seg
    #        if seg.end == end:
    #            next_seg = seg
    #            flip = True
    #    new_remaining_segs = []
    #    for seg in remaining_segments:
    #        if seg != next_seg:
    #            new_remaining_segs.append(seg)
    #    return next_seg, new_remaining_segs, flip

    #remaining_segments = segments[1:]
    #seg = remaining_segments[0]
    #end = seg.end
    #trace += seg.points

    #while remaining_segments != []:
    #    print("before seg", seg, end)
    #    next_seg, remaining_segments, flip= select_next_seg(end, remaining_segments)
    #    print("next seg", next_seg, end)
    #    if remaining_segments == []:
    #        continue
    #    if flip:
    #        trace += next_seg.points[::-1]
    #        end = next_seg.start
    #    else:
    #        trace += next_seg.points
    #        end = next_seg.end
    #    seg = next_seg

    trace = []
    for seg in segments:
        trace += seg.points

    return trace

def wall_to_trace(wall):

    segments = []

    free_edges = []
    connecting_edges = []
    base_edges = []
    point_remapping = {}
    for edge in wall.free_edges:
        #free_edge = Segment(*flatten(edge, wall.normal))
        free_edge = crumbling_edge(*flatten(edge, wall.normal))
        free_edges.append(free_edge)
    for edge in wall.base_edges:
        base_edge = Segment(*flatten(edge, wall.normal))
        base_edges.append(base_edge)
    for edge in wall.wall_connecter_edges:
        connecting_edge = Segment(*flatten(edge,wall.normal))
        fr , to = connecting_edge.start, connecting_edge.end
        d = 3
        #connecting_edge.translate(-d/2,0)
        connecting_edge.zigify(d)
        connecting_edges.append(connecting_edge)

        point_remapping[fr] = connecting_edge.start
        point_remapping[to] = connecting_edge.end

    for seg in free_edges + base_edges:
        seg.remap_points(point_remapping)

    box_cut_traces = []
    floor_cut_guides = []
    for fc_edge in wall.floor_connecter_edges:
        rect_cuts_start_end = flatten(fc_edge,wall.normal)
        floor_cut_guides.append(Segment(*rect_cuts_start_end))
        box_cut_traces += edge_to_box_traces(rect_cuts_start_end,5,d)

    wall_outline = segments_to_trace(free_edges + connecting_edges + base_edges)

    return [wall_outline] + box_cut_traces

def floor_to_trace(floor):
    pass
