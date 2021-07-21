import sys

from tikz import *
from common import *


def main():
    file = File()
    draw(file, "aącólź")

    with open(sys.argv[1], 'wt') as f:
        file.save(f)


UTF8_BIT = 'fill=gray!50'
MASKED   = ''
UNUSED   = 'fill=gray!25'
ASCII    = 'fill=yellow!50'
BYTE0    = 'fill=blue!50'
BYTE1    = 'fill=green!50'


def decompose(s):
    result = []
    for c in s:
        b = bytes(c, encoding='utf-8')
        if len(b) == 1:
            result.append((ASCII, b[0]))
        elif len(b) == 2:
            result.append((BYTE0, b[0]))
            result.append((BYTE1, b[1]))
        else:
            assert False

    return result


def draw(file, s):
    assert len(s) == 6
    bytes = decompose(s)

    ctx = Context()
    ctx.d = 0.2
    ctx.h = 0.35
    vspace = -3

    input = prepare_input(ctx, bytes)
    ctx.y += vspace * ctx.d

    perm = prepare_perm(ctx, bytes)
    ctx.y += vspace * ctx.d

    ascii = prepare_ascii(ctx, bytes)
    ctx.y += vspace * ctx.d

    highbyte = prepare_highbyte(ctx, bytes)
    ctx.y += vspace * ctx.d

    shifted_highbyte = prepare_shifted_highbyte(ctx, bytes)
    ctx.y += vspace * ctx.d

    combined = prepare_combined(ctx, ascii, shifted_highbyte)

    expand = [('L', 0, 0)]
    src_idx = 0
    dst_idx = 0
    for t, b in bytes:
        if t == ASCII:
            src_idx += 8
            dst_idx += 16
            expand.append(('R', src_idx - 1, dst_idx - 1))
        elif t == BYTE0:
            src_idx += 8
        elif t == BYTE1:
            src_idx += 8
            dst_idx += 16
            expand.append(('R', src_idx - 1, dst_idx -1))

    for side, src_idx, dst_idx in expand:
        src = input.bits[src_idx]
        dst = perm.bits[dst_idx]
        if side == 'L':
            p1 = src.bottom_left
            p2 = dst.top_left
        else:
            p1 = src.bottom_right
            p2 = dst.top_right

        file.line(p1, p2, 'densely dotted')

    expand = [('L', 0, 0)]
    for i in range(1, 6+1):
        expand.append(('R', i*16-1, i*16-1))

    for side, src_idx, dst_idx in expand:
        src = perm.bits[src_idx]
        dst = combined.bits[dst_idx]
        if side == 'L':
            p1 = src.bottom_left
            p2 = dst.top_left
        else:
            p1 = src.bottom_right
            p2 = dst.top_right

        file.line(p1, p2, 'densely dotted')

    inputs = [
        (input,             r'UTF-8'),
        (perm,              r'a'),  # r'v1'),
        (ascii,             r'b'), # r'v2 = v1 \& byte(0x7f)'),
        (highbyte,          r'c'), # r'v3 = v1 \& word(0x1f00)'),
        (shifted_highbyte,  r'd'), # r'v4 = v3 >> 2'),
        (combined,          r'UTF-16'),
    ]

    for bs, label in inputs:
        bs.draw(file)
        file.label(bs.bits[0].left, texttt(label), 'anchor=east')

    # label input chars
    bs = input
    bit = 0
    idx = 0
    for t, b in bytes:
        label = f'char {idx}'
        if t == ASCII:
            bs.top_brace(file, bit, bit + 7, label)
            bit += 8
            idx += 1
        elif t == BYTE0:
            bs.top_brace(file, bit, bit + 15, label)
            bit += 16
            idx += 1

    # label output chars
    bs = combined
    for idx in range(6):
        bit = idx * 16

        label = f'char {idx}'
        bs.bottom_brace(file, bit, bit + 15, label)


def as_spec(byte):
    t, v = byte
    bits = '{:08b}'.format(v)

    if t == ASCII:
        return [(UNUSED, bits[0:1]), (ASCII, bits[1:8])]
    if t == BYTE0:
        return [(UTF8_BIT, bits[0:3]), (BYTE0, bits[3:8])]
    if t == BYTE1:
        return [(UTF8_BIT, bits[0:2]), (BYTE1, bits[2:8])]

    assert False


class BitStream(Rectangle):
    def __init__(self, x, y, w, h, spec):
        self.bits = []
        for style, bits in spec:
            for label in bits:
                fmt = r"\tiny{%s}" % label
                B = BIT(x, y, w, h, fmt, style, None)
                B.value = bool(int(label))
                self.bits.append(B)
                x += w

        self.x = x
        self.y = y
        self.w = len(self.bits) * w
        self.h = h


    def top_brace(self, file, b0, b1, label):
        p1 = self.bits[b0].top_left
        p2 = self.bits[b1].top_right

        draw_horiz_brace(file, p1.x, p2.x, p1.y, label)


    def bottom_brace(self, file, b0, b1, label):
        p1 = self.bits[b0].bottom_left
        p2 = self.bits[b1].bottom_right

        draw_horiz_brace(file, p2.x, p1.x, p1.y, label, 'below')

    
    def draw(self, file):
        for bit in self.bits:
            bit.draw(file)


def unused(n):
    return (UNUSED, '0' * n)


def masked(n):
    return (MASKED, '0' * n)


def prepare_input(ctx, bytes):
    spec = []
    for byte in bytes:
        spec.extend(as_spec(byte))

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_perm(ctx, bytes):
    spec = []
    i = 0
    while i < len(bytes):
        t, b = bytes[i]
        if b & 0x80:
            tmp = as_spec(bytes[i]) + as_spec(bytes[i+1])
            spec.extend(tmp)
            i += 2
        else:
            tmp = [unused(8)] + as_spec(bytes[i])
            spec.extend(tmp)
            i += 1

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_ascii(ctx, bytes):
    spec = []
    i = 0
    while i < len(bytes):
        t, b = bytes[i]
        if b & 0x80:
            tmp = [masked(8), masked(1), (UTF8_BIT, '0'), (BYTE1, as_bin(bytes[i+1][1], 6))]
            spec.extend(tmp)
            i += 2
        else:
            spec.append(masked(8))
            spec.extend(as_spec(bytes[i]))
            i += 1

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def as_bin(byte, bits_count):
    tmp = '{:08b}'.format(byte)
    return tmp[8 - bits_count:]


def prepare_highbyte(ctx, bytes):
    spec = []
    i = 0
    while i < len(bytes):
        t, b = bytes[i]
        if b & 0x80:
            tmp = [masked(3), (BYTE0, as_bin(b & 0x1f, 5)), masked(8)]
            spec.extend(tmp)
            i += 2
        else:
            spec.append(masked(16))
            i += 1

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def split_init_bits(spec):
    result = []
    for style, labels in spec:
        for label in labels:
            result.append((style, label))

    return result


def prepare_shifted_highbyte(ctx, bytes):
    spec = []
    i = 0
    while i < len(bytes):
        t, b = bytes[i]
        if b & 0x80:
            tmp = [masked(3), (BYTE0, as_bin(b & 0x1f, 5)), masked(8)]
            spec.extend(tmp)
            i += 2
        else:
            spec.append(masked(16))
            i += 1

    spec = split_init_bits(spec)
    spec = [masked(2)] + spec[:-2]

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_combined(ctx, ascii, shifted_highbyte):
    spec = []
    for B1, B2 in zip(ascii.bits, shifted_highbyte.bits):
        b1 = B1.value
        b2 = B2.value
        assert not (b1 and b2)
        if b1:
            spec.append((B1.style, '1'))
        elif b2:
            spec.append((B2.style, '1'))
        else:
            style = MASKED
            if B1.style in (ASCII, BYTE0, BYTE1):
                style = B1.style
            elif B2.style in (ASCII, BYTE0, BYTE1):
                style = B2.style

            spec.append((style, '0'))
            
    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def bit_stream(*args):
    return BitStream(*args)
    

if __name__ == '__main__':
    main()
