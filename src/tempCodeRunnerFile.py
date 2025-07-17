from board import Board
from v3_piece_square_table import IntelligentBot as BotV1  # Original bot
from v4 import IntelligentBot as BotV2  # King safety bot
import hashlib

def test_bots(num_games=10):
    """Test new bot against old bot"""
    results = {"v1_wins": 0, "v2_wins": 0, "draws": 0}
    
    print(f"Testing: V1 (Original) vs V2 (King Safety)")
    print(f"Games: {num_games}")
    print("-" * 50)
    
    for game in range(num_games):
        board = Board()
        
        # Alternate colors each game
        if game % 2 == 0:
            white_bot = BotV1(board, depth=2)
            black_bot = BotV2(board, depth=2)
            white_name = "V1"
            black_name = "V2"
        else:
            white_bot = BotV2(board, depth=2)
            black_bot = BotV1(board, depth=2)
            white_name = "V2"
            black_name = "V1"
        
        print(f"Game {game + 1}: {white_name} (white) vs {black_name} (black)")
        
        # Play the game
        winner = play_game(board, white_bot, black_bot)
        
        # Record result
        if winner == 'white':
            if white_name == "V1":
                results["v1_wins"] += 1
                print(f"  Result: V1 wins")
            else:
                results["v2_wins"] += 1
                print(f"  Result: V2 wins")
        elif winner == 'black':
            if black_name == "V1":
                results["v1_wins"] += 1
                print(f"  Result: V1 wins")
            else:
                results["v2_wins"] += 1
                print(f"  Result: V2 wins")
        else:
            results["draws"] += 1
            print(f"  Result: Draw")
    
    # Print final results
    print("\n" + "=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    total = sum(results.values())
    print(f"V1 (Original): {results['v1_wins']} wins ({results['v1_wins']/total*100:.1f}%)")
    print(f"V2 (King Safety): {results['v2_wins']} wins ({results['v2_wins']/total*100:.1f}%)")
    print(f"Draws: {results['draws']} ({results['draws']/total*100:.1f}%)")
    
    # Show improvement
    if results['v2_wins'] > results['v1_wins']:
        print(f"\n✅ V2 is better! (+{results['v2_wins'] - results['v1_wins']} games)")
    elif results['v1_wins'] > results['v2_wins']:
        print(f"\n❌ V1 is better! (+{results['v1_wins'] - results['v2_wins']} games)")
    else:
        print("\nTied performance")


def play_game(board, white_bot, black_bot, max_moves=150):
    """Play a single game between two bots with repetition and draw detection."""
    moves = 0
    position_counts = {}

    def board_hash(board):
        """Simple hash using piece positions and turn."""
        state_str = ""
        for row in board.squares:
            for square in row:
                piece = square.piece
                if piece:
                    state_str += f"{piece.name[0]}{piece.color[0]}"
                else:
                    state_str += "."
        state_str += board.current_turn
        return hashlib.md5(state_str.encode()).hexdigest()


    while moves < max_moves:
        current_color = 'white' if moves % 2 == 0 else 'black'
        current_bot = white_bot if current_color == 'white' else black_bot

        # Checkmate
        if board.is_checkmate(current_color):
            print(f"Checkmate! {('black' if current_color == 'white' else 'white')} wins")
            return 'black' if current_color == 'white' else 'white'

        # Stalemate
        valid_moves = board.get_all_valid_moves(current_color)
        if not valid_moves:
            print("No valid moves left. Stalemate.")
            return 'draw'

        # Repetition detection
        hash_key = board_hash(board)
        position_counts[hash_key] = position_counts.get(hash_key, 0) + 1
        if position_counts[hash_key] >= 3:
            print("Threefold repetition detected. Draw.")
            return 'draw'

        try:
            piece, move, eval_score = current_bot.select_move(current_color, return_eval=True)

            if piece is None or move is None:
                print("Bot returned no move.")
                return 'draw'

            print(f"{current_color.capitalize()} move {moves+1}: {piece.__class__.__name__} {move} Eval: {eval_score:.2f}")

            board.make_move(piece, move)
            board.next_turn()
            moves += 1

        except Exception as e:
            print(f"Error on move {moves+1}: {e}")
            return 'draw'

    print("Max move limit reached.")
    return 'draw'

if __name__ == "__main__":
    test_bots(20)
