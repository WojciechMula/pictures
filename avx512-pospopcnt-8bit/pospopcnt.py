def color(bit, opacity=100):
    lookup = {
        0: 'yellow',
        1: 'blue',
        2: 'red',
        3: 'brown',
        4: 'green',
        5: 'magenta',
        6: 'cyan',
        7: 'violet',
    }
    name = lookup[bit]
    return f'fill={name}!{opacity}'


inactive = 'fill=lightgray!25'
