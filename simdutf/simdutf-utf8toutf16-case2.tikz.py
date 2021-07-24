import sys

from tikz import *
from common import *


def main():
    file = File()
    draw(file, "a\u14FFcó")

    with open(sys.argv[1], 'wt') as f:
        file.save(f)


def decompose(s):
    result = []
    for c in s:
        b = bytes(c, encoding='utf-8')
        print(b)
        if len(b) == 1:
            result.append((ASCII, b[0], 1))
        elif len(b) == 2:
            result.append((BYTE0, b[0], 2))
            result.append((BYTE1, b[1]))
        elif len(b) == 3:
            result.append((BYTE0, b[0], 3))
            result.append((BYTE1, b[1]))
            result.append((BYTE2, b[2]))
        else:
            assert False

    return result


def draw(file, s):
    assert len(s) == 4
    raw = decompose(s)

    ctx = Context()
    ctx.d = 0.15
    ctx.h = 0.25
    vspace = -3

    input = prepare_input(ctx, raw)
    ctx.y += vspace * 1.5 * ctx.d

    perm = prepare_perm(ctx, raw)
    ctx.y += vspace * ctx.d

    ascii = prepare_ascii(ctx, perm)
    ctx.y += vspace * ctx.d

    middlebyte = prepare_middlebyte(ctx, perm)
    ctx.y += vspace * ctx.d

    middlebyte_shifted = prepare_middlebyte_shifted(ctx, middlebyte)
    ctx.y += vspace * ctx.d

    highbyte = prepare_highbyte(ctx, perm)
    ctx.y += vspace * ctx.d

    highbyte_shifted = prepare_highbyte_shifted(ctx, highbyte)
    ctx.y += vspace * ctx.d

    combined = prepare_combined(ctx, ascii, middlebyte_shifted, highbyte_shifted)
    ctx.y += vspace * 1.5 * ctx.d

    combined_repacked = prepare_combined_repacked(ctx, combined)

    #
    def connect(bs1, bs2, pattern):
        for side, src_idx, dst_idx in pattern:
            src = bs1.bits[src_idx]
            dst = bs2.bits[dst_idx]
            if side == 'L':
                p1 = src.bottom_left
                p2 = dst.top_left
            else:
                p1 = src.bottom_right
                p2 = dst.top_right

            file.line(p1, p2, 'densely dotted')


    expand = [('L', 0, 0)]
    src_idx = 0
    dst_idx = 0
    for idx, c in enumerate(s):
        tmp = bytes(c, encoding='utf-8')
        src_idx += len(tmp) * 8
        dst_idx += 32
        expand.append(('R', src_idx - 1, dst_idx - 1))

    connect(input, perm, expand)

    pattern = [('L', 0, 0)]
    for i in range(1, 4+1):
        pattern.append(('R', i*32-1, i*32-1))
    
    connect(perm, combined, pattern)

    pattern = [('L', 0, 0)]
    for i in range(1, 4+1):
        pattern.append(('R', i*32-1, i*16-1))

    connect(combined, combined_repacked, pattern)


    inputs = [
        (input,                 'UTF-8'),
        (perm,                  'a'),
        (ascii,                 'b'),
        (middlebyte,            'c'),
        (middlebyte_shifted,    "c'"),
        (highbyte,              'd'),
        (highbyte_shifted,      "d'"),
        (combined,              "e"),
        (combined_repacked,     'UTF-16'),
    ]

    for bs, label in inputs:
        bs.draw(file)
        file.label(bs.bits[0].left, texttt(label), 'anchor=east')

    # label input chars
    bs = input
    bit = 0
    for idx, c in enumerate(s):
        tmp = bytes(c, encoding='utf-8')
        label = f'char {idx}'

        bs.top_brace(file, bit, bit + len(tmp) * 8 - 1, label)
        bit += len(tmp) * 8

    # label output chars
    bs = combined_repacked
    for idx in range(4):
        bit = idx * 16

        label = f'char {idx}'
        bs.bottom_brace(file, bit, bit + 15, label)


def as_spec(byte):
    t = byte[0]
    v = byte[1]
    bits = '{:08b}'.format(v)

    if t == ASCII:
        return [(UNUSED, bits[0:1]), (ASCII, bits[1:8])]
    if t == BYTE0:
        k = byte[2]
        if k == 2:
            return [(UTF8_BIT, bits[0:3]), (BYTE0, bits[3:8])]
        elif k == 3:
            return [(UTF8_BIT, bits[0:4]), (BYTE0, bits[4:8])]
        assert False
    if t == BYTE1:
        return [(UTF8_BIT, bits[0:2]), (BYTE1, bits[2:8])]
    if t == BYTE2:
        return [(UTF8_BIT, bits[0:2]), (BYTE1, bits[2:8])]

    assert False


def prepare_input(ctx, bytes):
    spec = []
    for byte in bytes:
        spec.extend(as_spec(byte))

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_perm(ctx, bytes):
    spec = []
    i = 0
    while i < len(bytes):
        t = bytes[i][0]
        b = bytes[i][1]
        k = bytes[i][2]
        if k == 1: # ASCII
            tmp = [unused(3*8)] + as_spec(bytes[i])
            spec.extend(tmp)
        elif k == 2:
            tmp = [unused(2*8)] + as_spec(bytes[i]) + as_spec(bytes[i+1])
            spec.extend(tmp)
        elif k == 3:
            tmp = [unused(1*8)] + as_spec(bytes[i]) + as_spec(bytes[i+1]) + as_spec(bytes[i+2])
            spec.extend(tmp)
        else:
            assert False
        
        i += k

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def bitwise_and(bitstream, mask_bits):
    assert len(mask_bits) == len(bitstream.bits)
    spec = []
    for bit, maskbit in zip(bitstream.bits, mask_bits):
        if maskbit == '0':
            spec.append(masked(1))
        else:
            v = '1' if bit.value else '0'
            spec.append((bit.style, v))
    return spec


def shift_right_epu32(bitstream, shift):
    assert len(bitstream.bits) % 32 == 0
    spec = []
    for i in range(0, len(bitstream.bits), 32):
        dword = bitstream.bits[i:i+32]

        spec.append(masked(shift))
        dword = dword[:-shift]
        for bit in dword:
            v = '1' if bit.value else '0'
            spec.append((bit.style, v))
        
    return spec


def pack_epu32_epi16(bitstream):
    assert len(bitstream.bits) % 32 == 0
    spec = []
    for i in range(0, len(bitstream.bits), 32):
        dword = bitstream.bits[i:i+32]

        dword = dword[16:]
        for bit in dword:
            v = '1' if bit.value else '0'
            spec.append((bit.style, v))
        
    return spec


def prepare_ascii(ctx, perm):
    mask_bits = 4 * '{:032b}'.format(0x7f)
    spec = bitwise_and(perm, mask_bits)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_middlebyte(ctx, perm):
    mask_bits = 4 * '{:032b}'.format(0x3f00)
    spec = bitwise_and(perm, mask_bits)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_middlebyte_shifted(ctx, middlebyte):
    spec = shift_right_epu32(middlebyte, 2)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_highbyte(ctx, perm):
    mask_bits = 4 * '{:032b}'.format(0x0f0000)
    spec = bitwise_and(perm, mask_bits)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_highbyte_shifted(ctx, highbyte):
    spec = shift_right_epu32(highbyte, 4)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_combined(ctx, ascii, middlebyte_shifted, highbyte_shifted):
    spec = []
    assert len(ascii.bits) == len(middlebyte_shifted.bits)
    assert len(ascii.bits) == len(highbyte_shifted.bits)
    for B1, B2, B3 in zip(ascii.bits, middlebyte_shifted.bits, highbyte_shifted.bits):
        b1 = B1.value
        b2 = B2.value
        b3 = B3.value
        if b1:
            spec.append((B1.style, '1'))
        elif b2:
            spec.append((B2.style, '1'))
        elif b3:
            spec.append((B3.style, '1'))
        else:
            style = MASKED
            if B1.style in (ASCII, BYTE0, BYTE1, BYTE2):
                style = B1.style
            elif B2.style in (ASCII, BYTE0, BYTE1, BYTE2):
                style = B2.style
            elif B3.style in (ASCII, BYTE0, BYTE1, BYTE2):
                style = B3.style

            spec.append((style, '0'))
            
    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_combined_repacked(ctx, combined):
    spec = pack_epu32_epi16(combined)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


if __name__ == '__main__':
    main()
