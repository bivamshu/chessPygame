from board import Board
from v1 import IntelligentBot as BotV1
from v2 import IntelligentBot as BotV2
import time
import json
from datetime import datetime


class MatchManager:
    def __init__(self, BotA_class, BotB_class, depth=2):
        self.BotA_class = BotA_class
        self.BotB_class = BotB_class
        self.depth = depth
        self.results = {"A_wins": 0, "B_wins": 0, "draws": 0}

    def play_match(self, bot_white, bot_black):
        board = Board()
        board.next_player = 'white'
        game_log = []  # to store move history

        move_number = 1
        while True:
            color = board.next_player
            bot = bot_white if color == 'white' else bot_black

            start_time = time.time()
            piece, move = bot.select_move(color)
            move_time = time.time() - start_time

            if piece is None or move is None:
                break  # No legal move

            captured = move.final.piece is not None
            move_str = f"{type(piece).__name__} from {move.initial.name} to {move.final.name}"


            if captured:
                move_str += f" capturing {move.final.piece.symbol()}"

            print(f"{move_number}. {color.capitalize()} ({'Bot A' if bot is bot_white else 'Bot B'}) plays: {move_str} [Time: {move_time:.2f}s]")

            game_log.append({
                "move_number": move_number,
                "color": color,
                "bot": "A" if bot is bot_white else "B",
                "from": move.initial.name,
                "to": move.final.name,
                "piece": piece.__class__.__name__,
                "captured": move.final.piece.__class__.__name__ if captured else None,
                "time": move_time
            })

            board.make_move(piece, move)
            board.next_turn()
            move_number += 1

            # Game end check
            if board.is_checkmate('white'):
                self.save_game(game_log, "black")
                return 'black'
            elif board.is_checkmate('black'):
                self.save_game(game_log, "white")
                return 'white'
            elif len(board.get_all_valid_moves('white')) == 0 and len(board.get_all_valid_moves('black')) == 0:
                self.save_game(game_log, "draw")
                return 'draw'

        self.save_game(game_log, "draw")
        return 'draw'

    def run_series(self, games=10):
        for i in range(games):
            print(f"Game {i+1} — ", end='')

            shared_board = Board()  # Shared board for both bots

            # Alternate colors
            if i % 2 == 0:
                botA = self.BotA_class(shared_board, self.depth)
                botB = self.BotB_class(shared_board, self.depth)
                result = self.play_match(botA, botB)
            else:
                botB = self.BotB_class(shared_board, self.depth)
                botA = self.BotA_class(shared_board, self.depth)
                result = self.play_match(botB, botA)

            # Tally
            if result == 'white' and i % 2 == 0:
                self.results["A_wins"] += 1
                print("Bot A wins as white")
            elif result == 'black' and i % 2 == 1:
                self.results["A_wins"] += 1
                print("Bot A wins as black")
            elif result == 'draw':
                self.results["draws"] += 1
                print("Draw")
            else:
                self.results["B_wins"] += 1
                print("Bot B wins")

        self.print_results()

    def save_game(self, game_log, winner):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"game_{timestamp}.json"
        data = {
            "winner": winner,
            "depth": self.depth,
            "log": game_log,
            "timestamp": timestamp
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved game to {filename}")


    def print_results(self):
        print("\n=== Match Results ===")
        print(f"Bot A Wins: {self.results['A_wins']}")
        print(f"Bot B Wins: {self.results['B_wins']}")
        print(f"Draws: {self.results['draws']}")
        total = sum(self.results.values())
        print(f"Bot A Win Rate: {self.results['A_wins'] / total * 100:.1f}%")
