from time import time

class SudokuSolver:
    def __init__(self, game):
        self.Game = game
        self.value_of_cell = []
        self.constraint_on_cell = []
        self.order_domain_values = []

    def monitor(func):
        def wrap_func(*args, **kwargs):
            t1 = time()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                print(f'Error in {func.__name__!r}: {e}')
                return
            print(f'{func.__name__!r} executed in {(time() - t1):.16f}s')
            return result
        return wrap_func

    @monitor
    def simple_solve(self):
        self.initialize_data_structures()
        self.fill_initial_values()
        self.backtrack(0)
        return self.Game.data_filled

    def initialize_data_structures(self):
        for _ in range(9):
            row = []
            constraint = []
            values = []
            for _ in range(9):
                row.append((0, 0))
                constraint.append([(-1, -1), (-1, -1)])
                values.append([1, 2, 3, 4, 5, 6, 7, 8, 9])
            self.constraint_on_cell.append(constraint)
            self.value_of_cell.append(row)
            self.order_domain_values.append(values)

    def fill_initial_values(self):
        for cell in self.Game.data_totals:
            i, j, value, direction = cell
            self.value_of_cell[i][j] = (self.value_of_cell[i][j][0], value) if direction == 'v' else (value, self.value_of_cell[i][j][1])

        for cell in self.Game.data_fills:
            x, y = cell[0], cell[1]
            xi, yi = self.get_left_consistent(x, y)
            xj, yj = self.get_up_consistent(x, y)
            self.constraint_on_cell[x][y] = [(xi, yi), (xj, yj)]

    def get_left_consistent(self, i, j):
        while True:
            j -= 1
            if isinstance(self.value_of_cell[i][j], tuple):
                return i, j

    def get_up_consistent(self, i, j):
        while True:
            i -= 1
            if isinstance(self.value_of_cell[i][j], tuple):
                return i, j

    def column_sum(self, i, j):
        summ = 0
        cnt = 0
        while True:
            i += 1
            if i > 8 or isinstance(self.value_of_cell[i][j], tuple):
                break
            summ += self.value_of_cell[i][j]
            cnt += (self.value_of_cell[i][j] == 0)

        min_sum = ((cnt + 1) * cnt / 2)
        max_sum = 45 - ((9 - cnt) * (9 - cnt + 1) / 2)

        return summ + min_sum, max_sum + summ

    def row_sum(self, i, j):
        summ = 0
        cnt = 0
        while True:
            j += 1
            if j > 8 or isinstance(self.value_of_cell[i][j], tuple):
                break
            summ += self.value_of_cell[i][j]
            cnt += (self.value_of_cell[i][j] == 0)

        min_sum = ((cnt + 1) * cnt / 2)
        max_sum = 45 - ((9 - cnt) * (9 - cnt + 1) / 2)
        return summ + min_sum, max_sum + summ

    def get_filled_sum_value(self, i, j):
        xi, yi = self.constraint_on_cell[i][j][0]
        xj, yj = self.constraint_on_cell[i][j][1]
        sum_min_row, sum_max_row = self.row_sum(xi, yi)
        sum_min_column, sum_max_column = self.column_sum(xj, yj)
        return sum_max_row >= self.value_of_cell[xi][yi][0] >= sum_min_row and \
               sum_max_column >= self.value_of_cell[xj][yj][1] >= sum_min_column

    def update_order_domain_values(self, i, j, value, remove):
        xi, yi = self.constraint_on_cell[i][j][0]
        xj, yj = self.constraint_on_cell[i][j][1]
        if remove:
            self.remove_values_from_order_domain(xi, yi, value)
            self.remove_values_from_order_domain(xj, yj, value)
        else:
            self.add_value_to_order_domain(xi, yi, value)
            self.add_value_to_order_domain(xj, yj, value)

    def remove_values_from_order_domain(self, i, j, value):
        while i < 9 and not isinstance(self.value_of_cell[i][j], tuple):
            try:
                self.order_domain_values[i][j].remove(value)
            except ValueError:
                pass
            i += 1

    def add_value_to_order_domain(self, i, j, value):
        while i < 9 and not isinstance(self.value_of_cell[i][j], tuple):
            if value not in self.order_domain_values[i][j]:
                self.order_domain_values[i][j].append(value)
            i += 1

    def backtrack(self, current_cell_index):
        if current_cell_index == len(self.Game.data_fills):
            if self.Game.check_win():
                print(' ACCEPTED ')
                return True
            else:
                return False

        current_cell = self.Game.data_fills[current_cell_index]
        domain = self.order_domain_values[current_cell[0]][current_cell[1]].copy()
        for i in domain:
            self.value_of_cell[current_cell[0]][current_cell[1]] = i
            if self.get_filled_sum_value(current_cell[0], current_cell[1]):
                self.Game.data_filled.append([current_cell[0], current_cell[1], i])
                self.update_order_domain_values(current_cell[0], current_cell[1], i, True)
                if self.backtrack(current_cell_index + 1):
                    return True
                self.Game.data_filled.pop()
                self.update_order_domain_values(current_cell[0], current_cell[1], i, False)
            self.value_of_cell[current_cell[0]][current_cell[1]] = 0
        return False

    def print_board(self):
        for i in range(9):
            for j in range(9):
                print(self.value_of_cell[i][j], end='\t')
            print()
