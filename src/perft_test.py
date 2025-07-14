from board import Board
from move import Move
from square import Square
import time

def perft(board, depth):
    if depth == 0:
        return 1

    total_nodes = 0
    color = board.next_player
    all_moves = board.get_all_valid_moves(color)

    for piece, move in all_moves:
        board.make_move(piece, move)
        board.next_turn()
        total_nodes += perft(board, depth - 1)
        board.unmake_move()
        board.prev_turn()  # We'll define this

    return total_nodes

if __name__ == '__main__':
    board = Board()
    for depth in range(1, 6):
        start = time.time()
        nodes = perft(board, depth)
        end = time.time()
        print(f"Perft depth {depth}: {nodes} (Time: {end - start:.2f}s)")

