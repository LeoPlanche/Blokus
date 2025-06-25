import numpy as np

def find_pieces(game, size, player):
    """
    Find all pieces of a given size for a player in the game.
    
    Args:
        game: The game state object.
        size: The size of the pieces to find.
        player: The player whose pieces are being searched for.
    
    Returns:
        A list of pieces of the specified size for the player.
    """
    return [piece for piece in game.player_pieces[player] if ( sum((piece == 1).flatten()) == size)]

def sum_angles(board, board_size):
    cnt1 = 0
    cnt2 = 0
    for x in range( board_size):
        for y in range(board_size):
            if board[x, y] == 0:
                for player in [1,2]:
                    if ((y+1 < board_size  and x+1< board_size and board[x+1, y+1] == player) or \
                        (y-1 >= 0 and x+1 < board_size and board[x+1, y-1] == player) or \
                        (y+1 < board_size and x-1 >= 0 and board[x-1, y+1] == player) or \
                        (y-1 >= 0 and x-1 >= 0 and board[x-1, y-1] == player)) and \
                        (y+1 == board_size or board[x, y+1] != player) and \
                        (y-1 == -1 or board[x, y-1] != player) and \
                        (x+1 == board_size or board[x+1, y] != player) and \
                        (x-1 == -1 or board[x-1, y] != player):
                            if player == 1:
                                cnt1 += 1
                            else:
                                cnt2 += 1
    return cnt1-cnt2