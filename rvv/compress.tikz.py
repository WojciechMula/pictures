import sys
import random

from tikz import *

def draw(file):
    y0 = 0.0
    x = 0.0
    y = 0.0
    d = 0.5

    random.seed(42)

    elements = 16
    bitmask  = [int(random.randint(0, 100) > 70) for _ in range(elements)]
    vs1      = [random.randint(0, 255) for _ in range(elements)]
    vd       = [None] * elements

    target = 0
    for i, m in enumerate(bitmask):
        if m:
            vd[target] = vs1[i]
            target += 1

    assert len(bitmask) == elements
    assert len(vs1) == elements
    assert len(vd) == elements

    style_active    = 'fill=green'
    style_inactive  = 'fill=white'
    style_untouched = 'fill=gray!75'

    y = y0

    vs1_view = []
    for (i, v) in enumerate(vs1):
        l = LabelledRectangle(x - i * d, y, d, d)
        l.label = texttt('%02x' % v)
        if bitmask[i] == 1:
            l.style = style_active
        else:
            l.style = style_inactive

        l.draw(file)
        vs1_view.append(l)

    file.label(vs1_view[-1].left, "vs1", "anchor=east")

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

    y = y0 - 4.0 * d

    vd_view = []
    for (i, v) in enumerate(vd):
        l = LabelledRectangle(x - i * d, y, d, d)
        if v is not None:
           l.label = texttt('%02x' % v)
           l.style = style_active
        else:
           l.style = style_untouched

        l.draw(file)
        vd_view.append(l)

    file.label(vd_view[-1].left, "vd", "anchor=east")

    target_y = vs1_view[0].bottom.y - 2*d

    line_style  = 'thick,blue'
    arrow_style = '%s,->' % line_style

    target = 0
    for i, m in enumerate(bitmask):
        if m:
            file.line(
                vs1_view[i].bottom,
                vd_view[target].top,
                'thick,blue,->'
            )
            target += 1


if __name__ == '__main__':
    file = File()
    draw(file)

    with open(sys.argv[1], 'wt') as f:
        file.save(f)

