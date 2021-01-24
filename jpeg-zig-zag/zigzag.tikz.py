import sys
from tikz import *
from model import *

class DrawSSE:
    def __init__(self, file):
        self.cell_size = 1.1
        self.grid_size = self.cell_size * 8
        self.file = file
        self.x = 0
        self.y = 0
        self.model = Model()
        self.colors = {
            0: 'red',
            1: 'green',
            2: 'blue',
            3: 'yellow',
        }

        self.cells = []
        for y in range(8):
            self.cells.append([])
            for x in range(8):
                r = Rectangle(self.x + x * self.cell_size,
                              self.y + (7 - y) * self.cell_size,
                              self.cell_size,
                              self.cell_size)

                self.cells[-1].append(r)


    def draw(self):
        self.__color_grid()
        self.__draw_grid()
        self.__draw_array_indices()
        self.__draw_visit_order()
        self.__draw_visit_order_labels()


    def __color_grid(self):
        for item in self.model:
            register = item.target_index // 16

            r = self.cell(item.x, item.y)

            style = f'fill={self.colors[register]}!25'
            self.file.rectangle(r.top_left, r.bottom_right, style=style)


    def __draw_grid(self):
        self.file.rectangle(self.origin, self.origin + Point(self.grid_size, self.grid_size))
        for i in range(1, 8):
            self.file.hline(self.y + i * self.cell_size, self.x, self.x + self.grid_size)
            self.file.vline(self.x + i * self.cell_size, self.y, self.y + self.grid_size)


    def __draw_array_indices(self):
        for item in self.model:
            r = self.cell(item.x, item.y)
            self.file.label(r.bottom_right,
                            f'{{\\tiny {item.array_index}}}',
                            'anchor=south east')


    def __draw_visit_order(self):
        points = []
        for item in self.model:
            x = item.target_index % 8
            y = item.target_index // 8
            r = self.cell(x, y)
            points.append(r.center)

        self.file.polyline(points, style='thick')


    def __draw_visit_order_labels(self):
        for item in self.model:
            register = item.target_index // 16
            x = item.target_index % 8
            y = item.target_index // 8
            r = self.cell(x, y)

            r = self.cell(item.x, item.y)

            style = f'fill={self.colors[register]}!25'
            self.file.label(r.center, str(item.target_index), anchor=style)


    @property
    def origin(self):
        return Point(self.x, self.y)

    def cell(self, x, y):
        return self.cells[y][x]


if __name__ == '__main__':
    file = File()
    DrawSSE(file).draw()

    with open(sys.argv[1], 'wt') as f:
        file.save(f)
