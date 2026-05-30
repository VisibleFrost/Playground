from pydantic import BaseModel, Field

class MazeRequest(BaseModel):
    width: int = Field(15, ge=5, le=1000, description="Ширина лабиринта")
    height: int = Field(15, ge=5, le=1000, description="Высота лабиринта")