from segments import Segment, crumbling_edge
import matplotlib.pyplot as plt
import svg

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


class building:
    def __init__(self):
        self.walls  = []
        self.floors = []


seg_1 = crumbling_edge((95,100),(0,0))
seg_2 = Segment((0,0),(200,0))
seg_3 = crumbling_edge((200,0),(105,100))
seg_4 = Segment((105,100),(95,100))

cut = Segment((100,100),(100,0))
cut.zigify(2.5)

corner_seg = Segment((95,100),(0,0))
corner_seg.child_segments = [seg_1, seg_2, seg_3, seg_4]
corner_seg.fuse_children()

print(to_svg([corner_seg.points, cut.points]))


#fig, ax = plt.subplots()
#
#corner_seg.sketch(ax)
#plt.show()
