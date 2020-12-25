import sys

from tikz import *
from io import StringIO

def draw(file, type):
    x = 0.0
    y = 0.0
    d = 0.5

    v1 = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    if type == 'shuffle':
        # produce hexword "badcaffe"
        v2 = [1, 0, 3, 2, 0, 5, 5, 4]
        v2.reverse()
    elif type == 'broadcast':
        v2 = [3] * 8
    elif type == 'reverse':
        v2 = list(range(8))
        v2.reverse()
    else:
        assert False, "wrong type value"

    v3 = [None] * 8
    for trg, src in enumerate(v2):
        v3[trg] = v1[src]

    assert len(v1) == 8
    assert len(v2) == 8
    assert len(v3) == 8

    vec1 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for index, (byte, value) in enumerate(zip(vec1.byte, v1)):
        byte.label = texttt(value)
        byte.style = 'fill=white'
        byte.index = index
        byte.draw_index(file)

    y -= 4*d

    vec2 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for byte, value in zip(vec2.byte, v2):
        byte.style = 'fill=white'
        byte.label = texttt('%d' % value)

    y -= 2*d

    vec3 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for byte, value in zip(vec3.byte, v3):
        byte.label = value

    for i in range(8):
        f = vec1.byte[v2[i]].bottom
        t = vec2.byte[i].top
        file.line(f, t, 'dotted')

        file.line(vec2.byte[i].bottom,
                  vec3.byte[i].top,
                  'dotted')

    file.label(vec1.left, "$a=$", "anchor=east")
    file.label(vec2.left, "$b=$", "anchor=east")
    file.label(vec3.left, "$c=$", "anchor=east")
    file.draw(vec1)
    file.draw(vec2)
    file.draw(vec3)


if __name__ == '__main__':
    file = File()
    draw(file, sys.argv[2])

    with open(sys.argv[1], 'wt') as f:
        file.save(f)
