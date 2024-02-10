#!/usr/bin/env python
# coding: utf-8

# In[28]:


import os
import chess
import chess.svg
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO

class ChessGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        self.board = chess.Board()
        self.square_size = 50
        self.canvas = tk.Canvas(self.root, width=self.square_size*8, height=self.square_size*8)
        self.canvas.pack()
        self.load_piece_images()
        self.create_extra_images()

        self.start_pos = None
        self.dragged_piece = None
        
        self.draw_board()

        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<B1-Motion>", self.handle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.handle_release)

    def create_extra_images(self):
        def rgba(a,b,c,d):
            # Method for converting color output from a website to a usable format
            # Color picker website: https://rgbacolorpicker.com
            return (a, b, c, int(d*255))

        green = rgba(0, 98, 46, 0.53) #This line can be copied from https://rgbacolorpicker.com
        
        #---- Create Circle Image to use later
        diameter = self.square_size//2
        image1 = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
        draw1 = ImageDraw.Draw(image1)
        draw1.ellipse((0, 0, diameter, diameter), fill= green)
        self.circle = ImageTk.PhotoImage(image1)

        #----- Create piece capture cell
        size = self.square_size
        L = int(size*0.2) #What % of a side length each triangle should be
        image2 = Image.new("RGBA", (size, size), (0,0,0,0))
        draw2 = ImageDraw.Draw(image2)

        # Define the vertices of each triangle
        vertices1 = [(0,0), (0, L), (L, 0)] 
        vertices2 = [(0,size),(L, size),(0,size - L)]
        vertices3 = [(size, size),(size,size - L),(size - L, size)]
        vertices4 = [(size,0),(size - L,0),(size, L)]
        
        # Draw the filled triangles
        draw2.polygon(vertices1, fill=green)
        draw2.polygon(vertices2, fill=green)
        draw2.polygon(vertices3, fill=green)
        draw2.polygon(vertices4, fill=green)
        self.capture = ImageTk.PhotoImage(image2)

        #----- Create "check" highlight
        # Create a blank RGBA image
        image3 = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        
        # Draw a circle with increasing transparency
        draw3 = ImageDraw.Draw(image3)
        center_x = center_y  = max_radius = size // 2
        for r in range(max_radius):
            alpha = int(255//2 * (1 - float(r) / float(max_radius)))+20  # Calculate alpha based on radius
            draw3.ellipse((center_x - r, center_y - r, center_x + r, center_y + r), outline=(255, 0 ,0 , alpha))
            
        self.checkImage = ImageTk.PhotoImage(image3)
    
    def load_piece_images(self):
        self.piece_images = {}
        for piece in ['P', 'N', 'B', 'R', 'Q', 'K']:
            self.piece_images[piece] = Image.open(f"../pieces/PNG/white/{piece}.png")
        for piece in ['p', 'n', 'b', 'r', 'q', 'k']:
            self.piece_images[piece] = Image.open(f"../pieces/PNG/black/{piece}.png")

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = "white" if (row + col) % 2 == 0 else "gray"
                self.canvas.create_rectangle(col * self.square_size, row * self.square_size, (col + 1) * self.square_size, (row + 1) * self.square_size, fill=color)

        self.update_board()

    def update_board(self):
        self.canvas.delete("pieces")
        self.canvas.delete("check")
        self.imgs = [None]*64
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is not None:
                img = self.piece_images[piece.symbol()].resize((self.square_size, self.square_size), Image.Resampling.LANCZOS) #Grab image and format it
                self.imgs[square] = ImageTk.PhotoImage(img)     #Convert to TKinter-compatible format
                x = chess.square_file(square) * self.square_size + self.square_size//2
                y = 7*self.square_size - chess.square_rank(square) * self.square_size + self.square_size//2
                piece_ID = f"{piece.symbol()}{square}"          #Used to handle piece deletion when dragging pieces. Ex. K4
                self.canvas.create_image(x, y, image=self.imgs[square], tag= piece_ID)
                self.canvas.image = self.imgs[square]

                #Determine if king is in check
                if self.board.is_check():
                    king_square = self.board.king(self.board.turn)
                    if square == king_square:
                        self.canvas.create_image(x,y,image = self.checkImage, tag = "check")

    def handle_click(self, event):
        file = event.x // self.square_size
        rank = 7 - (event.y // self.square_size)
        self.start_pos = chess.square(file, rank)
        self.dragged_piece = self.board.piece_at(self.start_pos)
        if self.dragged_piece is None or (self.dragged_piece.color != self.board.turn):
            self.start_pos = None

    def handle_drag(self, event):
        if self.start_pos is not None:
            #Show valid moves with a dot or capture image
            self.canvas.delete("dots")
            self.canvas.delete("capture")
            for square in chess.SQUARES:
                move = chess.Move(self.start_pos, square)

                if move in self.board.legal_moves:
                    x = chess.square_file(square) * self.square_size + self.square_size//2
                    y = 7*self.square_size - chess.square_rank(square) * self.square_size + self.square_size//2
                    if self.board.is_capture(move):
                        self.canvas.create_image(x, y, image = self.capture, tag = "capture")
                    else:
                        self.canvas.create_image(x, y, image=self.circle, tag = "dots")

            #Move the piece around
            x, y = event.x, event.y
            self.canvas.delete("dragged_piece")
            moving_piece_ID = f"{self.board.piece_at(self.start_pos).symbol()}{self.start_pos}"
            self.canvas.delete(moving_piece_ID)
            img = self.piece_images[self.dragged_piece.symbol()]
            img = img.resize((self.square_size, self.square_size), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.canvas.create_image(x, y, image=img_tk, tag="dragged_piece")
            self.canvas.image = img_tk

    def handle_release(self, event):
        if self.start_pos is not None:
            file = event.x // self.square_size
            rank = 7 - (event.y // self.square_size)
            end_pos = chess.square(file, rank)
            move = chess.Move(self.start_pos, end_pos)
            if move in self.board.legal_moves:
                self.board.push(move)
            self.start_pos = None
            self.dragged_piece = None
            self.canvas.delete("dots")
            self.canvas.delete("capture")
            self.update_board()

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGameGUI(root)
    root.mainloop()


# # Bugs to fix
# - [x] Pieces duplicate when picking up: piece on the board doesn't disappear until the moving piece has been placed down.
# - [x] Add dots in the squares showing valid moves
# - [x] Highlight the king's sqare as red when in check
# - [ ] Handle game end
# - [ ] Handle draws
# - [ ] Add piece selecting function (if clicked, the piece is selected)
# - [ ] Add fuctionality to click a piece, then the move to move a piece.
# - [ ] Undo button?

# In[6]:


board = chess.Board()
board.legal_moves
chess.Move(13, 29)
board.push(chess.Move.from_uci('e2e4'))
board.push(chess.Move.from_uci('d7d5'))
board.piece_at(4).symbol().lower()


# In[ ]:





# In[ ]:




