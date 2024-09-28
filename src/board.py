from const import *
from square import Square
from piece import * 
from move import Move 

class Board:
    def __init__(self):
        '''
        This function initializes the varaibles when an object of this class is created. It first creates a 8X8 array that will keep
        objects squares as elements. Then it calls the create and add pieces methods. The add pieces method is called twice so that 
        pieces are created for each color.
        '''
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0,] for col in range(COLUMNS)]
        self.last_move = None 
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move):
        initial = move.initial
        final = move.final

        self.squares[initial.row][initial.column].piece = None 
        self.squares [final.row][final.column].piece = piece

        piece.moved = True

        piece.clear_moves()     
        self.last_move = move

    def valid_move(self, piece, move):
        
        return move in piece.moves

    def calc_moves(self, piece, row, col):

        def knight_moves():
            possible_moves = [
                (row - 2, col + 1),
                (row - 2, col - 1),
                (row + 2, col + 1),
                (row + 2, col - 1),
                (row - 1, col + 2),
                (row - 1, col - 2),
                (row + 1, col + 2),
                (row + 1, col - 2)
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                    
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)

                        move = Move(initial, final)
                        piece.add_move(move)
        
        def pawn_moves():
            '''
                This function begins by calculating the number of steps a pawn can move. Piece class has an attribute that records 
                whether a piece has moved or not. So if piece.moved is equal to true the piece has moved hence the number of square 
                it can move is one. 

                The start variable is equal to the row it occupies + piece.dir. piece.dir is either plus one or minus one. So 'start' 
                stores the number of the row right before the pawn and 'end' stores the last row the pawn can move to. First the 
                number of steps the pawn can move. Let's suppose it's 2. Add one and it becomes 3. 
                
                The for loop loops through the start the pawn can move to, to the last row the pawn can move to. it first checks if
                the row it can move to is within the board. It true, if the square is empty. If that is true as well, initial variable
                is set to the current position and final is set equal to the square that has just been checked. A move object is 
                created and is added to the possible moves of that piece. When the show_moves function is called, all the squares in
                the array are painted red.
                
                '''
            steps = 1 if piece.moved else 2

            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))

            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].isempty():
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)

                        move = Move(initial, final)
                        piece.add_move(move)

                    else:  break
                else: break

            possible_move_row = row + piece.dir
            possible_move_cols = [col - 1, col + 1]

            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)

                        move = Move(initial, final)
                        piece.add_move(move)

        def straight_line_moves(incrs):
            for inc in incrs:
                row_inc, col_inc = inc
                possible_move_row = row + row_inc
                possible_move_col = col + col_inc

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)

                        move = Move(initial, final)

                        if self.squares[possible_move_row][possible_move_col].isempty():
                            piece.add_move(move)
                        
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            piece.add_move(move)
                            break

                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break

                    else: break

                    possible_move_row = possible_move_row + row_inc
                    possible_move_col = possible_move_col + col_inc

        def king_moves():
            possible_moves = [(row + 1, col),
                            (row - 1, col), 
                            (row, col - 1), 
                            (row, col + 1), 
                            (row + 1, col + 1), 
                            (row + 1, col - 1),
                            (row - 1, col + 1),
                            (row - 1, col - 1)
                            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):
                    initial = Square(row, col)
                    final = Square(possible_move_row, possible_move_col)

                    move = Move(initial, final)

                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        piece.add_move(move)

        if isinstance(piece, Pawn): pawn_moves()

        elif isinstance(piece, Knight): knight_moves()

        elif isinstance(piece, Bishop):
            straight_line_moves(
                [(-1, 1), (1, 1), (1, -1), (-1, -1)]
            )

        elif isinstance(piece, Rook):
            straight_line_moves(
                [(-1, 0),
                (1, 0),
                (0, 1),
                (0, -1)]
            )
            
        elif isinstance(piece, Queen):
            straight_line_moves(
                [(-1, 1), (1, 1), (1, -1), (-1, -1), (-1, 0), (1, 0), (0, 1), (0, -1)]
            )
        
        elif isinstance(piece, King):
            king_moves()

    def _create(self):
        '''
            This method creates and inserts Square objects into the squares array. A nested loop, first one looping through the rows
            and the second one looping through the columns, is used to fill in the 2d array used as the board. Square object has two 
            attributes, row and column, which together tell the position of that square in the board. 
        '''
        for row in range(ROWS):
            for col in range(COLUMNS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        '''
            In Chess there are two sets of pieces: one white and one black. This method is responsible for adding all the pieces of a 
            specific color (white or black) to their respective positions on the board.

            - The 'row_pawn' variable holds the row number for the pawns of the given color. For white pieces, the pawns occupy the 
            second row(index 6) and for the black pieces, the pawns occupy the seventh row(index 1).

            -The 'other_row' variable hold the row number where the other major pieces (knights, bishops, rooks, queens, and King) are
            placed. White pieces occupy the first row(index 7) and black pieces occupy the eigth row(index 8).

            After determining the appropriate rows based on the color, the method proceeds to place the pieces. 

            1. **Pawns**:
            - A loop iterates through each column (0 to 7), placing pawns in the 'row_pawn' row of the specified color. The pawns are
            positioned in every column in their respective row. 

            2. **Knights**
            - The Knights are placed in third column from the left (index 2) and the third column from the right (index 5) in the 
            row_other of the specified color.

            3. **Bishops**
        '''
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        #placing the pawns
        for col in range(COLUMNS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        self.squares[5][1] = Square(5, 0, Pawn(color))

        #knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        #bishops 
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        self.squares[5][5] = Square(row_other, 5, Bishop(color))




        #rooks 
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        self.squares[3][7] = Square(row_other, 7, Rook('white'))

        #queens
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))
        self.squares[4][3] = Square(row_other, 3, Queen('white'))

        #kings
        self.squares[row_other][4] = Square(row_other, 4, King(color))
        
