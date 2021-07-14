import sys

from tikz import *


def main():
    file = File()
    variants = sys.argv[2]
    draw(file, variants)

    with open(sys.argv[1], 'wt') as f:
        file.save(f)


class Context:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.d = 0.5
        self.maxwidth = None # set by draw_4bytes_case, as its the widest image


UTF8_BIT = 'fill=gray!50'
UNUSED   = ''
ASCII    = ''
BYTE0    = 'fill=red!25'
BYTE1    = 'fill=green!25'
BYTE2    = 'fill=blue!25'
BYTE3    = 'fill=magenta!25'


def draw(file, variants):
    ctx = Context()
    vspace = 7
    if '4' in variants:
        draw_4bytes_case(ctx, file)
        ctx.y += vspace * ctx.d

    if '3' in variants:
        draw_3bytes_case(ctx, file)
        ctx.y += vspace * ctx.d

    if '2' in variants:
        draw_2bytes_case(ctx, file)
        ctx.y += vspace * ctx.d

    if '1' in variants:
        draw_1byte_case(ctx, file)


def draw_1byte_case(ctx, file):
    # UTF-8
    byte0 = [(UTF8_BIT, "0"), (BYTE0, "abcdefg")]
    spec  = [byte0]
    maxwidth = draw_utf8(ctx, file, spec)
    if ctx.maxwidth is None:
        ctx.maxwidth = maxwidth

    ctx.y -= 1.5 * ctx.d

    # UTF-16
    word0 = [(UTF8_BIT, "0" * 9), (BYTE0, "abcdefg")]
    spec  = [word0]
    draw_utf16(ctx, file, spec)


def draw_2bytes_case(ctx, file):
    # UTF-8: abcde_fghijk
    byte0 = [(UTF8_BIT, "110"), (BYTE0, "abcde")]
    byte1 = [(UTF8_BIT, "10"), (BYTE1, "fghijk")]
    spec  = [byte0, byte1]
    maxwidth = draw_utf8(ctx, file, spec)
    if ctx.maxwidth is None:
        ctx.maxwidth = maxwidth

    ctx.y -= 1.5 * ctx.d

    # UTF-16
    word0 = [(UTF8_BIT, "0" * 5), (BYTE0, "abcde"), (BYTE1, "fghijk")]
    spec  = [word0]
    draw_utf16(ctx, file, spec)


def draw_3bytes_case(ctx, file):
    # UTF-8: abcd_efghij_klmnop
    byte0 = [(UTF8_BIT, "1110"), (BYTE0, "abcd")]
    byte1 = [(UTF8_BIT, "10"), (BYTE1, "efghij")]
    byte2 = [(UTF8_BIT, "10"), (BYTE2, "klmnop")]
    spec  = [byte0, byte1, byte2]
    maxwidth = draw_utf8(ctx, file, spec)
    if ctx.maxwidth is None:
        ctx.maxwidth = maxwidth

    ctx.y -= 1.5 * ctx.d

    # UTF-16
    word0 = [(BYTE0, "abcd"), (BYTE1, "efghij"), (BYTE2, "klmnop")]
    spec  = [word0]
    draw_utf16(ctx, file, spec)


def draw_4bytes_case(ctx, file):
    # UTF-8: abc_defghi_jklmno_pqrstu
    byte0 = [(UTF8_BIT, "11110"), (BYTE0, "abc")]
    byte1 = [(UTF8_BIT, "10"), (BYTE1, "defghi")]
    byte2 = [(UTF8_BIT, "10"), (BYTE2, "jklmno")]
    byte3 = [(UTF8_BIT, "10"), (BYTE3, "pqrstu")]
    spec  = [byte0, byte1, byte2, byte3]
    maxwidth = draw_utf8(ctx, file, spec)
    if ctx.maxwidth is None:
        ctx.maxwidth = maxwidth

    ctx.y -= 1.5 * ctx.d

    # UTF-16: ABCDEFGHIJKLMNOPQRST
    word0 = [(UTF8_BIT, "110111"), (UNUSED, "ABCDEFGHIJ")]
    word1 = [(UTF8_BIT, "110110"), (UNUSED, "KLMNOPQRST")]
    spec  = [word0, word1]
    draw_utf16(ctx, file, spec)


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


if __name__ == '__main__':
    main()
