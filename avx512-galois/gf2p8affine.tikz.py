import sys
import argparse

from io import StringIO
from tikz import *
from gf2p8affine import *


class AVX512Lane(Rectangle):
    def __init__(self, x, y, width, height, values, byte_cls=BYTE):
        super().__init__(x, y, width, height)
        self.style = ''

        self.byte = []
        w = width/8
        for i in range(8):
            byte = byte_cls(x + (7-i) * w, y, w, height)
            byte.value = values[i]
            byte.index = i
            self.byte.append(byte)

    def draw(self, file):
        for byte in self.byte:
            file.draw(byte)


    def draw_indices(self, file):
        for byte in self.byte:
            byte.draw_index(file)


    @property
    def bytes(self):
        return self.byte


    @property
    def bits(self):
        for byte in self.byte:
            yield from self.byte


    @property
    def x_borders(self):
        yield self.byte[0].right.x
        for byte in self.byte:
            yield byte.left.x

class Struct:
    pass


active_bit = 'fill=green!75'
active_even_bit = 'fill=blue!25'
active_odd_bit = 'fill=red!25'

active_byte = 'fill=white'
inactive_byte = 'fill=gray!15'


def draw_register(file, reg, name):
    margin_left = 1.0
    margin_right = 0.4
    for y in reg.top.y, reg.bottom.y:
        file.hline(y, reg.left.x - margin_left, reg.left.x, "dashed")
        file.hline(y, reg.right.x, reg.right.x + margin_right, "dashed")

    file.label(reg.left, name, "anchor=east")
    file.draw(reg)


def draw_step(file, algorithm):

    x  = 0
    y  = 0
    W  = 14
    H  = 0.5
    vs = 0.2

    const_lane = AVX512Lane(x, y, W, H, algorithm.lane0, byte_cls=WHOLE_BYTE)
    y -= H + vs
    var_lane   = AVX512Lane(x, y, W, H, algorithm.lane1, byte_cls=WHOLE_BYTE)
    for byte in var_lane.byte:
        if byte.index == algorithm.index:
            byte.style = active_byte
        else:
            byte.style = inactive_byte

    y -= H + 4*vs

    lane_in0 = AVX512Lane(x, y, W, H, algorithm.lane0reversed)
    for byte in lane_in0.byte:
        byte.index = 7 - byte.index
        byte.index_label = "\\tiny{byte %d}" % byte.index

    for byte in lane_in0.byte:
        index = bfs(byte.value)
        byte.bit[index].style = active_bit

    y -= H + 2*vs
    lane_in1 = AVX512Lane(x, y, W, H, algorithm.lane1populated)
    for byte in lane_in1.byte:
        byte.index = algorithm.index
        byte.index_label = "\\tiny{byte %d}" % byte.index
        for bit in byte.bit:
            if bit.index < 4:
                bit.style = active_even_bit
            else:
                bit.style = active_odd_bit
    y -= H + vs

    y -= 5*vs

    lanes_anded = AVX512Lane(x, y, W, H, algorithm.lanes_anded)
    for byte in lanes_anded.byte:
        for bit in byte.bits:
            if bit.index == algorithm.order[byte.index]:
                if bit.index < 4:
                    bit.style = active_even_bit
                else:
                    bit.style = active_odd_bit
            else:
                bit.label = ''
    y -= H + vs

    y -= 5*vs

    lane_result = AVX512Lane(x, y, W, H, [0]*8, byte_cls=WHOLE_BYTE)
    for i in range(8):
        byte = lane_result.byte[i]
        if byte.index != algorithm.index:
            byte.label = ''
            byte.style = inactive_byte
        else:
            byte = BYTE(byte.x, byte.y, byte.w, byte.h)
            byte.value = algorithm.result
            lane_result.byte[i] = byte
            for bit in byte.bits:
                bit.style = lanes_anded.byte[bit.index].bit[algorithm.order[bit.index]].style

    draw_horiz_brace(file, const_lane.left.x, const_lane.right.x, const_lane.top.y,
                     r"lane \texttt{j} (\texttt{j} = 0\ldots 7)")

    for x in const_lane.x_borders:
        file.vline(x, const_lane.top.y, lane_result.bottom.y - vs, "densely dotted")

    draw_register(file, const_lane, texttt("A"))
    draw_register(file, var_lane, texttt("x"))
    file.draw(var_lane)

    file.draw(lane_in0)
    lane_in0.draw_indices(file)
    file.label(lane_in0.left, texttt("rev(A[j])"), "anchor=east")
    file.draw(lane_in1)
    lane_in1.draw_indices(file)
    file.label(lane_in1.left, texttt("x[j][%d]" % algorithm.index), "anchor=east")


    file.draw(lanes_anded)
    file.label(lanes_anded.left, texttt("tmp"), "anchor=east")
    for byte in lanes_anded.bytes:
        file.label(byte.top, r"\tiny{result bit %d}" % byte.index, "anchor=south")
        for bit in byte.bits:
            if not bit.label:
                continue
            bit.draw_index(file)

    draw_register(file, lane_result, texttt("dst"))

    for i in range(8):
        result_byte = lane_result.byte[algorithm.index]
        for bit in lanes_anded.byte[i].bits:
            if not bit.label:
                continue

            file.line(result_byte.bit[i].top, bit.bottom, "line width=0.5")

    # labels
    def picture_label(xc, yc, width, height, label, style=''):
        p0 = Point(xc - width/2, yc - height/2)
        p1 = Point(xc + width/2, yc + height/2)
        file.rectangle(p0, p1, style)
        file.label(Point(xc, yc), label)

    picture_label(lanes_anded.top.x, (lanes_anded.top.y + lane_in1.bottom.y) / 2,
                  lanes_anded.w + 0.4, 0.4,
                  texttt(r"tmp = rev(A[j]) \& x[j][%d]" % algorithm.index),
                  'fill=yellow!25,rounded corners=5pt')

    b = lane_result.byte[algorithm.index]
    picture_label(b.top.x, ((b.top + lanes_anded.bottom) / 2).y, 5, 0.5,
                  r"$\textrm{bit}_i$ = \texttt{parity(tmp.byte[i])}",
                  'fill=yellow!25,rounded corners=5pt')

    file.rectangle(lane_in0.lt - Point(1.9, -0.3), lane_result.rb + Point(0.5, -0.3),
                   'blue,dashed,thick,rounded corners=10pt')


def parse_args():
    parser = argparse.ArgumentParser()

    def intlist(s):
        return map(int, s.split(','))

    def hexlist(s):
        return map(lambda x: int(x, 16), s.split(','))

    parser.add_argument("path",
                        help="output TeX file name")
    parser.add_argument("--index", type=int,
                        help="input index (0..7)",
                        default=4)
    parser.add_argument("--order", type=intlist,
                        help="bit order given as 8 numbers spearate by the comma",
                        default=[0, 4, 1, 5, 2, 6, 3, 7])
    parser.add_argument("--input", type=hexlist,
                        help="input bytes given as 8 hex values separate by the comma",
                        default=[0xfa, 0x45, 0x89, 0x13, 0x78, 0x65, 0xfc, 0x0b])
    parser.add_argument("--allsteps", action="store_true",
                        help="perform all steps from 0 to index",
                        default=False)

    return parser.parse_args()


if __name__ == '__main__':
    buf = StringIO()
    buf.write(r"\begin{tikzpicture}")

    args = parse_args()
    if args.allsteps:
        algorithm = Algorithm(0, args.order, args.input)
        for index in range(args.index + 1):
            algorithm.index = index
    else:
        algorithm = Algorithm(args.index, args.order, args.input)


    draw_step(File(buf), algorithm)
    buf.write(r"\end{tikzpicture}")

    with open(args.path, 'wt') as f:
        f.write(buf.getvalue())
