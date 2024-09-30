import pygame

from const import *
from board import Board
from dragger import Dragger
from move import Move
from config import Config

class Game:
    def __init__(self):
        #the game class initializes a board and a dragger
        self.board = Board() 
        self.dragger = Dragger()
        self.next_player = 'white'
        self.hovered_square = None
        self.config = Config()

    def show_bg(self, surface):
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLUMNS):
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark

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
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            for move in piece.moves:
                color = theme.moves.light if (move.final.row + move.final.column) % 2 == 0 else theme.moves.dark
                rect = (move.final.column * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial 
            final = self.board.last_move.final

        
            for pos in [initial, final]:
                color = theme.trace.light if (pos.row + pos.column) % 2 == 0 else theme.trace.dark
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
                    
    def change_theme(self):
        self.config.change_themes()


        

