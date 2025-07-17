from match_manager import MatchManager
from v3_piece_square_table import IntelligentBot as BotV1
from v2 import IntelligentBot as BotV2

if __name__ == "__main__":
    manager = MatchManager(BotV1, BotV2, depth=2)
    manager.run_series(games=20)
