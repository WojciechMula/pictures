import sys

from tikz import *
from io import StringIO

def draw(file):
    x = 0.0
    y = 0.0
    d = 0.5

    v1style = 'fill=blue!75'
    v1style_desel = 'fill=blue!15'
    v2style = 'fill=green!75'
    v2style_desel = 'fill=green!15'
    v3style = 'fill=white'

    v1 = [2, 7, 8, 9, 1, 12, 5, 12]
    v2 = [8, 1, 13, 9, 5, 41, 0, 2]
    v3 = [True, False, True, True, False, False, True, False]

    assert len(v1) == 8
    assert len(v2) == 8
    assert len(v3) == 8

    vec1 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for byte, value, sel in zip(vec1.byte, v1, v3):
        byte.label = texttt('%d' % value)
        if sel == True:
            byte.style = v1style
        else:
            byte.style = v1style_desel


    y -= 2*d

    vec2 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for byte, value, sel in zip(vec2.byte, v2, v3):
        byte.label = texttt('%d' % value)
        if sel == False:
            byte.style = v2style
        else:
            byte.style = v2style_desel

    y -= 2*d

    vec3 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for byte, value in zip(vec3.byte, v3):
        if value:
            byte.label = texttt('ff')
        else:
            byte.label = texttt('00')

        byte.style = v3style

    y -= 2*d

    vec4 = QWORD(x, y, 8*d, d, WHOLE_BYTE)
    for byte, val1, val2, cond in zip(vec4.byte, v1, v2, v3):
        if cond:
            byte.label = texttt('%d' % val1)
            byte.style = v1style
        else:
            byte.label = texttt('%d' % val2)
            byte.style = v2style


    for i in range(8):
        dx = 0.2 * d

        color = None

        if v3[i]:
            f = vec1.byte[i].bottom
            t = vec3.byte[i].top

            f.x += dx
            t.x += dx
            color = "blue!75"
            file.line(f, t, f'color={color},->')
        else:
            f = vec2.byte[i].bottom
            t = vec3.byte[i].top

            f.x -= dx
            t.x -= dx
            color = "green!75"
            file.line(f, t, f'color={color},->')

        file.line(vec3.byte[i].bottom,
                  vec4.byte[i].top,
                  f'color={color},->')


    file.label(vec1.left, "$a=$", "anchor=east")
    file.label(vec2.left, "$b=$", "anchor=east")
    file.label(vec3.left, "$s=$", "anchor=east")
    file.label(vec4.left, "$c=$", "anchor=east")
    file.draw(vec1)
    file.draw(vec2)
    file.draw(vec3)
    file.draw(vec4)


if __name__ == '__main__':
    file = File()
    draw(file)

    with open(sys.argv[1], 'wt') as f:
        file.save(f)

