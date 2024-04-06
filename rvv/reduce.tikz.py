import sys
import random

from tikz import *

def draw(file):
    y0 = 0.0
    x = 0.0
    y = 0.0
    d = 0.5

    elements = 16
    vs2      = [None] * elements
    vs2[0]   = 11
    bitmask  = [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0]
    vs1      = [5, 7, 2, 3, 9, 1, 4, 3, 1, 5, 4, 9, 3, 2, 7, 7]
    vd       = [None] * elements

    arguments = [vs2[0]]
    vd[0] = vs2[0]
    for (i, m) in enumerate(bitmask):
        if m:
            arguments.append(vs1[i])

    vd[0] = sum(arguments)

    assert len(bitmask) == elements
    assert len(vs1) == elements
    assert len(vs2) == elements
    assert len(vd) == elements

    style_active   = 'fill=green'
    style_inactive = 'fill=white'

    y = y0

    vs1_view = []
    for (i, v) in enumerate(vs1):
        l = LabelledRectangle(x - i * d, y, d, d)
        l.label = texttt('%d' % v)
        if bitmask[i] == 1:
            l.style = style_active
        else:
            l.style = style_inactive

        l.draw(file)
        vs1_view.append(l)

    file.label(vs1_view[-1].left, "vs1", "anchor=east")

    y = y0 + 4 * d

    vs2_view = []
    for (i, v) in enumerate(vs2):
        l = LabelledRectangle(x - i * d, y, d, d)
        if v is not None:
           l.label = texttt('%d' % v)

        draw_index(file, l.bottom, str(i))
        l.draw(file)
        vs2_view.append(l)

    file.label(vs2_view[-1].left, "vs2", "anchor=east")

    y = y0 + 1.5 * d

    bitmask_view = []
    for (i, v) in enumerate(bitmask):
        l = LabelledRectangle(x - i * d, y, d, d)
        l.label = small(str(v))
        if v == 1:
            l.style = style_active
        else:
            l.style = style_inactive

        l.draw(file)
        bitmask_view.append(l)

    file.label(bitmask_view[-1].left, "mask", "anchor=east")

    y = y0 - 6.0 * d

    vd_view = []
    for (i, v) in enumerate(vd):
        l = LabelledRectangle(x - i * d, y, d, d)
        if v is not None:
           l.label = texttt('%d' % v)

        l.draw(file)
        vd_view.append(l)

    file.label(vd_view[-1].left, "vd", "anchor=east")

    target_y = vs1_view[0].bottom.y - 2*d

    line_style  = 'thick,blue'
    arrow_style = '%s,->' % line_style

    # draw initial value
    p0 = vs2_view[0].right
    p1 = p0.dx(+d)
    p2 = Point(p1.x, target_y)
    file.polyline([p0, p1, p2], line_style)
        

    # draw ops
    prev_x   = p2.x
    radious  = d * 0.4
    for (i, v) in enumerate(bitmask):
        if v != 1:
            continue

        p1 = vs1_view[i].bottom
        pc = Point(p1.x, target_y)

        c = LabelledCircle(pc, radious)
        c.label = "+"
        c.draw(file)

        file.line(p1, c.top, arrow_style)

        file.line(Point(prev_x, target_y), c.right, arrow_style)

        prev_x = c.left.x

    # draw final
    p0 = c.bottom
    p1 = p0.dy(-1.5 * d)
    p2 = Point(vd_view[0].right.x + d, p1.y)
    p3 = Point(p2.x, vd_view[0].right.y)
    p4 = vd_view[0].right
    file.polyline([p0, p1, p2, p3, p4], arrow_style)

    # draw label
    xc = (p1.x + p2.x) * 0.5
    yc = p1.y
    args   = " + ".join(map(str, arguments))
    label  = "$(%s) \pmod{256}$" % (args)

    file.label(Point(xc, yc), label, "anchor=south")


if __name__ == '__main__':
    file = File()
    draw(file)

    with open(sys.argv[1], 'wt') as f:
        file.save(f)

