from tikz import *


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
