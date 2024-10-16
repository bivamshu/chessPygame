class Square:

    ALPHACOLS = {0: 'A',
                1: 'B',
                2: 'C',
                3: 'D',
                4: 'E',
                5: 'F',
                6: 'G',
                7: 'H'
                }

    def __init__(self, row, column, piece = None):
        #initializes the Square class
        self.row = row #self.row assigns the value of the parameter received by the class when an object of the class is created.
        self.column = column #self.column is a property of a square. column is the argument that is passed into the the function 
                            #when an object is created. 
        self.piece = piece #the default value of piece is None. This means that the square is empty. 
        self.alphacol = self.ALPHACOLS[column]

    def __eq__(self, other):
        return self.row == other.row and self.column == other.column

    def has_piece(self):
        '''This function checks if self.piece, an attribute of the Square class, that tells whether or not the square of a chessboard has
        a piece or not and which piece it has, is equal to None or not. If self.piece is not equal to None, that would mean that it is 
        does have a piece. Hence, it returns None.'''
        return self.piece != None
    
    def isempty(self):
        '''
            This methods returns true if the the square it checks is empty. The function has_piece returns true if a square is NOT empty.
            So, isempty is simply a negation of has_piece. Whatever, has_piece returns, isempty returns the opposite. 
        '''
        return not self.has_piece()
    
    def has_team_piece(self, color):
        '''
            This function returns whether a square has a team piece or not. First it checks whether a square has a piece. It takes color 
            as a parameter. Color is the color the player is playing as. So, if the square has a piece and the color of the piece is equal
            to the color of the player, then the piece in the square being checked is a team_piece.
        '''
        return self.has_piece() and self.piece.color == color
    
    def has_enemy_piece(self, color):
        '''
            This function tells whether a square has the rival piece or not. First it checks whether the square has a piece. It takes 
            color as a parameter. Color is the color that player is playing as. So, if the square has a piece and the color of the piece
            is not equal to the color of the player, the function returns True.
        '''
        return self.has_piece() and self.piece.color != color
    
    def isempty_or_enemy(self, color):
        '''
            This function calculates whether a square is empty OR it has a rival piece. If it returns true, then the square is one where
            a piece can move to 
        '''
        return self.isempty() or self.has_enemy_piece(color)

    @staticmethod
    def in_range(*args):
        for arg in args:
            if arg < 0 or arg > 7:
                return False
            
        return True
    
    @staticmethod

    def get_alphacol(col):
        ALPHACOLS = {0: 'A',
                1: 'B',
                2: 'C',
                3: 'D',
                4: 'E',
                5: 'F',
                6: 'G',
                7: 'H'
                }
        return ALPHACOLS[col]