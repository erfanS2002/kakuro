from time import time

MIN_CELL_VALUE = 1
MAX_CELL_VALUE = 9


def monitor(func):
    def wrap_func(*args, **kwargs):
        t1 = time()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print(f'Function {func.__name__!r} executed in {(time() - t1):.16f}s')
            print(f'Error: {e}')
            return
        print(f'Function {func.__name__!r} executed in {(time() - t1):.16f}s')
        return result

    return wrap_func


class SudokuGame:
    pass


def initialize_game_state(game):
    value_of_cell = [[0] * 9 for _ in range(9)]
    constraint_on_cell = [[[(0, 0), (0, 0)] for _ in range(9)] for _ in range(9)]
    order_domain_values = [[[i for i in range(MIN_CELL_VALUE, MAX_CELL_VALUE + 1)] for _ in range(9)] for _ in range(9)]

    for cell in game.data_totals:
        i, j, value, direction = cell
        update_cell_value(value_of_cell, i, j, value, direction)

    for cell in game.data_fills:
        x, y = cell[0], cell[1]
        xi, yi = get_left_consist(x, y, value_of_cell)
        xj, yj = get_up_consist(x, y, value_of_cell)
        constraint_on_cell[x][y] = [(xi, yi), (xj, yj)]

    return value_of_cell, constraint_on_cell, order_domain_values


def update_cell_value(value_of_cell, i, j, value, direction):
    if direction == 'v':
        value_of_cell[i][j] = (value_of_cell[i][j][0], value)
    else:
        value_of_cell[i][j] = (value, value_of_cell[i][j][1])


def back_track(current_cell_index, game, value_of_cell, order_domain_values):
    if current_cell_index == -1:
        if game.check_win(value_of_cell):
            print('ACCEPTED')
            return True
        else:
            return False

    current_cell = game.data_fills[current_cell_index]
    domain = order_domain_values[current_cell[0]][current_cell[1]].copy()

    for i in domain:
        value_of_cell[current_cell[0]][current_cell[1]] = i
        if update_filled_sum_value(current_cell[0], current_cell[1], value_of_cell):
            game.data_filled.append([current_cell[0], current_cell[1], i])
            update_order_domain_values(current_cell[0], current_cell[1], i, True, order_domain_values, value_of_cell)
            if back_track(get_next_unassigned_variable(game, value_of_cell), game, value_of_cell, order_domain_values):
                return True
            game.data_filled.pop()
            update_order_domain_values(current_cell[0], current_cell[1], i, False, order_domain_values, value_of_cell)
        value_of_cell[current_cell[0]][current_cell[1]] = 0

    return False


def update_filled_sum_value(i, j, value_of_cell):
    xi, yi = get_left_consist(i, j, value_of_cell)
    xj, yj = get_up_consist(i, j, value_of_cell)
    sum_min_row, sum_max_row = row_sum(xi, yi, value_of_cell)
    sum_min_column, sum_max_column = column_sum(xj, yj, value_of_cell)

    return sum_max_row >= value_of_cell[xi][yi][0] >= sum_min_row and \
           sum_max_column >= value_of_cell[xj][yj][1] >= sum_min_column


def update_order_domain_values(i, j, value, remove, order_domain_values, value_of_cell):
    xi, yi = get_left_consist(i, j, value_of_cell)
    xj, yj = get_up_consist(i, j, value_of_cell)

    if remove:
        update_domain_values_range(xi, yi, value, order_domain_values, value_of_cell)
        update_domain_values_range(xj, yj, value, order_domain_values, value_of_cell, is_row=False)
    else:
        update_domain_values_range(xi, yi, value, order_domain_values, value_of_cell, add=True)
        update_domain_values_range(xj, yj, value, order_domain_values, value_of_cell, add=True)


def update_domain_values_range(i, j, value, order_domain_values, value_of_cell, add=False, is_row=True):
    inc = 1 if is_row else 0
    while 0 <= i < 9 and not isinstance(value_of_cell[i][j], tuple):
        if add and value not in order_domain_values[i][j]:
            order_domain_values[i][j].append(value)
        elif not add:
            try:
                order_domain_values[i][j].remove(value)
            except ValueError:
                pass
        i += inc


def column_sum(i, j, value_of_cell):
    summ = 0
    cnt = 0
    while True:
        i += 1
        if i > 8 or isinstance(value_of_cell[i][j], tuple):
            break
        summ += value_of_cell[i][j]
        cnt += (value_of_cell[i][j] == 0)

    minn = ((cnt + 1) * cnt) / 2
    maxx = 45 - ((9 - cnt) * (9 - cnt + 1) / 2)

    return summ + minn, maxx + summ


def row_sum(i, j, value_of_cell):
    summ = 0
    cnt = 0
    while True:
        j += 1
        if j > 8 or isinstance(value_of_cell[i][j], tuple):
            break
        summ += value_of_cell[i][j]
        cnt += (value_of_cell[i][j] == 0)

    minn = ((cnt + 1) * cnt) / 2
    maxx = 45 - ((9 - cnt) * (9 - cnt + 1) / 2)
    return summ + minn, maxx + summ


def get_left_consist(i, j, value_of_cell):
    while True:
        j -= 1
        if isinstance(value_of_cell[i][j], tuple):
            return i, j


def get_up_consist(i, j, value_of_cell):
    while True:
        i -= 1
        if isinstance(value_of_cell[i][j], tuple):
            return i, j


def print_board(value_of_cell):
    for i in range(9):
        for j in range(9):
            print(value_of_cell[i][j], end='\t')
        print()
    print(" ***************** ")


def get_next_unassigned_variable(game, value_of_cell, order_domain_values):
    constraint = float('inf')
    index = -1

    for i, pos in enumerate(game.data_fills):
        if value_of_cell[pos[0]][pos[1]] == 0:
            current_constraint = len(order_domain_values[pos[0]][pos[1]])
            if current_constraint < constraint:
                constraint = current_constraint
                index = i

    return index
