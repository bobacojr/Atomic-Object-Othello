#!/usr/bin/python

import sys
import json
import socket

import math

# All directions a piece can move
DIRS_TO_MOVE = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)]

# Scoring system to help player choose the best move
pos_weights = { 
  "corner_pos": 50000,
  "corner_adj_pos": 50000,
  "middle_pos": 50,
  "edge_pos": 50,
  "piece_num": 30
}

def evaluate_board(board, player, current_player, turn_num):
  score = 0
  
  # Weights for corner positions
  # Very important spaces as they create a stable piece
  for i in [0, 7]:
    for j in [0, 7]:
      if board[i][j] == current_player:
        score += pos_weights["corner_pos"]
    
  # Weights for corner adjacent positions
  # Penalizes the current player since a corner piece can capitalize on this
  for i in [0, 7]:
    for j in [1, 6]:
      if board[0][1] == current_player:
        score -= pos_weights["corner_adj_pos"]
  for i in [1, 6]:
    for j in [0, 1, 6, 7]:
      if board[0][1] == current_player:
        score -= pos_weights["corner_adj_pos"]
      
  # Weights for non-corner and non-corner-adjacent edge positions
  # Worth some points as these can create possible stable pieces
  # Hardcoded checks result in a more aggressive player for edge positions      
  if board[0][2] == current_player:
    score += pos_weights["edge_pos"]
  if board[0][3] == current_player:
    score += pos_weights["edge_pos"]
  if board[0][4] == current_player:
    score += pos_weights["edge_pos"]
  if board[0][5] == current_player:
    score += pos_weights["edge_pos"]
  if board[2][7] == current_player:
    score += pos_weights["edge_pos"]
  if board[3][7] == current_player:
    score += pos_weights["edge_pos"]
  if board[4][7] == current_player:
    score += pos_weights["edge_pos"]
  if board[5][7] == current_player:
    score += pos_weights["edge_pos"]
  if board[7][2] == current_player:
    score += pos_weights["edge_pos"]
  if board[7][3] == current_player:
    score += pos_weights["edge_pos"]
  if board[7][4] == current_player:
    score += pos_weights["edge_pos"]
  if board[7][5] == current_player:
    score += pos_weights["edge_pos"]
  if board[2][0] == current_player:
    score += pos_weights["edge_pos"]
  if board[3][0] == current_player:
    score += pos_weights["edge_pos"]
  if board[4][0] == current_player:
    score += pos_weights["edge_pos"]
  if board[5][0] == current_player:
    score += pos_weights["edge_pos"]
    
  # Weights for start-of-game middle positions
  # Worth some points as these can create move opportunities
  if turn_num < 20:
    for i in [3, 4]:
      for j in [3, 4]:
        if board[i][j] == current_player:
          score += pos_weights["middle_pos"]
   
  # Focus on chip count to increase score in late game
  if turn_num > 20:
    player_pieces = 0
    enemy_pieces = 0
    for row in range(0, 8):
      for col in range(0, 8):
        if board[row][col] == current_player:
          player_pieces += 1
        elif board[row][col] == get_enemy_player(player):
          enemy_pieces += 1
    score += (player_pieces - enemy_pieces) * pos_weights["piece_num"]
  
  # Returns a positive score for player (maximizing)
  # and a negative score for enemy (minimizing)
  if player == current_player:
    return score
  return -score

def minimax(player, board, depth, current_player, turn_num, alpha, beta):
  # Maximize the player
  maximizing_player = player == current_player
  valid_moves = get_valid_moves(board, current_player)
  
  # Base case
  if not valid_moves or depth == 0:
    return ([0, 0], evaluate_board(board, player, current_player, turn_num))
  
  # Setting default value for best_move and best_score
  best_move = [-1, -1]
  best_score = 0
  if maximizing_player:
    best_score = -math.inf
  else:
    best_score = math.inf
  # Current player, maximize
  if maximizing_player:
    for move in valid_moves:
      # Making the move, captures the enemy pieces
      pieces_to_flip = is_valid_move(board, current_player, move)
      for piece in pieces_to_flip:
        board[piece[0]][piece[1]] = current_player
      # Placing our piece
      board[move[0]][move[1]] = current_player
      
      result = minimax(player, board, depth - 1, get_enemy_player(current_player), turn_num, alpha, beta)
      # Updating the best_move and best_score based on the result
      if result[1] > best_score:
        best_move = move
        best_score = result[1]
        
      for piece in pieces_to_flip:
        # Resetting the pieces back to their original state
        board[piece[0]][piece[1]] = get_enemy_player(current_player)
      # Placing our piece
      board[move[0]][move[1]] = 0

      alpha = max(alpha, result[1])
      if beta <= alpha:
        break
  # Enemy, minimize
  else:
    for move in valid_moves:
      # Making the move, captures enemy pieces
      pieces_to_flip = is_valid_move(board, current_player, move)
      for piece in pieces_to_flip:
        board[piece[0]][piece[1]] = current_player
      # Placing the piece
      board[move[0]][move[1]] = current_player
      
      result = minimax(player, board, depth - 1, get_enemy_player(current_player), turn_num, alpha, beta)
      # Updating the best_move and best_score based on the result
      if result[1] < best_score:
        best_move = move
        best_score = result[1]
        
      for piece in pieces_to_flip:
        # Resetting the pieces back to their original state
        board[piece[0]][piece[1]] = get_enemy_player(current_player)
      # Placing the piece
      board[move[0]][move[1]] = 0
        
      beta = min(beta, result[1])
      if beta <= alpha:
        break
  # Returning the best_move and best_score that was found
  return best_move, best_score

def is_on_board(move):
  # Checks to see if the move is on the board
  return move[0] >= 0 and move[0] <= 7 and move[1] >= 0 and move[1] <= 7

def get_valid_moves(board, current_player):
  # Get a list of the valid moves for the
  valid_moves = []
  for row in range(0, 8):
    for col in range(0, 8):
      if is_valid_move(board, current_player, [row, col]):
        valid_moves.append([row, col])
  return valid_moves
      
def get_move(board, player, turn_num):
  # Get the best move from minimax
  result = minimax(player, board, 6, player, turn_num, -math.inf, math.inf)
  print(f'Score: {result[1]}')
  return result[0]

def is_valid_move(board, current_player, move):
  # Checks if the move is valid
  if board[move[0]][move[1]] != 0:
      return []
    
  pieces_to_flip = []
  for row_delta, col_delta in DIRS_TO_MOVE:
    search_row = move[0] + row_delta
    search_col = move[1] + col_delta
    while is_on_board([search_row, search_col]) and board[search_row][search_col] == get_enemy_player(current_player):
      search_row += row_delta
      search_col += col_delta
      if is_on_board([search_row, search_col]) and board[search_row][search_col] == current_player:
        search_row -= row_delta
        search_col -= col_delta
        while not ([search_row, search_col] == move):
          pieces_to_flip.append([search_row, search_col])
          search_row -= row_delta
          search_col -= col_delta
        break
      
  return pieces_to_flip
          
def get_enemy_player(player):
  # Returns the value of the enemy
  if player == 1:
    return 2
  return 1

def prepare_response(move):
  response = '{}\n'.format(move).encode()
  print('sending {!r}'.format(response))
  return response

if __name__ == "__main__":
  port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 1337
  host = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2]) else socket.gethostname()

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect((host, port))
    turn_num = 0
    while True:
      print(f'Turn: {turn_num}')
      data = sock.recv(1024)
      if not data:
        print('connection to server closed')
        break
      json_data = json.loads(str(data.decode('UTF-8')))
      board = json_data['board']
      maxTurnTime = json_data['maxTurnTime']
      player = json_data['player']
      print(player, maxTurnTime, board)

      move = get_move(board, player, turn_num)
      response = prepare_response(move)
      sock.sendall(response)
      turn_num += 2
  finally:
    sock.close()