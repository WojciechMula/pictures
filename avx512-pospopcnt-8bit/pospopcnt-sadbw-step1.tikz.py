import sys
import itertools

from io import StringIO
from tikz import *
from pospopcnt import *


def popcnt(bytes, mask):
    res = 0
    for b in bytes:
        if b & mask:
            res += 1
    
    return res


def draw_picture(f):
    x = 0.0
    y = 0.0
    w_bit = 0.25
    h = 0.45
    input = QWORD(x, y, 64*w_bit, h)

    bytes = [0x1f, 0xc0, 0x55, 0xff, 0xf0, 0x42, 0x72, 0x34]
    assert len(bytes) == 8

    for i, v in enumerate(bytes):
        byte = input.byte[i]
        byte.value = v
        for j, bit in enumerate(byte.bit):
            if j in (0, 4):
                bit.style = color(j)
            else:
                bit.style = inactive

    f.draw(input)
    f.label(input.lt, r'\texttt{input}', 'anchor=south west')
    for i, byte in enumerate(input.byte):
        draw_horiz_brace(f, byte.right.x, byte.left.x, byte.bottom.y,
                         f'$b_{i}$ = 0x{byte.value:02x}', 'below')

    y -= 4.0*h

    mask = QWORD(x, y, 64*w_bit, h)
    for i in range(8):
        mask.byte[i].value = 0x11
        for j, bit in enumerate(mask.byte[i].bit):
            if j not in (0, 4):
                bit.style = inactive

    f.draw(mask)
    f.label(mask.lt, r'\texttt{mask}', 'anchor=south west')

    y -= 2.5*h

    masked = QWORD(x, y, 64*w_bit, h)
    for i, v in enumerate(bytes):
        masked.byte[i].value = v & 0xff
        for j, bit in enumerate(masked.byte[i].bit):
            if j == 0:
                bit.style = color(0)
            elif j == 4:
                bit.style = color(4)
            else:
                bit.label = None

    masked.draw(f)
    f.label(masked.lt, r'\texttt{t04 = mask \& input}', 'anchor=south west')

    y -= 2.5*h

    sadbw = QWORD(x, y, 64*w_bit, h)
    for i in range(1, 8):
        byte = sadbw.byte[i]
        sadbw.byte[i] = WHOLE_BYTE(byte.x, byte.y, byte.w, byte.h)
        sadbw.byte[i].label = '0'

    bit0sum = popcnt(bytes, 0x01)
    bit4sum = popcnt(bytes, 0x10)

    byte0 = sadbw.byte[0]

    byte0.value = bit0sum | (bit4sum << 4)
    for j, bit in enumerate(byte0.bit):
        if j < 4:
            bit.style = color(0)
        else:
            bit.style = color(4)

    sadbw.draw(f)
    draw_horiz_brace(f, byte0.bit[0].right.x, byte0.bit[3].left.x, byte0.bottom.y,
                     '0x%02x' % bit0sum, 'below')

    draw_horiz_brace(f, byte0.bit[4].right.x, byte0.bit[7].left.x, byte0.bottom.y,
                     '0x%02x' % bit4sum, 'below')
    f.label(sadbw.lt, r'\texttt{sum04 = VPSADBW(t04, zero)}', 'anchor=south west')


if __name__ == '__main__':
    buf = StringIO()
    buf.write(r"\begin{tikzpicture}")
    draw_picture(File(buf))
    buf.write(r"\end{tikzpicture}")

    with open(sys.argv[1], 'wt') as f:
        f.write(buf.getvalue())
