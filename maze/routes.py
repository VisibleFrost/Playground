import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from .logic import MazeGame
from .models import MazeRequest 

active_maze_tasks = {}

router = APIRouter(prefix="/maze", tags=["Maze"])

@router.post("/")
async def create_maze(data: MazeRequest):
    task_key = "current_generation"

    if task_key in active_maze_tasks:
        old_task = active_maze_tasks[task_key]
        if not old_task.done():
            old_task.cancel()
            await asyncio.sleep(0)

    maze_game = MazeGame(data.width, data.height)
    maze_game.generate()

    queue = asyncio.Queue()

    async def run_generation():
        try:
            async for chunk in maze_game.solve_stream():
                await queue.put(chunk)
        except asyncio.CancelledError:
            raise
        finally:
            await queue.put(None)
            if active_maze_tasks.get(task_key) == asyncio.current_task():
                active_maze_tasks.pop(task_key, None)

    gen_task = asyncio.create_task(run_generation())
    active_maze_tasks[task_key] = gen_task

    async def queue_reader():
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk

    return StreamingResponse(queue_reader(), media_type="text/event-stream")