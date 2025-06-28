import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move


class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption('Chess')
        self.game_state = 'home'
        self.game = Game()

    def show_home_screen(self):
        self.screen.fill((30, 30, 30))
        font = pygame.font.SysFont('Arial', 36)
        button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 80)
        pygame.draw.rect(self.screen, (50, 50, 50), button_rect)
        text_surface = font.render('Start Game', True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        self.screen.blit(text_surface, text_rect)
        return button_rect

    def mainloop(self):
    
        screen = self.screen
        game = self.game
        board = game.board
        dragger = game.dragger

        while True:
            self.screen.fill((30, 30, 30))

            # Render appropriate screen
            if self.game_state == 'home':
                play_button = self.show_home_screen()

            elif self.game_state == 'game':
                game.show_bg(screen)
                game.show_last_move(screen)
                game.show_moves(screen)
                game.show_pieces(screen)
                game.show_hover(screen)

                if dragger.dragging:
                    dragger.update_blit(screen)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # --- HOME SCREEN EVENT HANDLING ---
                if self.game_state == 'home':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if play_button.collidepoint(event.pos):
                            self.game_state = 'game'
                            self.game.reset()
                            game = self.game
                            board = game.board
                            dragger = self.game.dragger

                # --- GAME SCREEN EVENT HANDLING ---
                elif self.game_state == 'game':

                    # Mouse click
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        dragger.update_mouse(event.pos)

                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

                        if board.squares[clicked_row][clicked_col].has_piece():
                            piece = board.squares[clicked_row][clicked_col].piece
                            if piece.color == game.next_player:
                                board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                dragger.save_initial(event.pos)
                                dragger.drag_piece(piece)
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)

                    # Mouse motion
                    elif event.type == pygame.MOUSEMOTION:
                        motion_row = event.pos[1] // SQSIZE
                        motion_col = event.pos[0] // SQSIZE

                        game.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)
                            dragger.update_blit(screen)

                    # Mouse release
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if dragger.dragging:
                            dragger.update_mouse(event.pos)

                            released_row = dragger.mouseY // SQSIZE
                            released_col = dragger.mouseX // SQSIZE

                            initial = Square(dragger.initial_row, dragger.initial_col)
                            final = Square(released_row, released_col)
                            move = Move(initial, final)

                            if board.valid_move(dragger.piece, move):
                                captured = board.squares[released_row][released_col].has_piece()
                                board.move(dragger.piece, move)
                                board.set_true_en_passant(dragger.piece)
                                game.play_sound(captured)
                                game.show_bg(screen)
                                game.show_last_move(screen)
                                game.show_pieces(screen)
                                game.next_turn()

                        dragger.undrag_piece()

                    # Key press
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_t:
                            game.change_theme()

                        elif event.key == pygame.K_r:
                            game.reset()
                            game = self.game
                            board = game.board
                            dragger = self.game.dragger

            pygame.display.update()



main = Main()
main.mainloop()