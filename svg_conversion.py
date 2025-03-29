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
