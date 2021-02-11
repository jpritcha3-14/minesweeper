import argparse
import random

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

    def __key__(self):
        return (self.row, self.col)

    def __hash__(self):
        return hash(self.__key__())

    def __eq__(self, other):
        if isinstace(other, Tile):
            return self.__key__() == other.__key__()
        return NotImplemented
    
    def ismine(self):
        return (self.row * sz + self.col) in mines

    @staticmethod
    def inbounds(tile, i, j):
        return (    tile.row + i >= 0 
                and tile.row + i < sz 
                and tile.col + j >= 0 
                and tile.col + j < sz)
    
    def checkneighbors(self):
        global first_click
        global tiles_left
        q = set([self])
        seen = set()
        while q:
            minecount = 0
            unclicked = set() 
            cur = q.pop()
            # Iterate through all 8 neighbors, counting mines, queueing empty tiles
            for i, j in product([-1, 0, 1], [-1, 0, 1]):
                if self.inbounds(cur, i, j):
                    t = tiles[cur.row + i][cur.col + j]
                    if t.ismine():
                        minecount += 1
                    else:
                        if not t.clicked and t.neighbormines == -1 and t not in seen:
                            unclicked.add(t)
            # If there's at least one mine, don't add unclicked to q
            if minecount > 0:
                if first_click:
                    shuffle_mines()
                    q.add(cur)
                    continue
                cur.neighbormines = minecount
                cur.text.set(cur.neighbormines)
                cur.label.config(relief=clickedstyle, bg=clickedcolor, fg=numcolor[cur.neighbormines])
                cur.clicked = True
                tiles_left -= 1
                print('Num:', tiles_left)
            else:
                if not cur.flagged:
                    q.update(unclicked)
                    seen.update(unclicked)
                    cur.text.set(" ")
                    cur.clicked = True
                    cur.label.config(relief=clickedstyle, bg=clickedcolor)
                    first_click = False
                    tiles_left -= 1
                    print('Blank:', tiles_left)
            if tiles_left == 0:
                avatar.config(image=win)
                unbind_tiles()


    def inside(self, x, y):
        return x >= 0 and y >= 0 and x < self.label.winfo_width() and y < self.label.winfo_height()

    def anticipate(self, event=None):
        if not self.flagged and not self.clicked:
            self.label.config(relief=clickedstyle)
            avatar.config(image=anticipate)

    def left_click(self, event=None):
        global first_click
        global tiles_left
        if not self.flagged and not self.clicked:
            avatar.config(image=fine)
            self.label.config(relief=unclickedstyle)
            if self.inside(event.x, event.y):
                if first_click and self.ismine():
                    while self.ismine():
                        shuffle_mines()
                self.clicked = True
                self.label.config(relief=clickedstyle, bg=clickedcolor)
                if self.ismine():
                    avatar.config(image=dead)
                    unbind_tiles()
                    for r, c in map(lambda b: (b // sz, b % sz), mines):
                        tiles[r][c].label.configure(fg="black", bg="red")
                        if not tiles[r][c].flagged:
                            tiles[r][c].text.set("*")
                else:
                    self.checkneighbors()

    def right_click(self, event=None):
        global first_click
        if not self.clicked and self.inside(event.x, event.y) and not first_click:
            if self.flagged:
                if self.text.get() == "!":
                    self.text.set("?")
                    self.label.config(fg="black")
                else:
                    self.text.set(" ")
                    self.flagged = False
            else:
                self.text.set("!")
                self.label.config(fg="red")
                self.flagged = True


def unbind_tiles():
    for row in range(sz):
        for col in range(sz):
            tiles[row][col].label.unbind("<ButtonRelease-1>")
            tiles[row][col].label.unbind("<ButtonRelease-2>")
            tiles[row][col].label.unbind("<ButtonRelease-3>")
            tiles[row][col].label.unbind("<Button-1>")

def shuffle_mines():
    # A random 1D set of mines maps to the 2D tile grid.
    # These are managed independently of individual tiles, 
    # with thes self.ismine() function used for lookup.
    mines.clear()
    while len(mines) < b:
        mines.add(random.randint(0,sz**2-1))

def restart_game(event=None):
    global first_click
    global tiles_left
    # Reset Avatar
    avatar.config(image=fine)

    tiles_left = sz**2 - b
    first_click = True 
    shuffle_mines()

    # Reset tile config and binding 
    for row in range(sz):
        for col in range(sz):
            cur = tiles[row][col]
            cur.text.set(" ")
            cur.label.config(fg="red", relief=unclickedstyle, bg=unclickedcolor)
            cur.neighbormines = -1
            cur.flagged = False
            cur.clicked = False
            cur.label.bind("<ButtonRelease-1>", cur.left_click)
            cur.label.bind("<Button-1>", cur.anticipate)
            cur.label.bind("<ButtonRelease-2>", cur.right_click)
            cur.label.bind("<ButtonRelease-3>", cur.right_click)

    
# Size and number of mines, to be replaced with parseargs
sz = 20 
b = 60 

# Color and style config
clickedstyle="sunken"
clickedcolor="gray80"
unclickedstyle="raised"
unclickedcolor="gray65"
font="consolas 10 bold"
numcolor = {1:"blue", 2:"green", 3:"red", 4:"purple", 5:"yellow", 6:"turquoise3", 7:"black", 8:"lightskyblue4"}
first_click = True
tiles_left = sz**2 - b

# Frame setup
root = tk.Tk()
root.title("Minesweeper")
icon = tk.PhotoImage(file="bomb.png")
root.iconphoto(False, icon)
frame = tk.Frame(root)
frame.pack(side="bottom")
status = tk.Frame(root, bd = 4)
status.pack(fill='x')

tiles = [[] for _ in range(sz)]
mines = set()

# Create the tile grid
for row in range(sz):
    for col in range(sz):
        cur_tile = Tile(row, col)
        cur_tile.label.grid(row=row, column=col)
        tiles[row].append(cur_tile)

# Load images
fine = tk.PhotoImage(file="fine.gif")
dead = tk.PhotoImage(file="dead.gif")
anticipate = tk.PhotoImage(file="anticipate.gif")
win = tk.PhotoImage(file="win.gif")

# Bind avatar to restart
clock = tk.Label(status, text=" 00:00:00 ", font="courier 14 bold")
clock.pack(side="left", expand=True)
avatar = tk.Label(status, image=fine)
avatar.pack(side="left", expand=True)
avatar.bind('<Button-1>', restart_game)
counter = tk.Label(status, text="Mines: 000", font="courier 14 bold")
counter.pack(side="left",expand=True)


restart_game()
root.mainloop()
