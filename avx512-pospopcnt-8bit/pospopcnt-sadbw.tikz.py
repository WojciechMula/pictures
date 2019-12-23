import sys
import itertools

from io import StringIO
from tikz import *
from pospopcnt import *

class AVX512Reg(Rectangle):
    def __init__(self, x, y, width, height, byte_cls=BYTE):
        super().__init__(x, y, width, height)
        self.style = ''

        self.byte = []
        w = width/64
        for i in range(64):
            self.byte.append(byte_cls(x + (63-i) * w, y, w, height))

    def draw(self, file):
        for byte in self.byte:
            byte.draw(file)


class SharedByte(Rectangle):
    def __init__(self, x, y, width, height, byte_cls=BYTE):
        super().__init__(x, y, width, height)
        self.style  = ''
        self.style1 = ''
        self.style2 = ''

    def draw(self, file):
        if self.style1:
            file.writeln(r'\fill [%s] (%0.2f, %0.2f) -- (%0.2f, %0.2f) -- (%0.2f, %0.2f) -- cycle;' %
                        (self.style1, self.x, self.y, self.x + self.w, self.y, self.x, self.y + self.h))

        if self.style2:
            file.writeln(r'\fill [%s] (%0.2f, %0.2f) -- (%0.2f, %0.2f) -- (%0.2f, %0.2f) -- cycle;' %
                        (self.style2,
                         self.x + self.w, self.y,
                         self.x + self.w, self.y + self.h,
                         self.x, self.y + self.h))

        file.writeln(r'\draw [%s] (%0.2f, %0.2f) rectangle (%0.2f, %0.2f);' %
                    (self.style, self.x, self.y, self.x + self.w, self.y + self.h))
        

def draw_byte_layout(f):
    x = 0.0
    y = 0.0
    w_byte = 14
    h = 1.5 * w_byte/64
    H = 2.5 * w_byte/64
    sum04 = AVX512Reg(x, y - 0 * H, w_byte, h, SharedByte)
    sum15 = AVX512Reg(x, y - 1 * H, w_byte, h, SharedByte)
    sum26 = AVX512Reg(x, y - 2 * H, w_byte, h, SharedByte)
    sum37 = AVX512Reg(x, y - 3 * H, w_byte, h, SharedByte)

    regs = [sum04, sum15, sum26, sum37]

    for i in range(64):
        if i % 8 == 0:
            sum04.byte[i].style1 = color(0)
            sum04.byte[i].style2 = color(4)

            sum15.byte[i].style1 = color(1)
            sum15.byte[i].style2 = color(5)

            sum26.byte[i].style1 = color(2)
            sum26.byte[i].style2 = color(6)

            sum37.byte[i].style1 = color(3)
            sum37.byte[i].style2 = color(7)
        else:
            for reg in regs:
                reg.byte[i].style = inactive


    sum04.draw(f)
    draw_label(f, sum04.left, r'\texttt{sum04}', 'left')
    sum15.draw(f)
    draw_label(f, sum15.left, r'\texttt{sum15}', 'left')
    sum26.draw(f)
    draw_label(f, sum26.left, r'\texttt{sum26}', 'left')
    sum37.draw(f)
    draw_label(f, sum37.left, r'\texttt{sum37}', 'left')


def draw_reshuffled(f):
    x = 0.0
    y = 0.0
    w_byte = 14
    h = 1.5 * w_byte/64
    H = 2.5 * w_byte/64

    def reshuffled(y, bits, label):
        reg = AVX512Reg(x, y, w_byte, h, WHOLE_BYTE)
        for i in range(0, 64):
            q = i // 8
            if q in bits:
                reg.byte[i].style = color(q)
            else:
                reg.byte[i].style = inactive

        reg.draw(f)
        draw_label(f, reg.left, label, 'left')

    reshuffled(y - 0*H, (0, 4, 1, 5), r'\texttt{g0}')
    reshuffled(y - 1*H, (2, 6, 3, 7), r'\texttt{g1}')
    reshuffled(y - 2*H, (0, 1, 2, 4, 5, 6, 7), r'\texttt{t0}')


if __name__ == '__main__':
    buf = StringIO()
    buf.write(r"\begin{tikzpicture}")
    name = "draw_%s" % sys.argv[1].replace('-', '_')
    draw_func = globals()[name]
    draw_func(File(buf))
    buf.write(r"\end{tikzpicture}")

    with open(sys.argv[2], 'wt') as f:
        f.write(buf.getvalue())
