import sys

from tikz import *
from common import *


def main():
    file = File()
    draw(file, "\U000ffa51\u14FF")

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
        elif len(b) == 4:
            result.append((BYTE0, b[0], 4))
            result.append((BYTE1, b[1]))
            result.append((BYTE2, b[2]))
            result.append((BYTE3, b[3]))
        else:
            assert False

    return result


def draw(file, s):
    assert len(s) == 2
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

    middlehighbyte = prepare_middlehighbyte(ctx, perm)
    ctx.y += vspace * ctx.d

    correct = prepare_middlehighbyte_correct(ctx, perm)
    ctx.y += vspace * ctx.d

    middlehighbyte_corrected = prepare_middlehighbyte_corrected(ctx, middlehighbyte, correct)
    ctx.y += vspace * ctx.d

    middlehighbyte_shifted = prepare_middlehighbyte_shifted(ctx, middlehighbyte_corrected)
    ctx.y += vspace * ctx.d

    highbyte = prepare_highbyte(ctx, perm)
    ctx.y += vspace * ctx.d

    highbyte_shifted = prepare_highbyte_shifted(ctx, highbyte)
    ctx.y += vspace * ctx.d

    composed = prepare_composed(ctx, ascii, middlebyte_shifted, middlehighbyte_shifted, highbyte_shifted)
    ctx.y += vspace * ctx.d

    # surrogate pair handling
    composedminus = prepare_composedminus(ctx, composed)
    ctx.y += vspace * ctx.d

    lowtenbits = prepare_lowtenbits(ctx, composed)
    ctx.y += vspace * ctx.d

    lowtenbitsadd = prepare_lowtenbitsadd(ctx, lowtenbits)
    ctx.y += vspace * ctx.d

    lowtenbitsadd_shifted = prepare_lowtenbitsadd_shifted(ctx, lowtenbitsadd)
    ctx.y += vspace * ctx.d

    hightenbits = prepare_hightenbits(ctx, composed)
    ctx.y += vspace * ctx.d

    hightenbitsadd = prepare_hightenbitsadd(ctx, hightenbits)
    ctx.y += vspace * ctx.d

    surrogates = prepare_surrogates(ctx, lowtenbitsadd_shifted, hightenbitsadd)


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
    for i in range(1, 2+1):
        pattern.append(('R', i*32-1, i*32-1))
    
    connect(perm, composed, pattern)

    pattern = [('L', 0, 0)]
    for i in range(1, 1+1):
        pattern.append(('R', i*32-1, i*32-1))

    connect(composed, surrogates, pattern)

    inputs = [
        (input,                         'UTF-8'),
        (perm,                          'a'),
        (ascii,                         'b'),
        (middlebyte,                    'c'),
        (middlebyte_shifted,            "c'"),
        (middlehighbyte,                "d"),
        (correct,                       "e"),
        (middlehighbyte_corrected,      "d'"),
        (middlehighbyte_shifted,        "d''"),
        (highbyte,                      'f'),
        (highbyte_shifted,              "f'"),
        (composed,                      "UTF-16"),
        (composedminus,                 "g"),
        (lowtenbits,                    "h"),
        (lowtenbitsadd,                 "h'"),
        (lowtenbitsadd_shifted,         "h''"),
        (hightenbits,                   "i"),
        (hightenbitsadd,                "i'"),
        (surrogates,                    "UTF-16"),
    ]

    for bs, label in inputs:
        bs.draw(file)
        file.label(bs.bits[0].left, texttt(label), 'anchor=east')

    # label the input chars
    bs = input
    bit = 0
    for idx, c in enumerate(s):
        tmp = bytes(c, encoding='utf-8')
        label = f'char {idx}'

        bs.top_brace(file, bit, bit + len(tmp) * 8 - 1, label)
        bit += len(tmp) * 8

    # label the output chars
    bs = composed
    bit = 48
    label = 'char 1'
    bs.bottom_brace(file, bit, bit + 15, label)

    bs = surrogates
    bit = 0
    label = 'surrogate pair 0'
    bs.bottom_brace(file, bit, bit + 31, label)


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
        elif k == 4:
            return [(UTF8_BIT, bits[0:5]), (BYTE0, bits[5:8])]
        assert False
    if t == BYTE1:
        return [(UTF8_BIT, bits[0:2]), (BYTE1, bits[2:8])]
    if t == BYTE2:
        return [(UTF8_BIT, bits[0:2]), (BYTE2, bits[2:8])]
    if t == BYTE3:
        return [(UTF8_BIT, bits[0:2]), (BYTE3, bits[2:8])]

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
        elif k == 4:
            tmp = as_spec(bytes[i]) + as_spec(bytes[i+1]) + as_spec(bytes[i+2]) + as_spec(bytes[i+3])
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


def bitwise_xor(bitstream, mask_bits):
    assert len(mask_bits) == len(bitstream.bits)

    spec = []
    for bit, maskbit in zip(bitstream.bits, mask_bits):
        b1 = bit.value
        b2 = (maskbit == '1')
        if b2:
            if b1:
                spec.append(masked(1))
            else:
                assert False
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
    mask_bits = 2 * '{:032b}'.format(0x7f)
    spec = bitwise_and(perm, mask_bits)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_middlebyte(ctx, perm):
    mask_bits = 2 * '{:032b}'.format(0x3f00)
    spec = bitwise_and(perm, mask_bits)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_middlebyte_shifted(ctx, middlebyte):
    spec = shift_right_epu32(middlebyte, 2)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_middlehighbyte(ctx, perm):
    mask_bits = 2 * '{:032b}'.format(0x3f0000)
    spec = bitwise_and(perm, mask_bits)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_middlehighbyte_correct(ctx, perm):
    mask_bits = 2 * '{:032b}'.format(0x400000)
    spec1 = bitwise_and(perm, mask_bits)
    tmp = bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec1)

    spec2 = shift_right_epu32(tmp, 1)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec2)


def prepare_middlehighbyte_corrected(ctx, middlehighbyte, correct):
    mask_bits = correct.bin_string()
    spec = bitwise_xor(middlehighbyte, mask_bits)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_middlehighbyte_shifted(ctx, middlehighbyte):
    spec = shift_right_epu32(middlehighbyte, 4)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_highbyte(ctx, perm):
    mask_bits = 2 * '{:032b}'.format(0x07000000)
    spec = bitwise_and(perm, mask_bits)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_highbyte_shifted(ctx, highbyte):
    spec = shift_right_epu32(highbyte, 6)

    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_composed(ctx, ascii, middlebyte_shifted, middlehighbyte_shifted, highbyte_shifted):
    spec = []
    assert len(ascii.bits) == len(middlebyte_shifted.bits)
    assert len(ascii.bits) == len(middlehighbyte_shifted.bits)
    assert len(ascii.bits) == len(highbyte_shifted.bits)
    for B1, B2, B3, B4 in zip(ascii.bits, middlebyte_shifted.bits, middlehighbyte_shifted.bits, highbyte_shifted.bits):
        b1 = B1.value
        b2 = B2.value
        b3 = B3.value
        b4 = B4.value
        if b1:
            spec.append((B1.style, '1'))
        elif b2:
            spec.append((B2.style, '1'))
        elif b3:
            spec.append((B3.style, '1'))
        elif b4:
            spec.append((B4.style, '1'))
        else:
            style = MASKED
            if B1.style in (ASCII, BYTE0, BYTE1, BYTE2, BYTE3):
                style = B1.style
            elif B2.style in (ASCII, BYTE0, BYTE1, BYTE2, BYTE3):
                style = B2.style
            elif B3.style in (ASCII, BYTE0, BYTE1, BYTE2, BYTE3):
                style = B3.style
            elif B4.style in (ASCII, BYTE0, BYTE1, BYTE2, BYTE3):
                style = B4.style

            spec.append((style, '0'))
            
    return bit_stream(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_composedminus(ctx, composed):
    dword = int(composed.bin_string()[:32], 2)
    dword -= 0x10000
    image = 2 * '{:032b}'.format(dword)
    assert len(image) == len(composed.bits)

    spec = []
    for bit, value in zip(composed.bits, image):
        spec.append((bit.style, value))

    return bit_stream_highdword(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_lowtenbits(ctx, composedminus):
    mask_bits = 2 * '{:032b}'.format(0x3ff)
    spec = bitwise_and(composedminus, mask_bits)

    return bit_stream_highdword(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_lowtenbitsadd(ctx, lowtenbits):
    # 0xdc >> 2 = 0b110111
    merge = {
        10: (UTF16_BIT, '1'),
        11: (UTF16_BIT, '1'),
        12: (UTF16_BIT, '1'),
        13: (UTF16_BIT, '0'),
        14: (UTF16_BIT, '1'),
        15: (UTF16_BIT, '1'),
    }
    spec = lowtenbits.spec()
    for i, s in merge.items():
        spec[31-i] = s

    return bit_stream_highdword(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_hightenbits(ctx, composedminus):
    spec = shift_right_epu32(composedminus, 10)

    return bit_stream_highdword(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_hightenbitsadd(ctx, hightenbits):
    # 0xdc >> 2 = 0b110110
    merge = {
        10: (UTF16_BIT, '0'),
        11: (UTF16_BIT, '1'),
        12: (UTF16_BIT, '1'),
        13: (UTF16_BIT, '0'),
        14: (UTF16_BIT, '1'),
        15: (UTF16_BIT, '1'),
    }
    spec = hightenbits.spec()
    for i, s in merge.items():
        spec[31-i] = s

    return bit_stream_highdword(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_lowtenbitsadd_shifted(ctx, lowtenbitsadd):
    spec = lowtenbitsadd.spec()
    spec = spec[16:32] + spec[0:16] + spec[32:]

    return bit_stream_highdword(ctx.x, ctx.y, ctx.d, ctx.h, spec)


def prepare_surrogates(ctx, lowtenbitsadd_shifted, hightenbitsadd):
    spec1 = lowtenbitsadd_shifted.spec()
    spec2 = hightenbitsadd.spec()
    spec = spec1[0:16] + spec2[16:]

    return bit_stream_highdword(ctx.x, ctx.y, ctx.d, ctx.h, spec)


if __name__ == '__main__':
    main()
