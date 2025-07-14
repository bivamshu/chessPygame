from board import Board
from v1 import IntelligentBot as BotV1
from v2 import IntelligentBot as BotV2



class MatchManager:
    def __init__(self, BotA_class, BotB_class, depth=2):
        self.BotA_class = BotA_class
        self.BotB_class = BotB_class
        self.depth = depth
        self.results = {"A_wins": 0, "B_wins": 0, "draws": 0}

    def play_match(self, bot_white, bot_black):
        board = Board()
        board.next_player = 'white'

        while True:
            color = board.next_player
            bot = bot_white if color == 'white' else bot_black

            piece, move = bot.select_move(color)
            if piece is None or move is None:
                break  # No legal move

            board.make_move(piece, move)
            board.next_turn()

            # Check game end conditions
            if board.is_checkmate('white'):
                return 'black'
            elif board.is_checkmate('black'):
                return 'white'
            elif len(board.get_all_valid_moves('white')) == 0 and len(board.get_all_valid_moves('black')) == 0:
                return 'draw'

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


        self.print_results()

    def print_results(self):
        print("\n=== Match Results ===")
        print(f"Bot A Wins: {self.results['A_wins']}")
        print(f"Bot B Wins: {self.results['B_wins']}")
        print(f"Draws: {self.results['draws']}")
        total = sum(self.results.values())
        print(f"Bot A Win Rate: {self.results['A_wins'] / total * 100:.1f}%")
