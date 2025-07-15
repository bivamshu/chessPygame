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

pawn_pst = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [ 5,  5, 10, 25, 25, 10,  5,  5],
    [ 0,  0,  0, 20, 20,  0,  0,  0],
    [ 5, -5,-10,  0,  0,-10, -5,  5],
    [ 5, 10, 10,-20,-20, 10, 10,  5],
    [ 0,  0,  0,  0,  0,  0,  0,  0]
    ]   

knight_pst = [
        [-50, -40, -30, -30, -30, -30, -40, -50],
        [-40, -20,   0,   0,   0,   0, -20, -40],
        [-30,   0,  10,  15,  15,  10,   0, -30],
        [-30,   5,  15,  20,  20,  15,   5, -30],
        [-30,   0,  15,  20,  20,  15,   0, -30],
        [-30,   5,  10,  15,  15,  10,   5, -30],
        [-40, -20,   0,   5,   5,   0, -20, -40],
        [-50, -40, -30, -30, -30, -30, -40, -50]
    ]

bishop_pst = [
        [-20, -10, -10, -10, -10, -10, -10, -20],
        [-10,   5,   0,   0,   0,   0,   5, -10],
        [-10,  10,  10,  10,  10,  10,  10, -10],
        [-10,   0,  10,  10,  10,  10,   0, -10],
        [-10,   5,   5,  10,  10,   5,   5, -10],
        [-10,   0,   5,  10,  10,   5,   0, -10],
        [-10,   0,   0,   0,   0,   0,   0, -10],
        [-20, -10, -10, -10, -10, -10, -10, -20]
    ]

rook_pst = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [5, 10, 10, 10, 10, 10, 10,  5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [-5, 0, 0, 0, 0, 0, 0, -5],
        [0,  0,  0,  5,  5,  0,  0,  0]
    ]

queen_pst = [
        [-20, -10, -10, -5, -5, -10, -10, -20],
        [-10,   0,   0,  0,  0,   0,   0, -10],
        [-10,   0,   5,  5,  5,  5,   0, -10],
        [ -5,   0,  5,  5,  5,  5,   0,  -5],
        [  0,   0,  5,  5,  5,  5,   0,  -5],
        [-10,  5,  5,  5,  5,  5,   0, -10],
        [-10,  0,  5,  0,  0,  0,   0, -10],
        [-20, -10, -10, -5, -5, -10, -10, -20]
    ]

king_pst = [
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-30, -40, -40, -50, -50, -40, -40, -30],
        [-20, -30, -30, -40, -40, -30, -30, -20],
        [-10, -20, -20, -20, -20, -20, -20, -10],
        [ 20,  20,   0,   0,   0,   0,  20,  20],
        [ 20,  30,  10,   0,   0,  10,  30,  20]
    ]

class IntelligentBot:
    def __init__(self, board, depth=2):
        self.board = board
        self.depth = depth
        self.color = None  # Bot's color (set when move is selected)

    def evaluate(self):
        score = 0
        for row_idx, row in enumerate(self.board.squares):
            for col_idx, square in enumerate(row):
                piece = square.piece
                if piece:
                    material = piece_values.get(type(piece), 0)
                    positional = self.pst_bonus(piece, row_idx, col_idx)
                    total = material + positional
                    score += total if piece.color == self.color else -total
        return score

    def select_move(self, color):
        self.color = color
        best_score = float('-inf')
        best_move = None
        best_piece = None

        moves = self.board.get_all_valid_moves(color)
        moves.sort(key=lambda m: self.score_move(*m), reverse=True)

        for piece, move in moves:
            self.board.make_move(piece, move)
            self.board.next_turn()

            score = self.minimax(self.depth - 1, float('-inf'), float('inf'), False)

            self.board.prev_turn()
            self.board.unmake_move()

            if score > best_score:
                best_score = score
                best_move = move
                best_piece = piece

        return best_piece, best_move


    def minimax(self, depth, alpha, beta, maximizing):
        if depth == 0 or self.board.is_checkmate(self.color) or self.board.is_checkmate(self._opponent_color()):
            return self.evaluate()

        color = self.color if maximizing else self._opponent_color()
        moves = self.board.get_all_valid_moves(color)
        moves.sort(key=lambda m: self.score_move(*m), reverse=True)


        if not moves:
            return self.evaluate()

        if maximizing:
            max_eval = float('-inf')
            for piece, move in moves:
                self.board.make_move(piece, move)
                self.board.next_turn()

                eval = self.minimax(depth - 1, alpha, beta, False)

                self.board.prev_turn()
                self.board.unmake_move()

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for piece, move in moves:
                self.board.make_move(piece, move)
                self.board.next_turn()

                eval = self.minimax(depth - 1, alpha, beta, True)

                self.board.prev_turn()
                self.board.unmake_move()

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def pst_bonus(self, piece, row, col):
        if isinstance(piece, Pawn):
            table = pawn_pst
        elif isinstance(piece, Knight):
            table = knight_pst
        elif isinstance(piece, Bishop):
            table = bishop_pst
        elif isinstance(piece, Rook):
            table = rook_pst
        elif isinstance(piece, Queen):
            table = queen_pst
        elif isinstance(piece, King):
            table = king_pst
        else:
            return 0

        # Flip for black pieces (mirror vertically)
        return table[row][col] if piece.color == 'white' else table[7 - row][col]


    def _opponent_color(self):
        return 'white' if self.color == 'black' else 'black'

    def score_move(self, piece, move):
        """Assigns a score to the move based on MVV-LVA (Most Valuable Victim - Least Valuable Attacker)."""
        if move.final.piece:
            victim_value = piece_values.get(type(move.final.piece), 0)
            attacker_value = piece_values.get(type(piece), 1)
            return 10_000 + victim_value - attacker_value  # High priority for better captures
        return 0  # Quiet move
