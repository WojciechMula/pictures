import sys

from tikz import *
from io import StringIO

def draw(file):
    x = 0.0
    y = 0.0
    d = 0.5

    v1color = 'blue'
    v2color = 'red'
    transparency = 25

    v1 = [2, 7, 8, 9, 1, 12, 5, 12]
    v2 = [8, 1, 13, 9, 5, 41, 0, 2]
    v3 = [a + b for a,b in zip(v1, v2)]

    assert len(v1) == 8
    assert len(v2) == 8
    assert len(v3) == 8

    vec1 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for byte, value in zip(vec1.byte, v1):
        byte.label = texttt('%d' % value)
        byte.style = f'fill={v1color}!{transparency}'

    y -= 2*d

    vec2 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for byte, value in zip(vec2.byte, v2):
        byte.style = f'fill={v2color}!{transparency}'
        byte.label = texttt('%d' % value)

    y -= 4*d

    vec3 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for byte, value in zip(vec3.byte, v3):
        byte.label = texttt('%d' % value)

    m = (vec2.bottom_left + vec3.top_right) / 2

    for i in range(8):
        f1 = vec1.byte[i].bottom
        t1 = vec3.byte[i].top

        s = 0.2
        
        f1.x -= s * d
        t1.x -= s * d
        t1.y  = m.y + d/2

        f2 = vec2.byte[i].bottom
        t2 = vec3.byte[i].top
        
        f2.x += s * d
        t2.x += s * d
        t2.y  = m.y + d/2

        file.line(f1, t1, f'->,color={v1color}')
        file.line(f2, t2, f'->,color={v2color}')

        t3 = vec3.byte[i].top
        f3 = Point(t3.x, m.y)

        file.line(f3, t3, 'very thin,->')


    def picture_label(xc, yc, width, height, label, style=''):
        p0 = Point(xc - width/2, yc - height/2)
        p1 = Point(xc + width/2, yc + height/2)
        file.rectangle(p0, p1, style)
        file.label(Point(xc, yc), label)

    picture_label(m.x, m.y, vec2.w, d,
                  "$c_i = a_i + b_i$",
                  "fill=yellow!25,rounded corners=5pt")

    file.label(vec1.left, "$a=$", "anchor=east")
    file.label(vec2.left, "$b=$", "anchor=east")
    file.label(vec3.left, "$c=$", "anchor=east")
    file.draw(vec1)
    file.draw(vec2)
    file.draw(vec3)


if __name__ == '__main__':
    file = File()
    draw(file)

    with open(sys.argv[1], 'wt') as f:
        file.save(f)
