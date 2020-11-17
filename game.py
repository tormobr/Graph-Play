import random
import math
import time
from collections import deque
import random
import os
import pygame
import numpy as np


# some colors
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (10,100,100)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
LIGHTGRAY = (150,150,150)
PURPLE = (128,0,128)
ORANGE = (255,128,0)
DARK_SOMETHING = (76,0,153)


# Set video to center
os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()

# Class represention a square in the grid
class Node():
    def __init__(self, x, y, dim, value):
        self.x = x
        self.y = y
        self.dim = dim
        self.value = value
        self.rect = pygame.Rect(x*dim, y*dim, dim-1, dim-1)
    
    def __str__(self):
        return f"{self.x}, {self.y}"

    def __repr__(self):
        return self.__str__()
        
    # Sets the color of node
    def update_value(self, color):
        self.value = color

# The main class with the game
class Game():
    def __init__(self):
        self.screen_w = 1300
        self.block_size = 20
        self.w = 800 + self.block_size
        self.h = 800 + self.block_size
        self.nodes = self.create_nodes()
        self.start = self.nodes[1][1]
        self.end = self.nodes[-2][-2]
        self.mouse_is_down = False
        self.h_factor = 1
        self.steps = 0
        self.h_function = 0
        self.h_strings = ["Manhatten", "Euclidian"]
        self.fill_val = BLACK

        # Setup for pygame
        pygame.display.set_caption("Algo Tester")
        self.screen = pygame.display.set_mode((self.screen_w, self.h))
        pygame.font.init()
        self.font_title = pygame.font.SysFont("ubuntumono", 30)
        self.font_par = pygame.font.SysFont("ubuntumono", 18)
        self.clock = pygame.time.Clock()

    # Draws all the menu text on the screen
    def draw_text(self):
        instructions = self.font_title.render(f"Intructions:", True, BLACK)
        self.screen.blit(instructions, (self.w + 15, 55))
        a = self.font_par.render(f"Press: 'a' for A*", True, BLACK)
        b = self.font_par.render(f"Press: 'b' for Breath-First", True, BLACK)
        d = self.font_par.render(f"Press: 'd' for Depth-First", True, BLACK)
        p = self.font_par.render(f"Press: 'p' for Maze-gen with Prim", True, BLACK)
        s = self.font_par.render(f"Press: 's' to set start", True, BLACK)
        e = self.font_par.render(f"Press: 'e' to set end", True, BLACK)
        r = self.font_par.render(f"Press: 'r' to reset drawing", True, BLACK)
        u = self.font_par.render(f"Press: 'key UP' to increase heuristic", True, BLACK)
        do = self.font_par.render(f"Press: 'key DOWN' to decrease heuristic", True, BLACK)
        mouse = self.font_par.render(f"press 'Left Mouse' to draw", True, BLACK)
        mouse_right = self.font_par.render(f"press 'Right Mouse' to clear", True, BLACK)
        scroll = self.font_par.render(f"Press 'Scroll' to change Square Size", True, BLACK)
        h = self.font_par.render(f"Press: 'h' to change heuristic func", True, BLACK)
        ins = [a, b, d, p, s, e, r, u, do, scroll, h, mouse, mouse_right]
        for i, t in enumerate(ins):
            self.screen.blit(t, (self.w + 35, 30*(i+3)))

        BS = self.font_title.render(f"Square Size: {self.block_size}", True, BLACK)
        steps = self.font_title.render(f"Nodes Visited: {self.steps}", True, BLACK)
        h_func = self.font_title.render(f"Heuristic Function: {self.h_strings[self.h_function]}", True, BLACK)
        heuristic = self.font_title.render(f"Heuristic Factor: {round(self.h_factor, 2)}", True, BLACK)
        TITLES = [BS, steps, h_func, heuristic]
        for i, t in enumerate(TITLES):
            self.screen.blit(t, (self.w + 15, self.h - 60*(i+1)))

    # Function for handling zooming in and out of grid
    def zoom(self, v):
        self.block_size += v
        self.nodes = self.create_nodes()
        self.start = self.nodes[1][1]
        self.end = self.nodes[-2][-2]
    
    # Creates the data-structures
    def create_nodes(self):
        ret = []
        for y in range(self.h // self.block_size):
            tmp = []
            for x in range(self.w // self.block_size):
                val = WHITE
                if x == 0 or x == self.w // self.block_size -1 or y == 0 or y == self.h // self.block_size -1:
                    val = PURPLE
                new = Node(x, y, self.block_size, val)
                tmp.append(new)
            ret.append(tmp)
        return ret

    # Draw each node on the screen
    def draw_nodes(self):
        self.start.update_value(RED)
        self.end.update_value(GREEN)
        for row in self.nodes:
            for n in row:
                pygame.draw.rect(self.screen, n.value, n.rect)

    # Checks the colision between mouse position and nodes
    def check_collision(self, pos, v):
        x, y = pos
        if x < 0 + self.block_size or x > (self.w - self.block_size)-1:
            return
        if y < 0 + self.block_size or y > (self.h - self.block_size)-1:
            return
        # Get the node pressed
        n = self.nodes[y//self.block_size][x//self.block_size]
        n.update_value(v)

        # If start node
        if v == RED:
            self.start.update_value(WHITE)
            self.start = n

        # Id end node
        if v == GREEN:
            self.end.update_value(WHITE)
            self.end = n

    # Backtracks a path, and applies nice gradient color
    def backtrack(self, path):
        for i, n in enumerate(reversed(path)):
            fac = 255 // len(path) +1
            n.update_value((min(i*fac, 255),max(255-(i*fac), 0),0))
            self.update_screen(300)

    # Update the pygame screen
    def update_screen(self, ticks=200):
        # Draw the basic layout of screen
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, ORANGE, (self.w, 0, self.screen_w - self.w, self.h))
        pygame.draw.rect(self.screen, WHITE, (self.w+10, 10, self.screen_w - self.w - 20, self.h -20 ))

        # Draw the squares and text on screen
        self.draw_nodes()
        self.draw_text()

        # Tick clock and update screen
        self.clock.tick(ticks)
        pygame.display.flip()

    # breath first search (and DFS)
    def bfs(self, dfs=False):
        self.steps = 0
        self.reset(keep_drawing=True)

        # Init the queue and visisted set
        q = deque([(self.start, [])])
        visited = set()

        # While queue in not emptu
        while q:
            # Get the first in queue and check if visited
            current, path = q.popleft()
            if current in visited:
                continue
            visited.add(current)
            self.steps += 1

            # If the goal is reached
            if current == self.end:
                self.backtrack(path)
                print(len(path))
                return
            
            # Get all neighbors of current cell
            for n in self.get_neighbors(current):
                new_path = path.copy()
                new_path.append(current)
                if n in visited:
                    continue

                # If DFS prepend, to explore depth first (kinda hacky solution)
                if dfs:
                    q.appendleft((n, new_path))
                else:
                    q.append((n, new_path))

                n.update_value(DARK_SOMETHING)

            # Speeds up the stuff
            if self.steps % int(1/self.block_size * 100) == 0:
                self.update_screen(ticks=400)

            current.update_value(LIGHTGRAY)

    # Flips the heuristic function between the options
    def change_heuristic(self):
        self.h_function = (self.h_function + 1) % 2

    # Heuristic function for A*
    def manhatten(self, n):
        # Find the delta x and y
        dx = abs(n.x - self.end.x)
        dy = abs(n.y - self.end.y)

        # Manhatten
        if self.h_function == 0:
            ret = (dx + dy)

        # Euclidian
        elif self.h_function == 1:
            ret = math.sqrt(dx**2 + dy**2)

        return ret * self.h_factor


    # A* path finding
    def astar(self):
        self.steps = 0
        self.reset(keep_drawing=True)
        q = [(self.start, [], 0)]
        visited = set()

        while q:
            if not self.handle_events():
                return
            # Should change this to use heapq.. TODO
            q = sorted(q, key=lambda x: x[2] + self.manhatten(x[0]))
            current, path, g = q.pop(0)
            if current in visited:
                continue
            visited.add(current)
            self.steps += 1

            if current == self.end:
                self.backtrack(path)
                print(len(path))
                return
            
            for n in self.get_neighbors(current):
                new_path = path.copy()
                new_path.append(current)
                if n in visited:
                    continue
                q.append((n, new_path, g+1))
                n.update_value(DARK_SOMETHING)

            if not self.handle_events():
                return
            # Speeds up the stuff
            if self.steps % int(1/self.block_size * 100) == 0:
                self.update_screen(ticks=400)
            current.update_value(LIGHTGRAY)

    # Gets all the neighbors of a node. Can specify jmp lenngth
    def get_neighbors(self, n, rand=False, exclude_vals=[BLACK, PURPLE], jmp=1):
        # Directions to find neighbors
        dirs = [(1,0), (0,-1), (-1,0), (0,1)]
        ret = []
        for dx, dy in dirs:
            new_y = n.y + dy*jmp
            new_x = n.x + dx*jmp

            # Check out of bounds
            if new_x < 0 or new_x >= self.w // self.block_size:
                continue
            elif new_y < 0 or new_y >= self.h // self.block_size:
                continue

            # get the new cell from list based on index
            new = self.nodes[new_y][new_x]
            if new.value not in exclude_vals:
                ret.append(new)

        return ret

    # Removes all drawings from screen
    def reset(self, keep_drawing=False):
        keep_vals = [WHITE, PURPLE]     # Keep these colors
        if keep_drawing: keep_vals.append(BLACK)
        for row in self.nodes:
            for n in row:
                if n.value not in keep_vals:
                    n.update_value(WHITE)

    # Uses prims minimal span tree algo to create maze
    def prim(self):
        self.steps = 0
        for row in self.nodes[1:-1]:
            for n in row[1:-1]:
                n.update_value(BLACK)
        
        self.update_screen(ticks=200)
        
        # Init wall queue with neighbors of start cell
        walls = self.get_neighbors(self.start, exclude_vals=[WHITE, PURPLE, RED], jmp=2)
        visited = set()

        # While walls in queue
        while walls:
            if not self.handle_events():
                return

            # Randomly select a wall
            random.shuffle(walls)
            current = walls.pop(0)

            # If wall visited, return
            if current in visited:
                continue
            visited.add(current)
            self.steps += 1
              
            # Get a random open cell and create a path to it
            connections  = self.get_neighbors(current, exclude_vals=[BLACK, PURPLE, GREEN], jmp=2)
            node = random.choice(connections)
            avgx = (current.x + node.x) // 2
            avgy = (current.y + node.y) // 2
            current.update_value(WHITE)
            self.nodes[avgy][avgx].update_value(WHITE)

            # Find new walls from current cell
            frontiers = self.get_neighbors(current, exclude_vals=[WHITE, PURPLE], jmp=2)
            for n in frontiers:
                if n.value != WHITE and n not in visited:
                    walls.append(n)

            # Speeds up the animation
            if self.steps % int(1/self.block_size * 100) == 0:
                self.update_screen(ticks=400)


    # Main loop while game active
    def play(self):
        while True:
            # Handle all pygame events
            if not self.handle_events():
                return

            # If drawing
            if self.mouse_is_down:
                pos = pygame.mouse.get_pos()
                self.check_collision(pos, self.fill_val) 
                    

            self.update_screen(ticks=300)

    # Handle events in pygame
    def handle_events(self):
        # Handle events
        for e in pygame.event.get():
            # click exit
            if e.type == pygame.QUIT:
                return 0
            # handle keydown events
            if e.type == pygame.KEYDOWN:
                # Exit if escape is pressed
                if e.key == pygame.K_ESCAPE:
                    return 0
                # Set start
                if e.key == pygame.K_s:
                    pos = pygame.mouse.get_pos()
                    self.check_collision(pos, RED)
                # Set end
                if e.key == pygame.K_e:
                    pos = pygame.mouse.get_pos()
                    self.check_collision(pos, GREEN)
                # BFS
                if e.key == pygame.K_b:
                    self.bfs()
                # DFS
                if e.key == pygame.K_d:
                    self.bfs(dfs=True)
                # A*
                if e.key == pygame.K_a:
                    self.astar()
                # reset board
                if e.key == pygame.K_r:
                    self.reset()
                # Create maze with prims algo
                if e.key == pygame.K_p:
                    self.prim()
                # decrese heuristics
                if e.key == pygame.K_DOWN:
                    self.h_factor -= .01
                # increase heuristics
                if e.key == pygame.K_UP:
                    self.h_factor += .01
                # Change heuristic function
                if e.key == pygame.K_h:
                    self.change_heuristic()
            # If mouse event.. Drawing and zooming
            if e.type == pygame.MOUSEBUTTONDOWN:
                # Right click mouse
                if e.button == 3:
                    self.fill_val = WHITE
                    self.mouse_is_down = True
                # Left click mouse
                elif e.button == 1:
                    self.fill_val = BLACK
                    self.mouse_is_down = True
                # Scroll up
                elif e.button == 4:
                    if self.block_size < 100:
                        self.zoom(1)
                # Scroll down
                elif e.button == 5:
                    if self.block_size > 5:
                        self.zoom(-1)

            # Disables drawing mode
            if e.type == pygame.MOUSEBUTTONUP:
                self.mouse_is_down = False

        # If not exit return 1
        return 1

# Play the *game*
if __name__ == "__main__":
    g = Game()
    g.play()
