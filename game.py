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
        self.fill_val = BLACK
    
    def __str__(self):
        return f"{self.x}, {self.y}"

    def __repr__(self):
        return f"({self.x},{self.y})"
        
    def update_value(self, color):
        self.value = color

class Game():
    def __init__(self):
        self.w = 820
        self.h = 820
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
                val = WHITE
                if x == 0 or x == self.w // self.block_size -1 or y == 0 or y == self.h // self.block_size -1:
                    val = GRAY
                new = Node(x, y, self.block_size, val)
                tmp.append(new)
            ret.append(tmp)
        return ret

    def draw_nodes(self):
        self.start.update_value(RED)
        self.end.update_value(GREEN)
        for row in self.nodes:
            for n in row:
                pygame.draw.rect(self.screen, n.value, n.rect)

    def check_collision(self, pos, v):
        x, y = pos
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

    def backtrack(self, path):
        for n in reversed(path):
            n.update_value(PURPLE)
            self.update_screen(30)

    def update_screen(self, ticks=200):
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
                n.update_value(BLUE)

            self.update_screen(ticks=300)
            current.update_value(YELLOW)

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
                n.update_value(BLUE)

            self.update_screen(ticks=300)
            current.update_value(YELLOW)

    def get_neighbors(self, n, rand=False, exclude_vals=[BLACK, GRAY], dig=False, jmp=1):
        dirs = [(1,0), (0,-1), (-1,0), (0,1)]
        if dig:
            dirs.append((1,1))
            dirs.append((-1,-1))
        ret = []
        x, y = n.x, n.y
        for dx, dy in dirs:
            new_y = y + dy*jmp
            new_x = x + dx*jmp
            if new_x < 0 or new_x >= self.w // self.block_size:
                continue
            elif new_y < 0 or new_y >= self.h // self.block_size:
                continue
            new = self.nodes[new_y][new_x]
            if new.value not in exclude_vals:
                ret.append(new)
        return ret

    def reset(self, keep_drawing=False):
        keep_vals = [WHITE, GRAY]
        if keep_drawing: keep_vals.append(BLACK)
        for row in self.nodes:
            for n in row:
                if n.value not in keep_vals:
                    n.update_value(WHITE)

    # Draw as somewhat ok grid
    def prim(self):
        for row in self.nodes[1:-1]:
            for n in row[1:-1]:
                n.update_value(BLACK)
        
        self.update_screen(ticks=2)
        middle_node = self.nodes[len(self.nodes) // 2][len(self.nodes) // 2]
        #middle_node.update_value(WHITE)
        walls = self.get_neighbors(self.start, exclude_vals=[WHITE, GRAY, RED], jmp=2)
        print(walls)
        visited = set()
        while walls:
            random.shuffle(walls)
            current = walls.pop(0)
            print(current)
            if current in visited:
                continue
            visited.add(current)
              
            connections  = self.get_neighbors(current, exclude_vals=[BLACK, GRAY, GREEN], jmp=2)
            print(connections)
            node = random.choice(connections)
            avgx = (current.x + node.x) // 2
            avgy = (current.y + node.y) // 2

            current.update_value(WHITE)
            self.nodes[avgy][avgx].update_value(WHITE)

            frontiers = self.get_neighbors(current, exclude_vals=[WHITE, GRAY], jmp=2)
            for n in frontiers:
                print(n)
                self.update_screen(ticks=200)
                if n.value != WHITE and n not in visited:
                    walls.append(n)
            #print(current)

            """
            current.update_value(WHITE) 
            news = self.get_neighbors(current, exclude_vals=[WHITE, GRAY, RED, GREEN])
            walls.extend(news)
            dx = current.x - n.x
            dy = current.y - n.y
            """


    # Main loop while game active
    def play(self):
        while True:
            if not self.handle_events():
                return
            if self.mouse_is_down:
                pos = pygame.mouse.get_pos()
                self.check_collision(pos, self.fill_val) 
                    

            self.update_screen(ticks=300)

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
                    self.h_factor -= .1
                    self.text = self.font.render(f"Heuristic: {self.h_factor}", False, WHITE)
                # increase heuristics
                if e.key == pygame.K_UP:
                    self.h_factor += .1
                    self.text = self.font.render(f"Heuristic: {self.h_factor}", False, WHITE)
            if e.type == pygame.MOUSEBUTTONDOWN:
                self.fill_val = WHITE if e.button == 3 else BLACK
                self.mouse_is_down = True
            if e.type == pygame.MOUSEBUTTONUP:
                self.mouse_is_down = False
        return 1

if __name__ == "__main__":
    g = Game()
    g.play()
