import random
import math
import time
from collections import deque
import random
import os
import pygame
import numpy as np


SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (10,100,100)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (0,255,255)
PURPLE = (255,0,255)

COLORS = {
    0: BLACK,
    1: WHITE,
    2: RED,
    3: GREEN,
    4: BLUE,
    5: YELLOW,
    6: PURPLE,
    7: GRAY
}

os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()



class Node():
    def __init__(self, x, y, dim, value):
        self.x = x
        self.y = y
        self.dim = dim
        self.value = value
        self.rect = pygame.Rect(x*dim, y*dim, dim-1, dim-1)
        self.color = COLORS[value]
        self.fill_val = 0
    
    def __str__(self):
        return f"{self.x}, {self.y}"

    def __repr__(self):
        return f"({self.x},{self.y})"
        
    def update_value(self, x):
        self.value = x
        self.color = COLORS[x]

class Game():
    def __init__(self):
        self.w = 800
        self.h = 800
        self.block_size = 20
        self.nodes = self.create_nodes()
        self.start = self.nodes[1][1]
        self.end = self.nodes[-2][-2]
        self.mouse_is_down = False
        self.h_factor = 1

        pygame.display.set_caption("Algo Tester")
        self.screen = pygame.display.set_mode((self.w, self.h))
        pygame.font.init()
        self.font = pygame.font.SysFont("Comic Sans MS", 30)
        self.clock = pygame.time.Clock()
        self.text = self.font.render(f"Heuristic: {self.h_factor}", False, WHITE)

    def create_nodes(self):
        ret = []
        for y in range(self.h // self.block_size):
            tmp = []
            for x in range(self.w // self.block_size):
                val = 1
                if x == 0 or x == self.w // self.block_size -1 or y == 0 or y == self.h // self.block_size -1:
                    val = 7
                new = Node(x, y, self.block_size, val)
                tmp.append(new)
            ret.append(tmp)
        return ret

    def draw_nodes(self):
        self.start.update_value(2)
        self.end.update_value(3)
        for row in self.nodes:
            for n in row:
                pygame.draw.rect(self.screen, n.color, n.rect)

    def check_collision(self, pos, v):
        x, y = pos
        # Get the node pressed
        n = self.nodes[y//self.block_size][x//self.block_size]
        n.update_value(v)

        # If start node
        if v == 2:
            self.start.update_value(1)
            self.start = n

        # Id end node
        if v == 3:
            self.end.update_value(1)
            self.end = n

    def backtrack(self, path):
        for n in reversed(path):
            n.update_value(6)
            self.update_screen(30)

    def update_screen(self, ticks):
        self.screen.fill(BLACK)
        self.draw_nodes()
        self.screen.blit(self.text,(self.w//2,0))
        self.clock.tick(ticks)
        pygame.display.flip()

    def bfs(self, dfs=False):
        self.reset(keep_drawing=True)
        q = deque([(self.start, [])])
        visited = set()

        while q:
            current, path = q.popleft()
            if current in visited:
                continue
            visited.add(current)
            if current == self.end:
                self.backtrack(path)
                print(len(path))
                return
            
            for n in self.get_neighbors(current):
                new_path = path.copy()
                new_path.append(current)
                if n in visited:
                    continue
                if dfs:
                    q.appendleft((n, new_path))
                else:
                    q.append((n, new_path))
                n.update_value(4)

            self.update_screen(300)
            current.update_value(5)

    def manhatten(self, n):
        dx = abs(n.x - self.end.x)
        dy = abs(n.y - self.end.y)
        ret = math.sqrt(dx**2 + dy**2)
        return ret * self.h_factor

    def sort_astar(self, q):
        current, path, f_score = q[0]
        best = f_score + self.manhatten(current)
        for n, p, f in q[1:]:
            new_score = f + self.manhatten(n)
            if new_score < best:
                current = n 
                path = p 
                f_score = f
                best = new_score
        q.remove((current, path, f_score))
        return (current, path, f_score)
        

    def astar(self):
        self.reset(keep_drawing=True)
        q = [(self.start, [], 0)]
        visited = set()

        while q:
            current, path, f = self.sort_astar(q)
            if current in visited:
                continue
            visited.add(current)
            if current == self.end:
                self.backtrack(path)
                print(len(path))
                return
            
            for n in self.get_neighbors(current):
                new_path = path.copy()
                new_path.append(current)
                if n in visited:
                    continue
                q.append((n, new_path, f+1))
                n.update_value(4)

            self.update_screen(300)
            current.update_value(5)

    def get_neighbors(self, n, rand=False, exclude_vals=[0,7], dig=False):
        dirs = [(1,0), (0,-1), (-1,0), (0,1)]
        if dig:
            dirs.append((1,1))
            dirs.append((-1,-1))
        ret = []
        x, y = n.x, n.y
        for dx, dy in dirs:
            new_y = y + dy
            new_x = x + dx
            new = self.nodes[new_y][new_x]
            if new.value not in exclude_vals:
                ret.append(new)
        return ret

    def reset(self, keep_drawing=False):
        keep_vals = [1, 7]
        if keep_drawing: keep_vals.append(0)
        for row in self.nodes:
            for n in row:
                if n.value not in keep_vals:
                    n.update_value(1)

    # Draw as somewhat ok grid
    def prim(self):
        for row in self.nodes[1:-1]:
            for n in row[1:-1]:
                n.update_value(0)
        
        self.update_screen(2)
        walls = self.get_neighbors(self.start, exclude_vals=[1, 7, 2])
        visited = set()
        while walls:
            random.shuffle(walls)
            current = walls.pop(0)
            if current in visited:
                continue
            visited.add(current)
            #current.update_value(1)
            neighbors = self.get_neighbors(current, exclude_vals=[0, 7, 3])
            print(current)
            print(neighbors)
            if len(neighbors) == 1:
                print("this happens")
                n = neighbors[0]
                if n.value != 0:
                    current.update_value(1) 
                else: continue
                news = self.get_neighbors(current, exclude_vals=[1,7,2])
                walls.extend(news)
                self.update_screen(200)



    # Main loop while game active
    def play(self):
        while True:
            if not self.handle_events():
                return
            if self.mouse_is_down:
                pos = pygame.mouse.get_pos()
                self.check_collision(pos, self.fill_val) 
                    

            self.update_screen(300)

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
                    self.check_collision(pos, 2)
                # Set end
                if e.key == pygame.K_e:
                    pos = pygame.mouse.get_pos()
                    self.check_collision(pos, 3)
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
                    self.h_factor -= .1
                    self.text = self.font.render(f"Heuristic: {self.h_factor}", False, WHITE)
                # increase heuristics
                if e.key == pygame.K_UP:
                    self.h_factor += .1
                    self.text = self.font.render(f"Heuristic: {self.h_factor}", False, WHITE)
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.fill_val = 1 if e.button == 3 else 0
                self.mouse_is_down = True
            if e.type == pygame.MOUSEBUTTONUP:
                self.mouse_is_down = False
        return 1

if __name__ == "__main__":
    g = Game()
    g.play()
