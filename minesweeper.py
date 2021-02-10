import argparse
import random

import tkinter as tk
from collections import deque

# Size and number of bombs, to be replaced with parseargs
sz = 20 
b = 20

# Frame setup
root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

tiles = [[] for _ in range(sz)]

class Tile:
    def __init__(self, row, col, isbomb):
        self.row = row
        self.col = col
        self.isbomb = isbomb 
        self.flagged = False
        self.clicked = False

        self.text = tk.StringVar()
        self.text.set(" ")

        self.label = tk.Label(frame, relief="groove", textvariable=self.text, width=2, height=1)
        self.label.bind("<Button-1>", self.left_click)
        self.label.bind("<Button-2>", self.right_click)
        self.label.bind("<Button-3>", self.right_click)

    @staticmethod
    def inbounds(tile, i, j):
        return (    tile.row + i >= 0 
                and tile.row + i < sz 
                and tile.col + j >= 0 
                and tile.col + j < sz)

    def checkneighbors(self):
        unclicked = deque([self])
        while unclicked:
            bombcount = 0
            cur = unclicked.pop()
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if self.inbounds(cur, i, j):
                        t = tiles[cur.row + i][cur.col + j]
                        if t.isbomb:
                            bombcount += 1
            if bombcount > 0:
                cur.text.set(str(bombcount))

    def left_click(self, event=None):
        if not self.clicked and not self.flagged:
            self.clicked = True
            self.label.config(relief="flat")
            if self.isbomb:
                self.text.set("b")
            else:
                self.text.set(" ")  
                self.checkneighbors()

    def right_click(self, event=None):
        if not self.clicked:
            self.flagged = not self.flagged
            self.text.set("f" if self.flagged else " ")


# Create a random 1D set of bombs that maps to the 2D tile grid
bombs = set()
while len(bombs) < b:
    bombs.add(random.randint(0,sz**2-1))

# Create the tile grid
for row in range(sz):
    for col in range(sz):
        cur_tile = Tile(row, col, (row * sz + col) in bombs)
        cur_tile.label.grid(row=row, column=col)
        tiles[row].append(cur_tile)

root.mainloop()
