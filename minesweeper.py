import argparse
import random
import time

import tkinter as tk
from itertools import product
from collections import deque
from PIL import ImageTk, Image

class GameState:
    # Color and style config
    clickedstyle="sunken"
    clickedcolor="gray80"
    unclickedstyle="raised"
    unclickedcolor="gray65"
    font="consolas 10 bold"
    numcolor = {
                1:"blue", 
                2:"green", 
                3:"red", 
                4:"purple", 
                5:"yellow", 
                6:"turquoise3", 
                7:"black", 
                8:"lightskyblue4"
               }

    def __init__(self, sz=20, m=20):
        self.first_click = True
        self.tiles_left = sz**2 - m
        self.start_time = time.time()
        self.time_mine_font = "courier 14 bold"
        self.size = sz
        self.m = m

        # Set up Frames
        self.root = tk.Tk()
        self.root.title("Minesweeper")
        self.root.iconphoto(False, tk.PhotoImage(file="bomb.png"))
        self.grid = tk.Frame(self.root)
        self.grid.pack(side="bottom")
        self.status = tk.Frame(self.root, bd=4)
        self.status.pack(fill='x')
        
        # Load images
        self.fine = tk.PhotoImage(file="fine.gif")
        self.dead = tk.PhotoImage(file="dead.gif")
        self.anticipate = tk.PhotoImage(file="anticipate.gif")
        self.win = tk.PhotoImage(file="win.gif")

        # Bind avatar to restart
        self.clock = tk.Label(self.status, text=" 00:00:00 ", font="courier 14 bold")
        self.clock.pack(side="left", expand=True)
        self.avatar = tk.Label(self.status, image=self.fine)
        self.avatar.pack(side="left", expand=True)
        self.avatar.bind('<Button-1>', self.restart_game)
        self.counter = tk.Label(self.status, text="Mines: 000", font="courier 14 bold")
        self.counter.pack(side="left",expand=True)

        self.tiles = [[] for _ in range(self.size)]
        self.mines = set()

        # Create the tile grid
        for row in range(self.size):
            for col in range(self.size):
                cur_tile = Tile(self, row, col)
                cur_tile.label.grid(row=row, column=col)
                self.tiles[row].append(cur_tile)

        self.restart_game()
        self.root.mainloop()

    def restart_game(self, event=None):
        self.avatar.config(image=self.fine)
        self.tiles_left = self.size**2 - self.m
        self.first_click = True 
        self.start_time = time.time() 
        self.update_timer() # Need to move into this class
        self.shuffle_mines() # Need to move into this class
    
        # Reset tile config and binding 
        for row in range(self.size):
            for col in range(self.size):
                cur = self.tiles[row][col]
                cur.text.set(" ")
                cur.label.config(fg="red", relief=GameState.unclickedstyle, bg=GameState.unclickedcolor)
                cur.neighbormines = -1
                cur.flagged = False
                cur.clicked = False
                cur.label.bind("<ButtonRelease-1>", cur.left_click)
                cur.label.bind("<Button-1>", cur.anticipate)
                cur.label.bind("<ButtonRelease-2>", cur.right_click)
                cur.label.bind("<ButtonRelease-3>", cur.right_click)

    def unbind_tiles(self):
        for row in range(self.size):
            for col in range(self.size):
                self.tiles[row][col].label.unbind("<ButtonRelease-1>")
                self.tiles[row][col].label.unbind("<ButtonRelease-2>")
                self.tiles[row][col].label.unbind("<ButtonRelease-3>")
                self.tiles[row][col].label.unbind("<Button-1>")
    
    def update_timer(self):
        cur_time = round(time.time() - self.start_time)
        secs = cur_time % 60
        mins = cur_time // 60
        hrs = cur_time // 3600
        fmtime = " {:02d}:{:02d}:{:02d} "
        self.clock.config(text=fmtime.format(hrs, mins, secs))
        self.root.after(1000, self.update_timer) 
    
    def shuffle_mines(self):
        # A random 1D set of mines maps to the 2D tile grid.
        # These are managed independently of individual tiles, 
        # with thes self.ismine() function used for lookup.
        self.mines.clear()
        while len(self.mines) < self.m:
            self.mines.add(random.randint(0,self.size**2-1))
    

class Tile:
    def __init__(self, game, row, col):
        self.row = row
        self.col = col
        self.game = game
        self.neighbormines = -1
        self.flagged = False
        self.clicked = False

        self.text = tk.StringVar()
        self.text.set(" ")

        self.label = tk.Label(  game.grid, 
                                fg="red", 
                                font=GameState.font, 
                                relief=GameState.unclickedstyle, 
                                bg=GameState.unclickedcolor, 
                                bd=1, 
                                textvariable=self.text, 
                                width=2, 
                                height=1
                             )
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
        return (self.row * self.game.size + self.col) in self.game.mines

    def inbounds(self, tile, i, j):
        return (    tile.row + i >= 0 
                and tile.row + i < self.game.size 
                and tile.col + j >= 0 
                and tile.col + j < self.game.size)
    
    def checkneighbors(self):
        #global first_click
        #global tiles_left
        q = set([self])
        seen = set()
        while q:
            minecount = 0
            unclicked = set() 
            cur = q.pop()
            # Iterate through all 8 neighbors, counting mines, queueing empty tiles
            for i, j in product([-1, 0, 1], [-1, 0, 1]):
                if self.inbounds(cur, i, j):
                    t = self.game.tiles[cur.row + i][cur.col + j]
                    if t.ismine():
                        minecount += 1
                    else:
                        if not t.clicked and t.neighbormines == -1 and t not in seen:
                            unclicked.add(t)
            # If there's at least one mine, don't add unclicked to q
            if minecount > 0:
                if self.game.first_click:
                    self.game.shuffle_mines()
                    q.add(cur)
                    continue
                cur.neighbormines = minecount
                cur.text.set(cur.neighbormines)
                cur.label.config( relief=GameState.clickedstyle, 
                                  bg=GameState.clickedcolor, 
                                  fg=GameState.numcolor[cur.neighbormines] )
                cur.clicked = True
                self.game.tiles_left -= 1
                print('Num:', self.game.tiles_left)
            else:
                if not cur.flagged:
                    q.update(unclicked)
                    seen.update(unclicked)
                    cur.text.set(" ")
                    cur.clicked = True
                    cur.label.config(relief=GameState.clickedstyle, bg=GameState.clickedcolor)
                    self.game.first_click = False
                    self.game.tiles_left -= 1
                    print('Blank:', self.game.tiles_left)

            if self.game.tiles_left == 0:
                self.game.avatar.config(image=self.game.win)
                self.game.unbind_tiles()


    def inside(self, x, y):
        return x >= 0 and y >= 0 and x < self.label.winfo_width() and y < self.label.winfo_height()

    def anticipate(self, event=None):
        if not self.flagged and not self.clicked:
            self.label.config(relief=GameState.clickedstyle)
            self.game.avatar.config(image=self.game.anticipate)

    def left_click(self, event=None):
        #global first_click
        #global tiles_left
        if not self.flagged and not self.clicked:
            self.game.avatar.config(image=self.game.fine)
            self.label.config(relief=GameState.unclickedstyle)
            if self.inside(event.x, event.y):
                if self.game.first_click and self.ismine():
                    while self.ismine():
                        self.game.shuffle_mines()
                self.clicked = True
                self.label.config(relief=GameState.clickedstyle, bg=GameState.clickedcolor)
                if self.ismine():
                    self.game.avatar.config(image=self.game.dead)
                    self.game.unbind_tiles()
                    for r, c in map(lambda b: (b // self.game.size, b % self.game.size), self.game.mines):
                        self.game.tiles[r][c].label.configure(fg="black", bg="red")
                        if not self.game.tiles[r][c].flagged:
                            self.game.tiles[r][c].text.set("*")
                else:
                    self.checkneighbors()

    def right_click(self, event=None):
        #global first_click
        if not self.clicked and self.inside(event.x, event.y) and not self.game.first_click:
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

#arg parse stuff here
game = GameState()
