import numpy as np
import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
ROWS = 6
COLUMNS = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
WIDTH = COLUMNS * SQUARESIZE
HEIGHT = (ROWS + 1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2

# Screen setup
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Connect 4")

# Fonts
font = pygame.font.SysFont("monospace", 75)

def create_board():
    board = np.zeros((ROWS, COLUMNS), dtype=int)
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROWS-1][col] == EMPTY

def get_next_open_row(board, col):
    for r in range(ROWS):
        if board[r][col] == EMPTY:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    for c in range(COLUMNS-3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    for c in range(COLUMNS):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    for c in range(COLUMNS-3):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    for c in range(COLUMNS-3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER1 if piece == PLAYER2 else PLAYER2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    # Center column preference
    center_array = [int(i) for i in list(board[:, COLUMNS//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMNS-3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    # Vertical
    for c in range(COLUMNS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # Positive diagonal
    for r in range(ROWS-3):
        for c in range(COLUMNS-3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Negative diagonal
    for r in range(ROWS-3):
        for c in range(COLUMNS-3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER1) or winning_move(board, PLAYER2) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, PLAYER2):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER1):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, PLAYER2))
    if maximizingPlayer:
        value = -math.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER2)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else: # Minimizing player
        value = math.inf
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER1)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMNS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def draw_board(board):
    for c in range(COLUMNS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE + SQUARESIZE/2), int(r*SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), RADIUS)
    
    for c in range(COLUMNS):
        for r in range(ROWS):
            if board[r][c] == PLAYER1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE + SQUARESIZE/2), HEIGHT - int(r*SQUARESIZE + SQUARESIZE/2)), RADIUS)
            elif board[r][c] == PLAYER2:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE + SQUARESIZE/2), HEIGHT - int(r*SQUARESIZE + SQUARESIZE/2)), RADIUS)
    pygame.display.update()

board = create_board()
print_board(board)
game_over = False
turn = 0

draw_board(board)
pygame.display.update()

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
            if turn == 0:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER1)

                    if winning_move(board, PLAYER1):
                        label = font.render("Player 1 wins!", 1, RED)
                        screen.blit(label, (40,10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

                    print_board(board)
                    draw_board(board)

    if turn == 1 and not game_over:
        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, PLAYER2)

            if winning_move(board, PLAYER2):
                label = font.render("Player 2 wins!", 1, YELLOW)
                screen.blit(label, (40,10))
                game_over = True

            print_board(board)
            draw_board(board)

            turn += 1
            turn = turn % 2

    if game_over:
        pygame.time.wait(3000)
