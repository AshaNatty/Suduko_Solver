import streamlit as st

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return i, j
    return None

def solve_sudoku(board):
    empty = find_empty(board)
    if not empty:
        return True
    row, col = empty
    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0
    return False

def display_board(board):
    return "\n".join(" ".join(str(cell) if cell != 0 else "." for cell in row) for row in board)

st.title("🧩 Sudoku Solver")
st.write("Enter your Sudoku puzzle (0 for empty cells):")

default_puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

board = []

st.write("Enter each row below:")

for i in range(9):
    row_input = st.text_input(f"Row {i+1}", " ".join(str(num) for num in default_puzzle[i]))
    row = [int(num) if num.isdigit() else 0 for num in row_input.strip().split()]
    if len(row) != 9:
        st.error(f"Row {i+1} must have 9 numbers")
        st.stop()
    board.append(row)

if st.button("Solve Sudoku"):
    if solve_sudoku(board):
        st.success("Sudoku Solved!")
        st.text(display_board(board))
    else:
        st.error("No solution found!")
