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
    6: PURPLE
}

os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()



class Node():
    def __init__(self, x, y, dim, value):
        self.x = x
        self.y = y
        self.dim = dim
        self.value = value
        self.rect = pygame.Rect(x, y, dim, dim)
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

        pygame.display.set_caption("Algo Tester")
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()

    def create_nodes(self):
        ret = []
        for y in range(0, self.h, self.block_size):
            tmp = []
            for x in range(0, self.w, self.block_size):
                val = 1
                if x == 0 or x == self.w-self.block_size or y == 0 or y == self.h-self.block_size:
                    val = 0
                new = Node(x, y, self.block_size-1, val)
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
        self.clock.tick(ticks)
        pygame.display.flip()

    def bfs(self, dfs=False):
        self.reset()
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

            self.update_screen(200)
            current.update_value(5)

    def manhatten(self, n):
        return math.sqrt(abs(self.end.x - n.x)**2 + abs(self.end.y - n.y)**2)

    def astar(self):
        self.reset()
        q = [(self.start, [], 0)]
        visited = set()

        while q:
            q = sorted(q, key=lambda x: x[2] + self.manhatten(x[0]))
            current, path, f = q.pop(0)
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

            self.update_screen(200)
            current.update_value(5)

    def get_neighbors(self, n):
        dirs = [(0,1), (0,-1), (1,0), (-1,0)]
        ret = []
        x, y = n.x // self.block_size, n.y // self.block_size
        for dx, dy in dirs:
            new_y = y + dy
            new_x = x + dx
            new = self.nodes[new_y][new_x]
            if new.value != 0:
                ret.append(new)

        return ret

    def reset(self):
        for row in self.nodes:
            for n in row:
                if n.value != 0 and n.value != 1:
                    n.update_value(1)
    
    def play(self):
        while True:
            if not self.handle_events():
                return
            if self.mouse_is_down:
                pos = pygame.mouse.get_pos()
                self.check_collision(pos, self.fill_val) 
                    

            self.update_screen(200)

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
                if e.key == pygame.K_s:
                    pos = pygame.mouse.get_pos()
                    self.check_collision(pos, 2)
                if e.key == pygame.K_e:
                    pos = pygame.mouse.get_pos()
                    self.check_collision(pos, 3)
                if e.key == pygame.K_b:
                    self.bfs()
                if e.key == pygame.K_d:
                    self.bfs(dfs=True)
                if e.key == pygame.K_a:
                    self.astar()
                if e.key == pygame.K_r:
                    self.reset()
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.fill_val = 1 if e.button == 3 else 0
                self.mouse_is_down = True
            if e.type == pygame.MOUSEBUTTONUP:
                self.mouse_is_down = False
        return 1

if __name__ == "__main__":
    g = Game()
    g.play()
