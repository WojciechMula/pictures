from tikz import *


UTF8_BIT  = 'fill=gray!50'
UTF16_BIT = 'fill=gray!50'
MASKED   = ''
UNUSED   = 'fill=gray!25'
ASCII    = 'fill=yellow!50'
BYTE0    = 'fill=blue!50'
BYTE1    = 'fill=green!50'
BYTE2    = 'fill=red!50'
BYTE3    = 'fill=magenta!50'


class Context:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.d = 0.5
        self.maxwidth = None


def draw_utf8(ctx, file, spec):
    x = ctx.x
    y = ctx.y
    d = ctx.d

    all_bytes = []
    for byte_spec in spec:
        B = BYTE(x, y, d * 8, d)
        all_bytes.append(B)

        index = 7
        for style, bits in byte_spec:
            for label in bits:
                bit = B.bits[index]
                bit.label = label
                bit.style = style
                index -= 1

        assert index == -1

        x += B.w + d/2

    if ctx.maxwidth is not None:
        x_shift = ctx.maxwidth - x
    else:
        x_shift = 0.0

    for i, b in enumerate(all_bytes):
        b.x += x_shift
        for bit in b.bits:
            bit.x += x_shift

        b.draw(file)
        draw_horiz_brace(file, b.left.x, b.right.x, b.top.y, "UTF-8 byte %d" % i, 'above')

    return x


def draw_utf16(ctx, file, spec):
    x = ctx.x
    y = ctx.y
    d = ctx.d

    all_words = []
    for word_spec in spec:
        W = WORD(x, y, d * 16, d)
        all_words.append(W)

        index = 15
        for style, bits in word_spec:
            for label in bits:
                bit = W.bits[index]
                bit.label = label
                bit.style = style
                index -= 1

        assert index == -1

        x += W.w + d/2

    if ctx.maxwidth is not None:
        x_shift = ctx.maxwidth - x
    else:
        x_shift = 0.0

    for i, w in enumerate(all_words):
        w.x += x_shift
        for bit in w.bits:
            bit.x += x_shift

        w.draw(file)
        draw_horiz_brace(file, w.right.x, w.left.x, w.bottom.y, "UTF-16 word %d" % i, 'below')

    return x


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


    def bin_string(self):
        return ''.join('1' if bit.value else '0' for bit in self.bits)


    def spec(self):
        return [(bit.style, '1' if bit.value else '0') for bit in self.bits]


    def draw(self, file):
        for bit in self.bits:
            bit.draw(file)


class BitStreamHighdword(BitStream):
    def draw(self, file):
        for bit in self.bits[:32]:
            bit.draw(file)


def bit_stream(*args):
    return BitStream(*args)


def bit_stream_highdword(*args):
    return BitStreamHighdword(*args)


def unused(n):
    return (UNUSED, '0' * n)


def masked(n):
    return (MASKED, '0' * n)
