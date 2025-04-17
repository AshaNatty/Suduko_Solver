import streamlit as st
import time
import copy
from collections import defaultdict

# Techniques
techniques = [
    "Backtracking",
    "Forward Checking",
    "AC-3",
    "MRV",
    "MRV + Degree",
    "MRV + Degree + LCV"
]

st.title("🧠 Sudoku CSP Solver")
st.markdown("You can modify the Sudoku puzzle below (use 0 for empty cells), and select a technique to solve it:")

# Default example Sudoku board
example_board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],

    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],

    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

# Input grid
board_input = []
for i in range(9):
    default_row = ",".join(str(num) for num in example_board[i])
    row = st.text_input(f"Row {i + 1} (comma separated)", value=default_row, key=f"row_{i}")
    try:
        row_values = [int(x.strip()) for x in row.split(',') if x.strip().isdigit() or x.strip() == '0']
        if len(row_values) == 9:
            board_input.append(row_values)
        else:
            board_input.append([0]*9)
    except:
        board_input.append([0]*9)

# CSP Class
class SudokuCSP:
    def __init__(self, board):
        self.board = board
        self.variables = [(i, j) for i in range(9) for j in range(9)]
        self.domains = {
            (i, j): [board[i][j]] if board[i][j] != 0 else list(range(1, 10))
            for i in range(9) for j in range(9)
        }
        self.neighbors = self.get_all_neighbors()

    def get_all_neighbors(self):
        neighbors = defaultdict(set)
        for row in range(9):
            for col in range(9):
                block_row, block_col = 3 * (row // 3), 3 * (col // 3)
                for i in range(9):
                    if i != col:
                        neighbors[(row, col)].add((row, i))
                    if i != row:
                        neighbors[(row, col)].add((i, col))
                for i in range(3):
                    for j in range(3):
                        r, c = block_row + i, block_col + j
                        if (r, c) != (row, col):
                            neighbors[(row, col)].add((r, c))
        return neighbors

# Heuristics and Inference
def select_var_default(csp):
    for var in csp.variables:
        if csp.board[var[0]][var[1]] == 0:
            return var
    return None

def select_mrv(csp):
    unassigned = [(var, len(csp.domains[var])) for var in csp.variables if csp.board[var[0]][var[1]] == 0]
    if not unassigned:
        return None
    min_domain = min(unassigned, key=lambda x: x[1])[1]
    mrv_vars = [var for var, size in unassigned if size == min_domain]
    return mrv_vars[0]

def select_mrv_degree(csp):
    unassigned = [(var, len(csp.domains[var])) for var in csp.variables if csp.board[var[0]][var[1]] == 0]
    if not unassigned:
        return None
    min_domain = min(unassigned, key=lambda x: x[1])[1]
    mrv_vars = [var for var, size in unassigned if size == min_domain]
    return max(mrv_vars, key=lambda var: len(csp.neighbors[var]))

def order_default(csp, var):
    return csp.domains[var]

def order_lcv(csp, var):
    def count_constraints(val):
        return sum(val in csp.domains[neighbor] for neighbor in csp.neighbors[var])
    return sorted(csp.domains[var], key=count_constraints)

def forward_checking(csp, var, value, assignment):
    removed = {}
    for neighbor in csp.neighbors[var]:
        if neighbor not in assignment and value in csp.domains[neighbor]:
            csp.domains[neighbor].remove(value)
            removed.setdefault(neighbor, []).append(value)
            if not csp.domains[neighbor]:
                return False, removed
    return True, removed

def ac3(csp):
    queue = [(xi, xj) for xi in csp.variables for xj in csp.neighbors[xi]]
    while queue:
        xi, xj = queue.pop(0)
        if revise(csp, xi, xj):
            if not csp.domains[xi]:
                return False
            for xk in csp.neighbors[xi] - {xj}:
                queue.append((xk, xi))
    return True

def revise(csp, xi, xj):
    revised = False
    for x in csp.domains[xi][:]:
        if all(x == y for y in csp.domains[xj]):
            csp.domains[xi].remove(x)
            revised = True
    return revised

def backtrack(assignment, csp, select_var, order_val, use_forward, use_ac3):
    if len(assignment) == sum(1 for row in csp.board for cell in row if cell != 0):
        return True

    var = select_var(csp)
    if var is None:
        return True

    for value in order_val(csp, var):
        if all(value != assignment.get(neigh) for neigh in csp.neighbors[var]):
            assignment[var] = value
            csp.board[var[0]][var[1]] = value
            original_domains = copy.deepcopy(csp.domains)
            removed = {}

            if use_forward:
                forward_ok, removed = forward_checking(csp, var, value, assignment)
                if not forward_ok:
                    assignment.pop(var)
                    csp.board[var[0]][var[1]] = 0
                    continue

            if use_ac3 and not ac3(csp):
                assignment.pop(var)
                csp.board[var[0]][var[1]] = 0
                continue

            result = backtrack(assignment, csp, select_var, order_val, use_forward, use_ac3)
            if result:
                return True

            for r in removed:
                csp.domains[r].extend(removed[r])
            csp.domains = original_domains
            csp.board[var[0]][var[1]] = 0
            assignment.pop(var)

    return False

def solve_sudoku(board, technique):
    board = copy.deepcopy(board)
    csp = SudokuCSP(board)

    if technique == "Backtracking":
        sel = select_var_default
        order = order_default
        fwd = False
        ac = False
    elif technique == "Forward Checking":
        sel = select_var_default
        order = order_default
        fwd = True
        ac = False
    elif technique == "AC-3":
        sel = select_var_default
        order = order_default
        fwd = False
        ac = True
    elif technique == "MRV":
        sel = select_mrv
        order = order_default
        fwd = False
        ac = False
    elif technique == "MRV + Degree":
        sel = select_mrv_degree
        order = order_default
        fwd = False
        ac = False
    elif technique == "MRV + Degree + LCV":
        sel = select_mrv_degree
        order = order_lcv
        fwd = True
        ac = True
    else:
        raise ValueError("Unknown technique")

    start = time.time()
    backtrack({}, csp, sel, order, fwd, ac)
    end = time.time()
    return csp.board, end - start

tech = st.selectbox("Select Technique", techniques)

if st.button("Solve Sudoku"):
    solution, t = solve_sudoku(board_input, tech)
    st.success(f"Solved using **{tech}** in {t:.5f} seconds.")
    st.write("### 🧩 Solved Board:")
    st.dataframe(solution)
