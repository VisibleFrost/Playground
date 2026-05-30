from collections import deque
import random
import asyncio
import json
import os

class MazeGame:
    def __init__(self, width: int, height: int):
        self.width = width if width % 2 != 0 else width + 1
        self.height = height if height % 2 != 0 else height + 1
        self.grid = [[1] * self.width for _ in range(self.height)]
    
    def generate(self):
        stack = [(1, 1)]
        self.grid[1][1] = 0
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nx, ny = cx + dx, cy + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1 and self.grid[ny][nx] == 1:
                    neighbors.append((nx, ny, dx, dy))
            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                self.grid[cy + dy // 2][cx + dx // 2] = 0
                self.grid[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        self.grid[1][0] = 0
        self.grid[self.height - 2][self.width - 1] = 0

    async def solve_stream(self):
        start = (0, 1)
        end = (self.width - 1, self.height - 2)
        queue = deque([start])
        parent = {start: None}
        visited = {start}

        while queue:
            curr = queue.popleft()
            if curr == end:
                break
            cx, cy = curr
            for dx, dy in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.grid[ny][nx] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = curr
                        queue.append((nx, ny))

        curr = end
        path = []
        while curr:
            path.append(curr)
            curr = parent.get(curr)
        path.reverse()

        total_time = 3.0
        delay = total_time / len(path) if path else 0.01

        yield json.dumps({"matrix": self.grid, "status": "start"}) + "\n"
        await asyncio.sleep(delay)

        for x, y in path:
            self.grid[y][x] = 2
            yield json.dumps({"step": [x, y], "status": "progress"}) + "\n"
            await asyncio.sleep(delay)

        yield json.dumps({"status": "done"}) + "\n"