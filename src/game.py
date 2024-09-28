import pygame

from const import *
from board import Board
from dragger import Dragger
from move import Move


class Game:
    def __init__(self):
        #the game class initializes a board and a dragger
        self.board = Board() 
        self.dragger = Dragger()
        self.next_player = 'white'
        self.hovered_square = None

    def show_bg(self, surface):
        for row in range(ROWS):
            for col in range(COLUMNS):
                if(row + col) % 2 == 0:
                    color = (234, 235, 200) #light green
                else:
                    color = (119, 154, 88) #dark green

                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)

                pygame.draw.rect(surface, color, rect)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLUMNS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece  

                    #all pieces except the dragger piece.
                    if piece is not self.dragger.piece:
                        piece.set_texture(size = 80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img, piece.texture_rect)
    
    def show_moves(self, surface):
        if self.dragger.dragging:
            piece = self.dragger.piece

            for move in piece.moves:
                color = '#C86464' if (move.final.row + move.final.column) % 2 == 0 else '#C84646'
                rect = (move.final.column * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def last_move(self, surface):
        if self.board.last_move:
            initial = self.board.last_move.initial 
            final = self.board.last_move.final

        
            for pos in [initial, final]:
                color = (244, 247, 116) if (pos.row + pos.column) % 2 == 0 else (172, 195, 51)
                rect = (pos.column * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_square(self, surface):
        if self.hovered_square:
            color = (180, 180, 180)
            rect = (self.hovered_square.column * SQSIZE, self.hovered_square.row * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect, width = 3)

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_square = self.board.squares[row][col]
                    


        

