# model of flags word

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '%0.3f,%0.3f' % (self.x, self.y)

    def __repr__(self):
        return '<Point %s>' % self


class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.w = width
        self.h = height

    @property
    def top(self):
        return Point(self.x + self.w/2, self.y + self.h)

    @property
    def bottom(self):
        return Point(self.x + self.w/2, self.y)

    @property
    def left(self):
        return Point(self.x, self.y + self.h/2)

    @property
    def right(self):
        return Point(self.x + self.w, self.y + self.h/2)
    
    @property
    def lt(self):
        return Point(self.x, self.y + self.h)

class LabelledRectangle(Rectangle):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.style = ''
        self.label = None

    def draw(self, file):
        file.writeln(r'\draw [%s] (%0.2f, %0.2f) rectangle (%0.2f, %0.2f);' %
                    (self.style, self.x, self.y, self.x + self.w, self.y + self.h))

        if self.label:
            file.writeln(r'\node at (%0.2f, %0.2f) {%s};' % (self.x + self.w/2, self.y + self.h/2, self.label))


class BIT(LabelledRectangle):
    def __init__(self, x, y, w, h, label, style, index):
        super().__init__(x, y, w, h)
        self.label = label
        self.style = style
        self.index = index


    def draw_index(self, file):
        file.writeln(r'\node[below] at (%0.2f, %0.2f) {%s};' %
                     (self.bottom.x, self.bottom.y, f"\\tiny{self.index}"))


class BYTE(Rectangle):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.style = ''
        self.__value = None

        self.bit = []
        w = width/8
        for i in range(8):
            self.bit.append(BIT(x + (7-i) * w, y, w, height, '', '', i))

    @property
    def value(self):
        return self.__value


    @value.setter
    def value(self, value):
        assert value >= 0 and value <= 0xff
        self.__value = value
        for i in range(8):
            v = value & (1 << i)
            if v:
                self.bit[i].label = '1'
            else:
                self.bit[i].label = '0'


    def draw(self, file):
        for bit in self.bit:
            bit.draw(file)


class QWORD(Rectangle):
    def __init__(self, x, y, width, height, byte_cls=BYTE):
        super().__init__(x, y, width, height)
        self.style = ''

        self.byte = []
        w = width/8
        for i in range(8):
            self.byte.append(byte_cls(x + (7-i) * w, y, w, height))


    def draw(self, file):
        for byte in self.byte:
            byte.draw(file)


class WHOLE_BYTE(LabelledRectangle):
    pass   


# drawing utilities

def escape(s):
    return s.replace('_', r'\_')


def texttt(s):
    return r'\texttt{%s}' % s


def bold(s):
    return r'\textbf{%s}' % s


def draw_label(file, point, label, anchor):
    file.writeln(r'\node[%s] at (%0.2f, %0.2f) {%s};' % (anchor, point.x, point.y, label))


def draw_description(file, x0, y0, x1, y1, label, anchor):
    file.writeln(r'\draw (%0.2f, %0.2f) -- (%0.2f, %0.2f) -- (%0.2f, %0.2f);' %
        (x0, y0, x0, y1, x1, y1)
    )

    file.writeln(r'\node[%s] at (%0.2f, %0.2f) {%s};' % (anchor, x1, y1, label))


def draw_horiz_brace(file, x0, x1, y, label, orientation='above'):
    if orientation == 'above':
        yshift = 5
    elif orientation == 'below':
        yshift = -5
    else:
        assert False, 'wrong value of "orientation"'

    file.writeln(r"\draw [decorate,decoration={brace,amplitude=5pt}] "
                 r"(%0.2f, %0.2f) -- (%0.2f, %0.2f) node [midway,%s,yshift=%dpt] {%s};" %
                 (x0, y, x1, y, orientation, yshift, label))


class File:
    def __init__(self, file):
        self.file = file

    def writeln(self, s):
        self.file.write(s)
        self.file.write('\n')
