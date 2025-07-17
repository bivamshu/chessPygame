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
        
        # Material and positional evaluation
        for row_idx, row in enumerate(self.board.squares):
            for col_idx, square in enumerate(row):
                piece = square.piece
                if piece:
                    material = piece_values.get(type(piece), 0)
                    positional = self.pst_bonus(piece, row_idx, col_idx)
                    total = material + positional
                    score += total if piece.color == self.color else -total
        
        # King safety evaluation
        king_safety_score = self.evaluate_king_safety()
        score += king_safety_score
        
        return score

    def evaluate_king_safety(self):
        """Evaluates king safety for both sides and returns the difference"""
        my_king_safety = self.king_safety_score(self.color)
        opponent_king_safety = self.king_safety_score(self._opponent_color())
        return my_king_safety - opponent_king_safety

    def king_safety_score(self, color):
        """Calculate king safety score for a given color"""
        king_pos = self.find_king(color)
        if not king_pos:
            return -10000  # King not found (shouldn't happen in normal game)
        
        safety_score = 0
        
        # Pawn shield evaluation
        safety_score += self.evaluate_pawn_shield(king_pos, color)
        
        # Open files near king penalty
        safety_score -= self.evaluate_open_files_near_king(king_pos, color)
        
        # Enemy piece attacks near king
        safety_score -= self.evaluate_attacks_near_king(king_pos, color)
        
        # King exposure penalty (distance from back rank)
        safety_score -= self.evaluate_king_exposure(king_pos, color)
        
        return safety_score

    def find_king(self, color):
        """Find the position of the king for given color"""
        for row_idx, row in enumerate(self.board.squares):
            for col_idx, square in enumerate(row):
                piece = square.piece
                if piece and isinstance(piece, King) and piece.color == color:
                    return (row_idx, col_idx)
        return None

    def evaluate_pawn_shield(self, king_pos, color):
        """Evaluate the pawn shield in front of the king"""
        king_row, king_col = king_pos
        shield_bonus = 0
        
        # Determine shield direction based on color
        shield_direction = -1 if color == 'white' else 1
        
        # Check the three files in front of the king
        for col_offset in [-1, 0, 1]:
            col = king_col + col_offset
            if 0 <= col < 8:
                # Check for pawn in front of king
                shield_row = king_row + shield_direction
                if 0 <= shield_row < 8:
                    piece = self.board.squares[shield_row][col].piece
                    if piece and isinstance(piece, Pawn) and piece.color == color:
                        shield_bonus += 30  # Bonus for pawn shield
                    else:
                        shield_bonus -= 20  # Penalty for missing pawn
                
                # Check for pawn two squares in front (for doubled protection)
                shield_row2 = king_row + 2 * shield_direction
                if 0 <= shield_row2 < 8:
                    piece = self.board.squares[shield_row2][col].piece
                    if piece and isinstance(piece, Pawn) and piece.color == color:
                        shield_bonus += 10  # Small bonus for advanced pawn shield
        
        return shield_bonus

    def evaluate_open_files_near_king(self, king_pos, color):
        """Penalize open files near the king"""
        king_row, king_col = king_pos
        open_file_penalty = 0
        
        # Check files around the king
        for col_offset in [-1, 0, 1]:
            col = king_col + col_offset
            if 0 <= col < 8:
                if self.is_file_open(col, color):
                    open_file_penalty += 25  # Penalty for open file near king
                elif self.is_file_semi_open(col, color):
                    open_file_penalty += 15  # Smaller penalty for semi-open file
        
        return open_file_penalty

    def is_file_open(self, col, color):
        """Check if a file has no pawns of the given color"""
        for row in range(8):
            piece = self.board.squares[row][col].piece
            if piece and isinstance(piece, Pawn) and piece.color == color:
                return False
        return True

    def is_file_semi_open(self, col, color):
        """Check if a file has no pawns of the given color but has enemy pawns"""
        has_own_pawn = False
        has_enemy_pawn = False
        
        for row in range(8):
            piece = self.board.squares[row][col].piece
            if piece and isinstance(piece, Pawn):
                if piece.color == color:
                    has_own_pawn = True
                else:
                    has_enemy_pawn = True
        
        return not has_own_pawn and has_enemy_pawn

    def evaluate_attacks_near_king(self, king_pos, color):
        """Count enemy pieces that can attack squares near the king"""
        king_row, king_col = king_pos
        attack_penalty = 0
        opponent_color = self._opponent_color()
        
        # Check all squares around the king
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                target_row = king_row + row_offset
                target_col = king_col + col_offset
                
                if 0 <= target_row < 8 and 0 <= target_col < 8:
                    # Count how many enemy pieces can attack this square
                    attackers = self.count_attackers(target_row, target_col, opponent_color)
                    attack_penalty += attackers * 10  # 10 points per attacking piece
        
        return attack_penalty

    def count_attackers(self, target_row, target_col, color):
        """Count how many pieces of given color can attack the target square"""
        attackers = 0
        
        for row_idx, row in enumerate(self.board.squares):
            for col_idx, square in enumerate(row):
                piece = square.piece
                if piece and piece.color == color:
                    if self.can_piece_attack(piece, row_idx, col_idx, target_row, target_col):
                        attackers += 1
        
        return attackers

    def can_piece_attack(self, piece, from_row, from_col, to_row, to_col):
        """Check if a piece can attack a target square (simplified check)"""
        if isinstance(piece, Pawn):
            direction = -1 if piece.color == 'white' else 1
            if from_row + direction == to_row and abs(from_col - to_col) == 1:
                return True
        
        elif isinstance(piece, Knight):
            row_diff = abs(from_row - to_row)
            col_diff = abs(from_col - to_col)
            if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
                return True
        
        elif isinstance(piece, Bishop):
            if abs(from_row - to_row) == abs(from_col - to_col):
                return self.is_diagonal_clear(from_row, from_col, to_row, to_col)
        
        elif isinstance(piece, Rook):
            if from_row == to_row or from_col == to_col:
                return self.is_path_clear(from_row, from_col, to_row, to_col)
        
        elif isinstance(piece, Queen):
            if (from_row == to_row or from_col == to_col or 
                abs(from_row - to_row) == abs(from_col - to_col)):
                return self.is_path_clear(from_row, from_col, to_row, to_col)
        
        elif isinstance(piece, King):
            if abs(from_row - to_row) <= 1 and abs(from_col - to_col) <= 1:
                return True
        
        return False

    def is_path_clear(self, from_row, from_col, to_row, to_col):
        """Check if path is clear for rook/queen movement"""
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        current_row, current_col = from_row + row_step, from_col + col_step
        
        while current_row != to_row or current_col != to_col:
            if self.board.squares[current_row][current_col].piece:
                return False
            current_row += row_step
            current_col += col_step
        
        return True

    def is_diagonal_clear(self, from_row, from_col, to_row, to_col):
        """Check if diagonal path is clear for bishop movement"""
        return self.is_path_clear(from_row, from_col, to_row, to_col)

    def evaluate_king_exposure(self, king_pos, color):
        """Penalize king being too far from back rank"""
        king_row, king_col = king_pos
        back_rank = 0 if color == 'white' else 7
        
        # Penalty increases with distance from back rank
        distance_penalty = abs(king_row - back_rank) * 15
        
        return distance_penalty

    def select_move(self, color, return_eval=False):
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

        if return_eval:
            return best_piece, best_move, best_score
        else:
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