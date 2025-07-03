import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move


class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game_state = 'home'
        self.game = Game()

    def show_home_screen(self):
        self.screen.fill((30, 30, 30))
        font = pygame.font.SysFont('Arial', 36)

        # PvP button
        pvp_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 90, 300, 70)
        pygame.draw.rect(self.screen, (100, 100, 100), pvp_rect)
        pvp_text = font.render('Player vs Player', True, (255, 255, 255))
        pvp_text_rect = pvp_text.get_rect(center=pvp_rect.center)
        self.screen.blit(pvp_text, pvp_text_rect)

        # Random Bot button
        bot_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 10, 300, 70)
        pygame.draw.rect(self.screen, (70, 70, 70), bot_rect)
        bot_text = font.render('Play vs Random Bot', True, (255, 255, 255))
        bot_text_rect = bot_text.get_rect(center=bot_rect.center)
        self.screen.blit(bot_text, bot_text_rect)

        return pvp_rect, bot_rect

    def mainloop(self):
        screen = self.screen
        game = self.game
        board = game.board
        dragger = game.dragger

        while True:
            self.screen.fill((30, 30, 30))

            if self.game_state == 'home':
                play_button, bot_button = self.show_home_screen()

            elif self.game_state == 'game':
                game.show_bg(screen)
                game.show_last_move(screen)
                game.show_moves(screen)
                game.show_pieces(screen)
                game.show_hover(screen)

                if dragger.dragging:
                    dragger.update_blit(screen)

            elif self.game_state == 'random_bot':
                game.show_bg(screen)
                game.show_last_move(screen)
                game.show_moves(screen)
                game.show_pieces(screen)
                game.show_hover(screen)

                if dragger.dragging:
                    dragger.update_blit(screen)

                # Let the bot play when it's its turn
                if game.next_player == 'black' and not dragger.dragging:
                    from random_bot import RandomBot
                    bot = RandomBot(board)
                    piece, move = bot.select_move('black')
                    if piece and move:
                        captured = board.squares[move.final.row][move.final.col].has_piece()
                        board.move(piece, move)
                        board.set_true_en_passant(piece)
                        game.play_sound(captured)
                        game.next_turn()

                        print('FEN:', board.fen())


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Home screen event handling
                if self.game_state == 'home':
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if play_button.collidepoint(event.pos):
                            self.game_state = 'game'
                            self.game.reset()
                            game = self.game
                            board = game.board
                            dragger = self.game.dragger

                        elif bot_button.collidepoint(event.pos):
                            self.game_state = 'random_bot'
                            self.game.reset()
                            game = self.game
                            board = game.board
                            dragger = self.game.dragger

                # Game screen event handling
                elif self.game_state in ['game', 'random_bot']:
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

                    elif event.type == pygame.MOUSEMOTION:
                        motion_row = event.pos[1] // SQSIZE
                        motion_col = event.pos[0] // SQSIZE

                        #Only call set_hover if within bounds
                        if 0 <= motion_row < ROWS and 0 <= motion_col < COLS:
                            game.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)

                            #Only show hover if within bounds
                            if 0 <= motion_row < ROWS and 0 <= motion_col < COLS:
                                game.show_hover(screen)

                            dragger.update_blit(screen)


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

                                print('FEN:', board.fen())


                                valid_moves = board.get_all_valid_moves(game.next_player)
                                if not valid_moves:
                                    if board.is_checkmate(game.next_player):
                                        print(f"{game.next_player.capitalize()} is checkmated!")
                                    else:
                                        print(f"Stalemate! {game.next_player.capitalize()} has no valid moves.")
                                    
                                    self.game_state = 'home'

                        dragger.undrag_piece()

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
