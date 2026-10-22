"""Jednoduché ukázkové API pro správu úkolů (TODO) postavené na FastAPI."""
from itertools import count
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="Todo API", version="1.0.0", description="Ukázkové CRUD API")


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, examples=["Napsat testy"])
    description: Optional[str] = Field(None, max_length=500)
    done: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    done: Optional[bool] = None


class Task(TaskCreate):
    id: int


# Jednoduché úložiště v paměti (pro demo stačí)
_db: Dict[int, Task] = {}
_ids = count(1)


def reset_db() -> None:
    """Vyčistí úložiště – používá se v testech."""
    global _ids
    _db.clear()
    _ids = count(1)


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/tasks", response_model=List[Task], tags=["tasks"])
def list_tasks(done: Optional[bool] = None) -> List[Task]:
    tasks = list(_db.values())
    if done is not None:
        tasks = [t for t in tasks if t.done == done]
    return tasks


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> Task:
    task = Task(id=next(_ids), **payload.model_dump())
    _db[task.id] = task
    return task


def _get_or_404(task_id: int) -> Task:
    task = _db.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.get("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def get_task(task_id: int) -> Task:
    return _get_or_404(task_id)


@app.patch("/tasks/{task_id}", response_model=Task, tags=["tasks"])
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    task = _get_or_404(task_id)
    updated = task.model_copy(update=payload.model_dump(exclude_unset=True))
    _db[task_id] = updated
    return updated


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int) -> Response:
    _get_or_404(task_id)
    del _db[task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
