import argparse
import random

import tkinter as tk
from itertools import product
from collections import deque

# Size and number of bombs, to be replaced with parseargs
sz = 20 
b = 50

# Color and style config
clickedstyle="sunken"
clickedcolor="gray80"
unclickedstyle="raised"
unclickedcolor="gray65"
font="consolas 10 bold"
numcolor = {1:"blue", 2:"green", 3:"red", 4:"purple", 5:"yellow", 6:"turquoise3", 7:"black", 8:"lightskyblue4"}

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
        self.neighborbombs = -1
        self.flagged = False
        self.clicked = False

        self.text = tk.StringVar()
        self.text.set(" ")

        self.label = tk.Label(frame, font=font, relief=unclickedstyle, bg=unclickedcolor, bd=1, textvariable=self.text, width=2, height=1)
        self.label.bind("<ButtonRelease-1>", self.left_click)
        self.label.bind("<ButtonRelease-2>", self.right_click)
        self.label.bind("<ButtonRelease-3>", self.right_click)

    @staticmethod
    def inbounds(tile, i, j):
        return (    tile.row + i >= 0 
                and tile.row + i < sz 
                and tile.col + j >= 0 
                and tile.col + j < sz)
    
    def checkneighbors(self):
        q = deque([self])
        physicalclick = True
        while q:
            bombcount = 0
            unclicked = deque() 
            cur = q.pop()
            for i, j in product([-1, 0, 1], [-1, 0, 1]):
                if self.inbounds(cur, i, j):
                    t = tiles[cur.row + i][cur.col + j]
                    if t.isbomb:
                        bombcount += 1
                    else:
                        if not t.clicked and t.neighborbombs == -1:
                            unclicked.append(t)
            if bombcount > 0:
                cur.neighborbombs = bombcount
                cur.text.set(cur.neighborbombs)
                cur.label.config(relief=clickedstyle, bg=clickedcolor, fg=numcolor[cur.neighborbombs])
                cur.clicked = True
            else:
                if not cur.flagged:
                    q.extend(unclicked)
                    cur.text.set(" ")
                    cur.clicked = True
                    cur.label.config(relief=clickedstyle, bg=clickedcolor)
            physicalclick = False

    def inside(self, x, y):
        return x >= 0 and y >= 0 and x < self.label.winfo_width() and y < self.label.winfo_height()

    def left_click(self, event=None):
        print(self.label.winfo_height(), self.label.winfo_width(), event.y, event.x)
        if not self.clicked and not self.flagged and self.inside(event.x, event.y):
            self.clicked = True
            self.label.config(relief=clickedstyle, bg=clickedcolor)
            if self.isbomb:
                self.text.set("b")
            else:
                self.text.set(" ")  
                self.checkneighbors()

    def right_click(self, event=None):
        if not self.clicked and self.inside(event.x, event.y):
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
