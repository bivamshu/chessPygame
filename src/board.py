from const import *
from square import Square
from piece import *
from move import Move
from sound import Sound
import copy
import os

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')
        self.next_player = 'white'
        self.move_history = []
        self.halfmove_clock = 0


    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final
        en_passant_empty = self.squares[final.row][final.col].isempty()
        captured_piece = self.squares[final.row][final.col].piece

        # Update halfmove clock
        if isinstance(piece, Pawn) or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if isinstance(piece, Pawn):
            diff = final.col - initial.col
            if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(os.path.join('assets/sounds/capture.wav'))
                    sound.play()
            else:
                self.check_promotion(piece, final)

        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                if rook and rook.moves:
                    self.move(rook, rook.moves[-1])

        piece.moved = True
        piece.clear_moves()
        self.last_move = move
        self.last_piece = piece


    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self, piece):
        if not isinstance(piece, Pawn): return
        for row in range(ROWS):
            for col in range(COLS):
                p = self.squares[row][col].piece
                if isinstance(p, Pawn): p.en_passant = False
        piece.en_passant = True

    def in_check(self, color):
        king_pos = None
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.squares[row][col].piece
                if piece and isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos: break
        if not king_pos: return False

        king_row, king_col = king_pos
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.squares[row][col].piece
                if piece and piece.color != color:
                    self.calc_moves(piece, row, col, bool=False)
                    for move in piece.moves:
                        if move.final.row == king_row and move.final.col == king_col:
                            return True
        return False

    def causes_check(self, piece, move):
        self.make_move(piece, move)
        self.next_turn()
        is_in_check = self.in_check(piece.color)
        self.prev_turn()
        self.unmake_move()
        return is_in_check


    def is_checkmate(self, color):
        if not self.in_check(color): return False
        return len(self.get_all_valid_moves(color)) == 0

    def get_all_valid_moves(self, color):
        all_moves = []
        for row in range(ROWS):
            for col in range(COLS):
                square = self.squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    if piece.color == color:
                        self.calc_moves(piece, row, col)
                        for move in piece.moves:
                            all_moves.append((piece, move))
        return all_moves

    def calc_moves(self, piece, row, col, bool=True):
        def pawn_moves():
            steps = 1 if piece.moved else 2
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for r in range(start, end, piece.dir):
                if Square.in_range(r) and self.squares[r][col].isempty():
                    move = Move(Square(row, col), Square(r, col))
                    if not bool or not self.causes_check(piece, move):
                        piece.add_move(move)
                else:
                    break
            for dc in [-1, 1]:
                r, c = row + piece.dir, col + dc
                if Square.in_range(r, c):
                    if self.squares[r][c].has_enemy_piece(piece.color):
                        move = Move(Square(row, col), Square(r, c, self.squares[r][c].piece))
                        if not bool or not self.causes_check(piece, move):
                            piece.add_move(move)
            if row == (3 if piece.color == 'white' else 4):
                fr = 2 if piece.color == 'white' else 5
                for dc in [-1, 1]:
                    if Square.in_range(col + dc):
                        target = self.squares[row][col + dc].piece
                        if isinstance(target, Pawn) and target.color != piece.color and target.en_passant:
                            move = Move(Square(row, col), Square(fr, col + dc, target))
                            if not bool or not self.causes_check(piece, move):
                                piece.add_move(move)

        def knight_moves():
            for dr, dc in [(-2,1), (-1,2), (1,2), (2,1), (2,-1), (1,-2), (-1,-2), (-2,-1)]:
                r, c = row + dr, col + dc
                if Square.in_range(r, c) and self.squares[r][c].isempty_or_enemy(piece.color):
                    move = Move(Square(row, col), Square(r, c, self.squares[r][c].piece))
                    if not bool or not self.causes_check(piece, move):
                        piece.add_move(move)

        def straightline_moves(directions):
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while Square.in_range(r, c):
                    dest = self.squares[r][c]
                    move = Move(Square(row, col), Square(r, c, dest.piece))
                    if dest.isempty():
                        if not bool or not self.causes_check(piece, move):
                            piece.add_move(move)
                    elif dest.has_enemy_piece(piece.color):
                        if not bool or not self.causes_check(piece, move):
                            piece.add_move(move)
                        break
                    else:
                        break
                    r += dr
                    c += dc

        def king_moves():
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
                    r, c = row + dr, col + dc
                    if Square.in_range(r, c) and self.squares[r][c].isempty_or_enemy(piece.color):
                        move = Move(Square(row, col), Square(r, c, self.squares[r][c].piece))
                        if not bool or not self.causes_check(piece, move):
                            piece.add_move(move)
            if not piece.moved:
                for side, rook_col, path_cols, king_final_col, rook_final_col in [
                    ('left', 0, [1,2,3], 2, 3),
                    ('right', 7, [5,6], 6, 5)
                ]:
                    rook = self.squares[row][rook_col].piece
                    if isinstance(rook, Rook) and not rook.moved:
                        if all(self.squares[row][c].isempty() for c in path_cols):
                            moveK = Move(Square(row, col), Square(row, king_final_col))
                            moveR = Move(Square(row, rook_col), Square(row, rook_final_col))
                            if not bool or not self.causes_check(piece, moveK):
                                piece.add_move(moveK)
                                rook.add_move(moveR)

        piece.clear_moves()
        if isinstance(piece, Pawn): pawn_moves()
        elif isinstance(piece, Knight): knight_moves()
        elif isinstance(piece, Bishop): straightline_moves([(-1,-1), (-1,1), (1,-1), (1,1)])
        elif isinstance(piece, Rook): straightline_moves([(-1,0), (1,0), (0,-1), (0,1)])
        elif isinstance(piece, Queen): straightline_moves([(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0), (0,-1), (0,1)])
        elif isinstance(piece, King): king_moves()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))
        placements = [
            (Rook, 0), (Knight, 1), (Bishop, 2), (Queen, 3), (King, 4),
            (Bishop, 5), (Knight, 6), (Rook, 7)
        ]
        for cls, col in placements:
            self.squares[row_other][col] = Square(row_other, col, cls(color))

    def count_moves(self):
        count = 0
        for row in self.squares:
            for square in row:
                piece = square.piece
                if piece:
                    count += len(getattr(piece, 'moves', []))
        return count
    
    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def prev_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'


    def fen(self):
        piece_to_fen = {
            Pawn: 'p',
            Knight: 'n',
            Bishop: 'b',
            Rook: 'r',
            Queen: 'q',
            King: 'k',
        }

        fen_rows = []
        for row in self.squares:
            empty = 0
            fen_row = ''
            for square in row:
                piece = square.piece
                if piece is None:
                    empty += 1
                else:
                    if empty > 0:
                        fen_row += str(empty)
                        empty = 0
                    symbol = piece_to_fen.get(type(piece), '?')
                    fen_row += symbol.upper() if piece.color == 'white' else symbol
            if empty > 0:
                fen_row += str(empty)
            fen_rows.append(fen_row)

        board_part = '/'.join(fen_rows)

        # Active color (assumes white moves first; toggle based on self.last_move)
        active_color = 'w' if not self.last_piece or self.last_piece.color == 'black' else 'b'

        # Castling rights
        castling_rights = ''
        for row in [0, 7]:
            king = self.squares[row][4].piece
            if isinstance(king, King) and not king.moved:
                if isinstance(self.squares[row][7].piece, Rook) and not self.squares[row][7].piece.moved:
                    castling_rights += 'K' if row == 7 else 'k'
                if isinstance(self.squares[row][0].piece, Rook) and not self.squares[row][0].piece.moved:
                    castling_rights += 'Q' if row == 7 else 'q'
        if not castling_rights:
            castling_rights = '-'

        # En passant target square
        en_passant = '-'
        if isinstance(self.last_piece, Pawn):
            diff = abs(self.last_move.initial.row - self.last_move.final.row)
            if diff == 2:
                col = self.last_move.initial.col
                mid_row = (self.last_move.initial.row + self.last_move.final.row) // 2
                en_passant = f"{chr(col + ord('a'))}{8 - mid_row}"

        # Halfmove clock (simplified to 0 always)
        halfmove_clock = '0'

        # Fullmove number (count of full turns)
        fullmove_number = '1' if not self.last_move else str((self.count_moves() // 2) + 1)

        return f"{board_part} {active_color} {castling_rights} {en_passant} {halfmove_clock} {fullmove_number}"

    def make_move(self, piece, move):
        initial = move.initial
        final = move.final
        captured = self.squares[final.row][final.col].piece
        promotion = False
        en_passant_capture = None
        rook_move = None

        # Handle en passant capture
        if isinstance(piece, Pawn):
            if initial.col != final.col and captured is None:
                en_passant_row = final.row + (1 if piece.color == 'white' else -1)
                en_passant_capture = self.squares[en_passant_row][final.col].piece
                self.squares[en_passant_row][final.col].piece = None

        # Handle castling rook move
        if isinstance(piece, King) and abs(initial.col - final.col) == 2:
            row = initial.row
            if final.col == 6:  # King-side
                rook = self.squares[row][7].piece
                self.squares[row][7].piece = None
                self.squares[row][5].piece = rook
                rook_move = (rook, Square(row, 7), Square(row, 5))
            else:  # Queen-side
                rook = self.squares[row][0].piece
                self.squares[row][0].piece = None
                self.squares[row][3].piece = rook
                rook_move = (rook, Square(row, 0), Square(row, 3))

        # Save en passant state
        en_passant_prev = piece.en_passant if isinstance(piece, Pawn) else None

        # Move piece
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # Handle promotion
        if isinstance(piece, Pawn) and (final.row == 0 or final.row == 7):
            piece = Queen(piece.color)
            self.squares[final.row][final.col].piece = piece
            promotion = True

        # Save to history
        self.move_history.append((piece, move, captured, piece.moved, promotion, en_passant_capture, en_passant_prev, rook_move))
        piece.moved = True


    def unmake_move(self):
        if not self.move_history:
            return

        piece, move, captured, piece_moved, promotion, en_passant_capture, en_passant_prev, rook_move = self.move_history.pop()
        initial = move.initial
        final = move.final

        # Undo promotion
        if promotion:
            piece = Pawn(piece.color)

        # Put piece back
        self.squares[initial.row][initial.col].piece = piece
        self.squares[final.row][final.col].piece = captured

        # Restore en passant capture
        if en_passant_capture:
            row = final.row + (1 if piece.color == 'white' else -1)
            self.squares[row][final.col].piece = en_passant_capture

        # Restore en passant flag
        if isinstance(piece, Pawn):
            piece.en_passant = en_passant_prev

        # Undo castling rook move
        if rook_move:
            rook, start, end = rook_move
            self.squares[start.row][start.col].piece = rook
            self.squares[end.row][end.col].piece = None

        piece.moved = piece_moved

    def load_fen(self, fen):
        piece_map = {
            'p': Pawn,
            'n': Knight,
            'b': Bishop,
            'r': Rook,
            'q': Queen,
            'k': King
        }

        parts = fen.strip().split()
        board_part = parts[0]
        active_color = parts[1]
        castling_rights = parts[2]
        en_passant = parts[3]
        # halfmove_clock = int(parts[4])  # optional, if you track this
        # fullmove_number = int(parts[5])  # optional

        # Clear board first
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col].piece = None

        rows = board_part.split('/')
        for row_idx, fen_row in enumerate(rows):
            col_idx = 0
            for char in fen_row:
                if char.isdigit():
                    col_idx += int(char)  # empty squares
                else:
                    color = 'white' if char.isupper() else 'black'
                    piece_class = piece_map[char.lower()]
                    self.squares[row_idx][col_idx].piece = piece_class(color)
                    col_idx += 1

        # Set next player to move
        self.next_player = 'white' if active_color == 'w' else 'black'

        # Set castling rights (optional - implement flags on King and Rooks or Board)
        # For simplicity, you can set moved = True/False on rooks/kings accordingly:
        # Example:
        for row in [0, 7]:
            king = self.squares[row][4].piece
            if isinstance(king, King):
                king.moved = True  # default to moved, will clear below if rights exist
                # Reset all rook moved states as well to True, then clear below if rights allow
                for col in [0, 7]:
                    rook = self.squares[row][col].piece
                    if isinstance(rook, Rook):
                        rook.moved = True

        if 'K' in castling_rights:
            if isinstance(self.squares[7][4].piece, King):
                self.squares[7][4].piece.moved = False
            if isinstance(self.squares[7][7].piece, Rook):
                self.squares[7][7].piece.moved = False
        if 'Q' in castling_rights:
            if isinstance(self.squares[7][4].piece, King):
                self.squares[7][4].piece.moved = False
            if isinstance(self.squares[7][0].piece, Rook):
                self.squares[7][0].piece.moved = False
        if 'k' in castling_rights:
            if isinstance(self.squares[0][4].piece, King):
                self.squares[0][4].piece.moved = False
            if isinstance(self.squares[0][7].piece, Rook):
                self.squares[0][7].piece.moved = False
        if 'q' in castling_rights:
            if isinstance(self.squares[0][4].piece, King):
                self.squares[0][4].piece.moved = False
            if isinstance(self.squares[0][0].piece, Rook):
                self.squares[0][0].piece.moved = False

        # Set en passant target square
        if en_passant != '-':
            col = ord(en_passant[0]) - ord('a')
            row = 8 - int(en_passant[1])
            # The pawn that can be captured en passant is on the row behind this target square
            # We'll mark that pawn's en_passant flag True
            ep_pawn_row = row + 1 if self.next_player == 'black' else row - 1
            if 0 <= ep_pawn_row < ROWS:
                pawn = self.squares[ep_pawn_row][col].piece
                if isinstance(pawn, Pawn) and pawn.color != self.next_player:
                    pawn.en_passant = True

        # Optionally reset move history or other states if you track them
        self.move_history = []
        self.last_move = None
        self.last_piece = None

    @property
    def current_turn(self):
        return self.next_player

