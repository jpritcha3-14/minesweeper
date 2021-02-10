import argparse
import random

import tkinter as tk
from functools import partial

# Size and number of bombs, to be replaced with parseargs
sz = 20 
b = 20

root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

class Tile:
    def __init__(self, isbomb):
        self.isbomb = isbomb
        self.flagged = False
        self.clicked = False

        self.text = tk.StringVar()
        self.text.set(" ")

        self.label = tk.Label(frame, relief="raised", textvariable=self.text, width=2, height=1)
        self.label.bind("<Button-1>", self.left_click)
        self.label.bind("<Button-2>", self.right_click)
        self.label.bind("<Button-3>", self.right_click)

    def left_click(self, event):
        if not self.clicked and not self.flagged:
            self.clicked = True
            self.text.set("b" if self.isbomb else "s")

    def right_click(self, event):
        if not self.clicked:
            if not self.flagged:
                self.flagged = True
                self.text.set("f")
            else:
                self.flagged = False
                self.text.set(" ")

# Map the tile row/col to the 1D set of bombs
def checkbomb(r, c):
    return (r * sz + c) in bombs

tiles = [[] for _ in range(sz)]

# Create a random 1D set of bombs that maps to the 2D tile grid
bombs = set()
while len(bombs) < b:
    bombs.add(random.randint(0,sz**2-1))

# Create the tile grid
for row in range(sz):
    for col in range(sz):
        cur_tile = Tile(checkbomb(row, col))
        cur_tile.label.grid(row=row, column=col)
        tiles[row].append(cur_tile)

root.mainloop()
