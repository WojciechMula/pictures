import sys
import random

from tikz import *

def draw(file):
    x = 0.0
    y = 0.0
    d = 0.5

    random.seed(42)

    elements = 32
    vstart   = 7
    vl       = 19
    vector   = [random.randint(0, 255) for _ in range(elements)]
    bitmask  = [random.randint(0, 1)   for _ in range(elements)]

    style_prestart = 'fill=gray!50'
    style_tail     = style_prestart
    style_active   = 'fill=green'
    style_inactive = 'fill=red!20'

    vector_view = []
    for (i, v) in enumerate(vector):
        l = LabelledRectangle(x - i * d, y, d, d)
        l.label = texttt('%02x' % v)
        if i < vstart:
            l.style = style_prestart
        elif i >= vl:
            l.style = style_tail
        else:
            if bitmask[i] == 1:
                l.style = style_active
            else:
                l.style = style_inactive

        if i == elements - 2:
            l.label = ".."
        else:
            if i == elements - 1:
               draw_index(file, l.bottom, "{VLMAX}")
            else:
               draw_index(file, l.bottom, str(i))

        l.draw(file)
        vector_view.append(l)

    y -= 4 * d

    bitmask_view = []
    for (i, v) in enumerate(bitmask):
        l = LabelledRectangle(x - i * d, y, d, d)
        if vstart <= i < vl:
            l.label = texttt('%d' % v)
            if v == 1:
                l.style = style_active
        else:
            l.label = ''
            l.style = style_tail

        l.draw(file)
        bitmask_view.append(l)


    if True:
        p1 = vector_view[vstart].top
        p2 = Point(p1.x, p1.y + 1.5*d)
        file.line(p2, p1, f'color=blue,->')

        file.label(p2, texttt(f"vstart = {vstart}"), "anchor=south")

        draw_horiz_brace(
            file,
            vector_view[vstart - 1].top_left.x,
            vector_view[0].top_right.x,
            vector_view[0].top_left.y,
            "prestart",
            "above"
        )


    if True:
        draw_horiz_brace(
            file,
            vector_view[vl - 1].top_left.x,
            vector_view[vstart].top_right.x,
            vector_view[vstart].top_left.y,
            "body",
            "above"
        )

    if True:
        p1 = vector_view[vl].top
        p2 = Point(p1.x, p1.y + 1.5*d)
        file.line(p2, p1, f'color=blue,->')

        file.label(p2, texttt(f"vl = {vl}"), "anchor=south")

        draw_horiz_brace(
            file,
            vector_view[elements - 1].top_left.x,
            vector_view[vl].top_right.x,
            vector_view[vl].top_left.y,
            "tail",
            "above"
        )

    x_coords = []    
    for i in range(elements):
        if vstart <= i < vl and bitmask[i] == 1:
            p = vector_view[i].bottom
            p = Point(p.x, p.y - 0.6 * d)
            file.line(bitmask_view[i].top, p, f'color=black,->')
            x_coords.append(p.x)

    x_coords.sort()

    def picture_label(xc, yc, width, height, label, style=''):
        p0 = Point(xc - width/2, yc - height/2)
        p1 = Point(xc + width/2, yc + height/2)
        file.rectangle(p0, p1, style)
        file.label(Point(xc, yc), label)

    xc = (x_coords[0] + x_coords[-1]) * 0.5
    yc = ((vector_view[0].bottom.y - 0.6 * d) + bitmask_view[0].top.y) * 0.5
    width  = x_coords[-1] - x_coords[0] + d
    height = d

    picture_label(xc, yc, width, height,
                  "active elements",
                  "fill=yellow!25,rounded corners=5pt")
    
    file.label(vector_view[-1].left, "vector", "anchor=east")
    file.label(bitmask_view[-1].left, "mask", "anchor=east")


if __name__ == '__main__':
    file = File()
    draw(file)

    with open(sys.argv[1], 'wt') as f:
        file.save(f)

