from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Task:
    id: str
    text: str
    completed: bool
    created_date: int
    completed_date: Optional[int] = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Task":
        return cls(
            id=data["id"],
            text=data["text"],
            completed=data["completed"],
            created_date=data["createdDate"],
            completed_date=data.get("completedDate"),
        )
