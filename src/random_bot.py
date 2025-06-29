import random
from move import Move

class RandomBot:
    def __init__(self, board):
        self.board = board 

    def select_move(self, color):
        valid_moves = self.board.get_all_valid_moves(color)
        if not valid_moves:
            return None, None
        return random.choice(valid_moves)