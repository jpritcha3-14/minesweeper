import argparse
import random
import copy

import tkinter as tk
from itertools import product
from collections import deque
from PIL import ImageTk, Image

class Tile:

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.neighbormines = -1
        self.flagged = False
        self.clicked = False

        self.text = tk.StringVar()
        self.text.set(" ")

        self.label = tk.Label(frame, fg="red", font=font, relief=unclickedstyle, bg=unclickedcolor, bd=1, textvariable=self.text, width=2, height=1)
        self.label.bind("<ButtonRelease-1>", self.left_click)
        self.label.bind("<Button-1>", self.anticipate)
        self.label.bind("<ButtonRelease-2>", self.right_click)
        self.label.bind("<ButtonRelease-3>", self.right_click)

    def ismine(self):
        return (self.row * sz + self.col) in mines

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
            minecount = 0
            unclicked = deque() 
            cur = q.pop()
            for i, j in product([-1, 0, 1], [-1, 0, 1]):
                if self.inbounds(cur, i, j):
                    t = tiles[cur.row + i][cur.col + j]
                    if t.ismine():
                        minecount += 1
                    else:
                        if not t.clicked and t.neighbormines == -1:
                            unclicked.append(t)
            if minecount > 0:
                cur.neighbormines = minecount
                cur.text.set(cur.neighbormines)
                cur.label.config(relief=clickedstyle, bg=clickedcolor, fg=numcolor[cur.neighbormines])
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

    def anticipate(self, event=None):
        if not self.flagged and not self.clicked:
            self.label.config(relief=clickedstyle)
            avatar.config(image=anticipate)

    def left_click(self, event=None):
        if not self.flagged and not self.clicked:
            avatar.config(image=fine)
            self.label.config(relief=unclickedstyle)
            if self.inside(event.x, event.y):
                self.clicked = True
                self.label.config(relief=clickedstyle, bg=clickedcolor)
                if self.ismine():
                    avatar.config(image=dead)
                    for r, c in map(lambda b: (b // sz, b % sz), mines):
                        tiles[r][c].label.configure(fg="black", bg="red")
                        if not tiles[r][c].flagged:
                            tiles[r][c].text.set("*")
                else:
                    self.checkneighbors()

    def right_click(self, event=None):
        if not self.clicked and self.inside(event.x, event.y):
            self.flagged = not self.flagged
            if self.flagged:
                self.text.set("!")
            else:
                self.text.set(" ")
                
def restart_game(event=None):
    # Reset Avatar
    avatar.config(image=fine)

    # Create a random 1D set of mines that maps to the 2D tile grid
    # These are managed independently of individual tiles, with the
    # self.ismine() function used for lookup
    mines.clear()
    while len(mines) < b:
        mines.add(random.randint(0,sz**2-1))

    print('here')

    # Reset all tiles 
    for row in range(sz):
        for col in range(sz):
            tiles[row][col].text.set(" ")
            tiles[row][col].label.config(fg="red", relief=unclickedstyle, bg=unclickedcolor)
            tiles[row][col].row = row
            tiles[row][col].col = col
            tiles[row][col].neighbormines = -1
            tiles[row][col].flagged = False
            tiles[row][col].clicked = False

    root.mainloop()
    
# Size and number of mines, to be replaced with parseargs
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
frame.pack(side="bottom")
status = tk.Frame(root)
status.pack(side="top")

tiles = [[] for _ in range(sz)]
mines = set()

# Create the tile grid
for row in range(sz):
    for col in range(sz):
        cur_tile = Tile(row, col)
        cur_tile.label.grid(row=row, column=col)
        tiles[row].append(cur_tile)

fine = tk.PhotoImage(file="fine.gif")
dead = tk.PhotoImage(file="dead.gif")
anticipate = tk.PhotoImage(file="anticipate.gif")
win = tk.PhotoImage(file="dead.gif")

avatar = tk.Label(status, image=fine)
avatar.pack()
avatar.bind('<Button-1>', restart_game)

restart_game()
