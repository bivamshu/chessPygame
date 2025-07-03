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

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final
        en_passant_empty = self.squares[final.row][final.col].isempty()
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
        temp_board = copy.deepcopy(self)
        temp_piece = copy.deepcopy(piece)
        temp_board.move(temp_piece, move, testing=True)
        return temp_board.in_check(piece.color)

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
