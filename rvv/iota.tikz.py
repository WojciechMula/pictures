import sys
import random

from itertools import chain
from tikz import *

def draw(file):
    y0 = 0.0
    x = 0.0
    y = 0.0
    w = 2.0
    h = 0.5

    random.seed(2047)

    elements = 8
    bitmask       = 0b10100111

    tmp1 = [bitmask] * elements
    tmp2 = [0xff >> (elements - i) for i in range(elements)]
    vd   = list(map(popcount, (a & b for a, b in zip(tmp1, tmp2))))

    style_active    = 'fill=green'
    style_inactive  = 'fill=white'
    style_untouched = 'fill=gray!75'

    y = y0

    tmp1_view = []
    for (i, v) in enumerate(tmp1):
        l = LabelledRectangle(x - i * w, y, w, h)

        tmp = image(v)
        pos = 8 - i
        l.label = r"\textcolor{gray}{%s}%s" % (texttt(tmp[:pos]), texttt(tmp[pos:]))
        l.style = style_inactive
        tmp1_view.append(l)

    file.label(tmp1_view[-1].left, r"$\textrm{tmp}_1$", "anchor=east")

    y = y0 - 1.5 * h

    tmp2_view = []
    for (i, v) in enumerate(tmp2):
        l = LabelledRectangle(x - i * w, y, w, h)
        l.label = texttt(image(v))
        l.style = style_inactive
        tmp2_view.append(l)

    file.label(tmp2_view[-1].left, r"$\textrm{tmp}_2$", "anchor=east")

    y = y0 - 5.0 * h

    vd_view = []
    for (i, v) in enumerate(vd):
        l = LabelledRectangle(x - i * w, y, w, h)
        l.label = texttt(str(v))
        vd_view.append(l)

    file.label(vd_view[-1].left, "vd", "anchor=east")

    center = (tmp2_view[0].bottom + vd_view[-1].top) / 2
    width  = vd_view[0].right.x - vd_view[-1].left.x
    height = h

    picture_label(center.x, center.y, width, height,
                  r"$\textrm{popcount}(\textrm{tmp}_1 \  \& \  \textrm{tmp}_2)$",
                  "fill=yellow!25,rounded corners=5pt")

    hspace = h/2
    line_style = "thick,blue,->"
    for i in range(elements):
        p1 = Point(tmp2_view[i].bottom.x - hspace, tmp2_view[i].bottom.y)
        p2 = Point(p1.x, center.y + height/2)
        file.line(p1, p2, line_style)

        p1 = Point(tmp1_view[i].bottom.x + hspace, tmp1_view[i].bottom.y)
        p2 = Point(p1.x, center.y + height/2)
        file.line(p1, p2, line_style)

        p2 = vd_view[i].top
        p1 = Point(p2.x, center.y - height/2)
        file.line(p1, p2, line_style)

    for w in chain(tmp1_view, tmp2_view, vd_view):
        w.draw(file)

    file.label(tmp1_view[-1].top_left.dy(h/2), r"mask = \texttt{0b%s}" % image(bitmask), "anchor=south west")


def picture_label(xc, yc, width, height, label, style=''):
    p0 = Point(xc - width/2, yc - height/2)
    p1 = Point(xc + width/2, yc + height/2)
    file.rectangle(p0, p1, style)
    file.label(Point(xc, yc), label)


def image(b):
    return '{:08b}'.format(b)


def popcount(x):
    n = 0
    while x:
        if x & 1:
            n += 1

        x >>= 1

    return n


if __name__ == '__main__':
    file = File()
    draw(file)

    with open(sys.argv[1], 'wt') as f:
        file.save(f)

