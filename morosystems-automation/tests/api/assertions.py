from typing import Any, Optional
from playwright.sync_api import APIResponse
from api.models import Task
from api.todo_client import TodoApiClient

TASK_FIELD_TYPES = {"id": str, "text": str, "completed": bool, "createdDate": int, "completedDate": int}
TASK_REQUIRED_FIELDS = {"id", "text", "completed", "createdDate"}

def assert_task_shape(body: Any) -> None:
    assert isinstance(body, dict), f"Task must be a JSON object, got {body!r}"

    missing = TASK_REQUIRED_FIELDS - body.keys()
    assert not missing, f"Required fields missing: {sorted(missing)}"

    unexpected = body.keys() - TASK_FIELD_TYPES.keys()
    assert not unexpected, f"Undocumented fields: {sorted(unexpected)}"

    for field, value in body.items():
        expected_type = TASK_FIELD_TYPES[field]
        assert type(value) is expected_type, f"{field!r} should be {expected_type.__name__}, got {value!r}"

def assert_response(response: APIResponse, status: int, text: Optional[str] = None) -> None:
    assert response.status == status, f"Expected {status}, got {response.status}: {response.text()}"
    if text is not None:
        assert response.text() == text

def _stored_tasks(todo_api: TodoApiClient) -> list[Task]:
    response = todo_api.get_tasks()
    assert_response(response, 200)
    return [Task.from_json(item) for item in response.json()]

def assert_task_stored(todo_api: TodoApiClient, task: Task) -> None:
    assert task in _stored_tasks(todo_api), f"Task not stored as expected: {task}"

def assert_task_not_stored(todo_api: TodoApiClient, task_id: str) -> None:
    assert task_id not in [t.id for t in _stored_tasks(todo_api)], f"Task {task_id} is still stored"
