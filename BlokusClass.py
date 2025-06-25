import tkinter as tk
import numpy as np
from tkinter import messagebox
import AIroutines as AI


BOARD_SIZE = 12
CELL_SIZE = 30
PLAYER1 = True
PLAYER2 = True
PLAYER2_IA = True
PLAYER1_IA = False

STRATEGY=['not_a_player','max_angles','max_angles'] # possibilities: glouton, random, max_angles
VICTORIES = [0, 0, 0]  # Player 1, Player 2, Draw

OVER1 = False
OVER2 = False


# Some basic polyominoes
SAMPLE_PIECES = [
    # Give up piece
    np.array([[2]]),
    # Single square piece
    np.array([[1]]),
    # Two square pieces
    np.array([[1, 1]]),
    # Three square pieces
    np.array([[1, 1, 1]]),
    np.array([[1, 0], [1, 1]]),
    # Four square pieces
    np.array([[1, 1, 1, 1]]),
    np.array([[1, 1 , 1], [0, 0, 1]]),
    np.array([[1, 1 , 1], [0, 1, 0]]),
    np.array([[1, 1 ], [1, 1]]),
    np.array([[1, 1 , 1], [0, 1, 1]]),
    # Five square pieces
    np.array([[1, 1, 1, 1, 1]]), 
    np.array([[1, 1,0], [0, 1,1], [0,0, 1]]),
    np.array([[1, 1 , 1 , 1], [0, 0,  0, 1]]),
    np.array([[1, 1 , 0 , 0 ], [0, 1,  1, 1]]),
    np.array([[1, 0, 1  ], [1, 1,  1]]),
    np.array([[1, 1 , 1 , 1 ], [0, 0,  1, 0]]),
    np.array([[1, 0,0], [1, 1,1], [1,0, 0]]),
    np.array([[1, 0,0], [1, 0,0], [1,1,1]]),
    np.array([[1, 0,0], [1, 1,1], [0,0,1]]),
    np.array([[1, 0,0], [1, 1,1], [0,1,0]]),
    np.array([[0, 1,0], [1, 1,1], [0,1,0]]),
]


class BlokusGUI:
    def __init__(self, master):
        self.master = master
        master.title("Blokus")

        self.frame = tk.Frame(master)
        self.frame.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.frame, width=BOARD_SIZE*CELL_SIZE, height=BOARD_SIZE*CELL_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)
        self.master.bind("<Button-4>", self.mouse_wheel_rotate_up)   # Linux scroll up
        self.master.bind("<Button-5>", self.mouse_wheel_rotate_down)
        self.master.bind("<Left>", self.mirror_vertical)
        self.master.bind("<Right>", self.mirror_vertical)
        self.master.bind("<Up>", self.mirror_horizontal)
        self.master.bind("<Down>", self.mirror_horizontal)

        self.instructions_frame = tk.Frame(master)
        self.instructions_frame.pack(side=tk.BOTTOM, pady=10)

        instructions = (
            "Wheel: Rotate    "
            "← or → : Vertical mirror    "
            "↑ or ↓ : Horizontal mirror"
        )

        tk.Label(self.instructions_frame, text=instructions, font=("Helvetica", 10)).pack()

        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.board_size = BOARD_SIZE
        self.current_player = 1
        self.has_played = {1: False, 2: False}
        self.starting_corners = {1: (0, 0), 2: (BOARD_SIZE-1, BOARD_SIZE-1)}

        self.player_pieces = {1: SAMPLE_PIECES.copy(), 2: SAMPLE_PIECES.copy()}
        self.current_piece = None

        # Side panel for selecting pieces
        self.selector_frame = tk.Frame(master)
        self.selector_frame.pack(side=tk.RIGHT)
        tk.Label(self.selector_frame, text="Select a piece").pack()
        self.piece_buttons = []
        self.render_piece_selector()

        self.current_frame = tk.Frame(master)
        self.current_frame.pack(side=tk.TOP)
        tk.Label(self.current_frame, text="Current piece").pack()
        self.current_canvas = tk.Canvas(self.current_frame, width=100, height=100, bg="white")
        self.current_canvas.pack(padx=0, pady=0)
        self.render_current_piece()

        self.draw_board()
        ai_turn = True
        while (not OVER1 or not OVER2) and ai_turn:
            ai_turn = False
            if self.current_player == 2 and PLAYER2_IA:
                # AI logic for player 2
                self.ai_play()
                self.current_player = 1
                ai_turn = True
            if self.current_player == 1 and PLAYER1_IA:
                # AI logic for player 2
                self.ai_play()
                self.current_player = 2
                ai_turn = True
            self.render_piece_selector()
            self.master.update()


    def handle_right_click(self, event):
        self.rotate_current_piece()

    def mouse_wheel_rotate_up(self, event):
        self.rotate_current_piece(clockwise=True)

    def mouse_wheel_rotate_down(self, event):
        self.rotate_current_piece(clockwise=False)

    def rotate_current_piece(self, clockwise=True):
        if self.current_piece is not None:
            if clockwise:
                # Rotate 90 degrees clockwise = 3 times counterclockwise
                self.current_piece = np.rot90(self.current_piece, k=3)
            else:
                # Rotate 90 degrees counterclockwise
                self.current_piece = np.rot90(self.current_piece)
            self.render_current_piece()
    
    def mirror_vertical(self, event=None):
        if self.current_piece is not None:
            self.current_piece = np.flipud(self.current_piece)
            self.render_current_piece()

    def mirror_horizontal(self, event=None):
        if self.current_piece is not None:
            self.current_piece = np.fliplr(self.current_piece)
            self.render_current_piece()

    def render_piece_selector(self):
        for widget in self.selector_frame.winfo_children()[1:]:
            widget.destroy()
        self.piece_buttons.clear()

        # Label at the top
        label = self.selector_frame.winfo_children()[0]  # Keep the label

        # Create a new frame for the grid layout
        grid_frame = tk.Frame(self.selector_frame)
        grid_frame.pack()

        max_rows = 6
        for idx, piece in enumerate(self.player_pieces[self.current_player]):
            canvas = tk.Canvas(grid_frame, width=100, height=100, bg="white")
            row = idx % max_rows
            col = idx // max_rows
            canvas.grid(row=row, column=col, padx=2, pady=2)

            def make_callback(i=idx):
                return lambda e: self.select_piece(i)

            canvas.bind("<Button-1>", make_callback())
            self.draw_mini_piece(canvas, piece)
            self.piece_buttons.append(canvas)

    def render_current_piece(self):
        self.current_canvas.delete("all")
        piece = self.current_piece if self.current_piece is not None else np.zeros((1, 1))
        self.draw_mini_piece(self.current_canvas, piece)

    def draw_mini_piece(self, canvas, piece):
        box = 20
        if np.all(piece == 2):
            canvas.create_text(50, 50, text="Give Up", font=("Helvetica", 12, "bold"), fill="gray")
            return
        for i in range(piece.shape[0]):
            for j in range(piece.shape[1]):
                if piece[i, j]:
                    if self.current_player == 1:
                        canvas.create_rectangle(j*box, i*box, (j+1)*box, (i+1)*box,
                                            fill="blue", outline="black")
                    else:
                        canvas.create_rectangle(j*box, i*box, (j+1)*box, (i+1)*box,
                                            fill="red", outline="black")

    def select_piece(self, idx):
        self.current_piece_index = idx
        self.current_piece = self.player_pieces[self.current_player][idx]
        self.render_current_piece()
        print(f"Player {self.current_player} selected piece {idx}")


    def draw_board(self):
        self.canvas.delete("all")
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                color = "white"
                if self.board[i, j] == 1:
                    color = "blue"
                elif self.board[i, j] == 2:
                    color = "red"
                self.canvas.create_rectangle(
                    j*CELL_SIZE, i*CELL_SIZE, (j+1)*CELL_SIZE, (i+1)*CELL_SIZE,
                    fill=color, outline="gray"
                )

    def handle_click(self, event):
        global OVER1
        global OVER2
        if self.current_piece is None:
            return
        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE
        print('Clicked at:', row, col)
        if self.can_place(self.current_piece, row, col, self.current_player):
            print(f"Placing piece at ({row}, {col}) for player {self.current_player}")
            self.place_piece(self.current_piece, row, col)
            self.draw_board()
            if self.current_piece_index != 0:
                del self.player_pieces[self.current_player][self.current_piece_index]
            if self.current_piece_index == 0:
                if self.current_player == 1:
                    OVER1 = True
                    if OVER2:
                        self.end_game()
                else:
                    OVER2 = True
                    if OVER1:
                        self.end_game()
            self.current_piece = None
            self.render_current_piece()
            self.current_player = 2 if self.current_player == 1 else 1

            if self.current_player == 2 and PLAYER2_IA:
                # AI logic for player 2
                self.ai_play()
                self.current_player = 1
            if self.current_player == 1 and PLAYER1_IA:
                # AI logic for player 2
                self.ai_play()
                self.current_player = 2
            
            self.render_piece_selector()

    def ai_play(self):
        result = True
        if STRATEGY[self.current_player] == 'random':
            result = self.ai_random()
        elif STRATEGY[self.current_player] == 'glouton':
            result = self.ai_glouton()
        elif STRATEGY[self.current_player] == 'max_angles':
            result = self.ai_max_angles()
        if not result:
            print(f"AI for Player {self.current_player} could not place any piece.")
            if self.current_player == 1:
                global OVER1
                OVER1 = True
            else:
                global OVER2
                OVER2 = True
            if OVER1 and OVER2:
                self.end_game()
            self.current_piece_index = 0
            self.current_piece = None
            self.render_current_piece()
        self.master.update()
        return

    def ai_random(self):
        print("AI is playing for Player 2")
        for _ in range(120):
            idx = np.random.randint(1, len(self.player_pieces[self.current_player]))
            # Try to place the piece on the board
            piece = self.player_pieces[2][idx]
            print(f"AI selected piece {idx} for Player 2")
            for _ in range(np.random.randint(5)):
                piece = np.rot90(piece)
            for _ in range(np.random.randint(2)):
                piece = np.fliplr(piece)
            for _ in range(np.random.randint(2)):
                piece = np.flipud(piece)
            for _ in range(np.random.randint(100)):
                x = np.random.randint(0, BOARD_SIZE)
                y = np.random.randint(0, BOARD_SIZE)
                if self.can_place(piece, x, y, self.current_player):
                    print(f"AI placing piece at ({x}, {y})")
                    self.place_piece(piece, x, y)
                    self.draw_board()
                    self.master.update()
                    del self.player_pieces[self.current_player][idx]
                    return True
        # If no piece can be placed, give up
        return False
        
    
    def ai_glouton(self):
        for size in reversed(range(5)):
            pieces = AI.find_pieces(self, size+1, self.current_player)
            for piece in pieces:
                print(piece)
                for idx, p in enumerate(self.player_pieces[self.current_player]):
                    if np.array_equal(p, piece):
                        self.current_piece_index = idx
                        break
                else:
                    print("Index not found for piece:", piece)
                    self.current_piece_index = None  # or raise an error if it must be found
                
                for small_square in range(BOARD_SIZE):
                    for _ in range(np.random.randint(5)):
                        piece = np.rot90(piece)
                    for _ in range(np.random.randint(2)):
                        piece = np.fliplr(piece)
                    for _ in range(np.random.randint(2)):
                        piece = np.flipud(piece)
                    for x in range(small_square):
                        for y in range(small_square):
                            if self.can_place(piece, x, y, self.current_player):
                                print(f"AI placing piece at ({x}, {y})")
                                self.place_piece(piece, x, y)
                                self.draw_board()
                                self.master.update()
                                del self.player_pieces[self.current_player][self.current_piece_index]
                                return True
                        
        # If no piece can be placed, give up
        return False

    def ai_max_angles(self):
        save_x = save_y = save_idx = save_score = 0
        for size in reversed(range(5)):
            self.current_piece = None
            self.current_piece_index = None
            maxiScore = -1000
            pieces = AI.find_pieces(self, size+1, self.current_player)
            for piece in pieces:
                for idx, p in enumerate(self.player_pieces[self.current_player]):
                    if np.array_equal(p, piece):
                        self.current_piece_index = idx
                        break
                else:
                    print("Index not found for piece:", piece)
                    self.current_piece_index = None  # or raise an error if it must be found

                
                for small_square in range(BOARD_SIZE):
                    for _ in range(np.random.randint(5)):
                        piece = np.rot90(piece)
                    for _ in range(np.random.randint(2)):
                        piece = np.fliplr(piece)
                    for _ in range(np.random.randint(2)):
                        piece = np.flipud(piece)
                    for x in range(small_square):
                        for y in range(small_square):
                            if self.can_place(piece, x, y, self.current_player):
                                copy_board = self.simulate_move(piece, x, y)
                                score = AI.sum_angles(copy_board, BOARD_SIZE)
                                if self.current_player == 2:
                                    score *= -1
                                if score > maxiScore:
                                    maxiScore = score
                                    self.current_piece = piece

                                    save_idx = self.current_piece_index
                                    save_x, save_y = x, y
                                    save_score = score
                                    print(f"AI found better piece at ({x}, {y}) with score {score}")
            
            if self.current_piece is not None:
                print(f"AI placing piece at ({save_x}, {save_y}) with score {save_score}")
                self.place_piece(self.current_piece, save_x, save_y)
                self.draw_board()
                print(f'Current score: {AI.sum_angles(self.board, BOARD_SIZE)}')
                self.master.update()
                del self.player_pieces[self.current_player][save_idx]
                return True
    
        # If no piece can be placed, give up
        return False


    def can_place(self, piece, x, y, player):
        if np.all(piece == 2):
            return True
        global PLAYER1
        global PLAYER2
        px, py = piece.shape
        print(f"Checking if piece can be placed at ({x}, {y}) for player {player}")
        print(f"Piece shape: {piece}")
        if x + px > BOARD_SIZE or y + py > BOARD_SIZE:
            print(f"Cannot place piece at ({x}, {y}), out of bounds.")
            return False
        is_cornered = False
        for i in range(px):
            for j in range(py):
                if piece[i,j]:
                    if piece[i, j] and self.board[x+i, y+j] != 0:
                        print(f"Cannot place piece at ({x+i}, {y+j}), cell already occupied.")
                        return False
                    if not ( (x+i+1>=BOARD_SIZE or self.board[x+i+1,y+j] != player) and (y+j+1>=BOARD_SIZE or self.board[x+i,y+j+1]!=player ) \
                        and (x+i-1<=-1 or self.board[x+i-1,y+j]!=player) and (y+j-1<=-1 or self.board[x+i,y+j-1]!=player)):
                        print(f"Cannot place piece at ({x+i}, {y+j}), other piece touching.")
                        return False
                    if (x+i+1 < BOARD_SIZE and y+j+1 < BOARD_SIZE and self.board[x+i+1,y+j+1] == player):
                        is_cornered = True
                    if (x+i-1 >= 0 and y+j-1 >= 0 and self.board[x+i-1,y+j-1] == player):
                        is_cornered = True
                    if (x+i+1 < BOARD_SIZE and y+j-1 >= 0 and self.board[x+i+1,y+j-1] == player):
                        is_cornered = True
                    if (x+i-1 >= 0 and y+j+1 < BOARD_SIZE and self.board[x+i-1,y+j+1] == player):
                        is_cornered = True
        print('Passed first test')
        if player == 1 and PLAYER1 == True:
            for i in range(px):
                for j in range(py):
                    if piece[i,j] and (x+i, y+j) == self.starting_corners[1]:
                        is_cornered = True
                        PLAYER1 = False
        elif player == 2 and PLAYER2 == True:
            for i in range(px):
                for j in range(py):
                    if piece[i,j] and (x+i, y+j) == self.starting_corners[2]:
                        is_cornered = True
                        PLAYER2 = False
        return is_cornered

    def place_piece(self, piece, x, y):
        if np.all(piece == 2):
            return
        px, py = piece.shape
        for i in range(px):
            for j in range(py):
                if piece[i, j]:
                    self.board[x+i, y+j] = self.current_player
    
    def simulate_move(self, piece, x, y):
        board_copy = np.copy(self.board)
        if np.all(piece == 2):
            return
        px, py = piece.shape
        for i in range(px):
            for j in range(py):
                if piece[i, j]:
                    board_copy[x+i, y+j] = self.current_player
        return board_copy

    def end_game(self):
        print("Game Over!")
        cnt1 = sum((self.board == 1).flatten())
        cnt2 = sum((self.board == 2).flatten())

        if cnt1 > cnt2:
            VICTORIES[0] += 1
            winner = f'Player 1 wins with {cnt1} pieces against {cnt2}! \n {VICTORIES[0]} victories for Player 1 \n {VICTORIES[1]} for Player 2 \n {VICTORIES[2]} draws.'
            
        elif cnt2 > cnt1:
            VICTORIES[1] += 1
            winner = f'Player 2 wins with {cnt2} pieces against {cnt1}!\n {VICTORIES[0]} victories for Player 1 \n {VICTORIES[1]} for Player 2 \n {VICTORIES[2]} draws.'
            
        else:
            VICTORIES[2] += 1
            winner = f'It\'s a tie! \n {VICTORIES[0]} victories for Player 1 \n {VICTORIES[1]} for Player 2 \n {VICTORIES[2]} draws.'
            

        messagebox.showinfo("Game Over", winner)
        self.restart_game()
        if cnt1 > cnt2:
            print("Player 1 wins!")
        elif cnt2 > cnt1:
            print("Player 2 wins!")

    def restart_game(self):
        global PLAYER1, PLAYER2, OVER1, OVER2
        PLAYER1 = PLAYER2 = True
        OVER1 = OVER2 = False

        self.board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.current_player = 1
        self.has_played = {1: False, 2: False}
        self.player_pieces = {1: SAMPLE_PIECES.copy(), 2: SAMPLE_PIECES.copy()}
        self.current_piece = None
        self.current_piece_index = None

        self.draw_board()
        self.render_piece_selector()
        self.render_current_piece()
            
                

if __name__ == "__main__":
    root = tk.Tk()
    app = BlokusGUI(root)
    root.mainloop()