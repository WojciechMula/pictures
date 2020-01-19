def bfs(x):
    n = 0
    assert(x > 0)
    while x != 1:
        x >>= 1
        n += 1

    return n


def popcnt(x):
    n = 0
    while x > 0:
        n += x & 0x01
        x >>= 1

    return n


def parity(x):
    return popcnt(x) & 0x01

