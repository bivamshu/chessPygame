import copy
from piece import Pawn, Knight, Bishop, Rook, Queen, King

piece_values = {
    Pawn: 100,
    Knight: 320,
    Bishop: 330,
    Rook: 500,
    Queen: 900,
    King: 20000  # Arbitrary high value since losing king = game over
}

class IntelligentBot:
    def __init__(self, board, depth=2):
        self.board = board
        self.depth = depth
        self.color = None  # Bot's color (set when move is selected)

    def evaluate(self):
        """Basic evaluation function based on material balance."""
        score = 0
        for row in self.board.squares:
            for square in row:
                piece = square.piece
                if piece:
                    value = piece_values.get(type(piece), 0)
                    score += value if piece.color == self.color else -value
        return score

    def select_move(self, color):
        self.color = color
        best_score = float('-inf')
        best_move = None
        best_piece = None

        moves = self.board.get_all_valid_moves(color)
        for piece, move in moves:
            board_copy = copy.deepcopy(self.board)
            initial = move.initial
            piece_copy = board_copy.squares[initial.row][initial.col].piece

            board_copy.move(piece_copy, move, testing=True)

            score = self.minimax(board_copy, self.depth - 1, float('-inf'), float('inf'), False)

            if score > best_score:
                best_score = score
                best_move = move
                best_piece = piece

        return best_piece, best_move


    def minimax(self, board, depth, alpha, beta, maximizing):
        if depth == 0 or board.is_checkmate(self.color) or board.is_checkmate(self._opponent_color()):
            return self.evaluate()

        color = self.color if maximizing else self._opponent_color()
        moves = board.get_all_valid_moves(color)

        if not moves:
            return self.evaluate()

        if maximizing:
            max_eval = float('-inf')
            for piece, move in moves:
                board_copy = copy.deepcopy(board)
                initial = move.initial
                piece_copy = board_copy.squares[initial.row][initial.col].piece
                board_copy.move(piece_copy, move, testing=True)
                eval = self.minimax(board_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for piece, move in moves:
                board_copy = copy.deepcopy(board)
                initial = move.initial
                piece_copy = board_copy.squares[initial.row][initial.col].piece
                board_copy.move(piece_copy, move, testing=True)
                eval = self.minimax(board_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def _opponent_color(self):
        return 'white' if self.color == 'black' else 'black'
