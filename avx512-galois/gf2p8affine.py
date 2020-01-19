class Algorithm:
    def __init__(self, index, order, input):
        assert 0 <= index < 8
        assert len(order) == 8
        assert all(0 <= i < 8 for i in order)
        assert len(input) == 8
        assert all(0 <= x <= 255 for x in input)

        self.order = order
        self.lane0 = [1 << i for i in reversed(self.order)]
        self.lane1 = input
        self.lane0reversed = list(reversed(self.lane0))
        self.results = [None] * 8
        self.index = index

    @property
    def result(self):
        return self.results[self.index]

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, value):
        self.__index = value
        self.lane1populated = [self.lane1[self.index]] * 8
        self.lanes_anded = [a & b for a, b in zip(self.lane0reversed, self.lane1populated)]
        self.results[self.index] = sum(parity(x) << i for i, x in enumerate(self.lanes_anded))


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

