from typing import Callable
import pytest
from api.models import Task
from api.todo_client import TodoApiClient
from tests.api.assertions import (
    assert_response,
    assert_task_not_stored,
    assert_task_shape,
    assert_task_stored,
)

pytestmark = pytest.mark.api

def test_get_task_list(
    todo_api: TodoApiClient, create_task: Callable[..., Task]) -> None:
    task = create_task()
    response = todo_api.get_tasks()
    assert_response(response, 200)
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert isinstance(body, list)
    for item in body:
        assert_task_shape(item)
    assert task in [Task.from_json(item) for item in body]

def test_create_task(
    todo_api: TodoApiClient, unique_text: Callable[[], str], cleanup_task_ids: list[str]) -> None:
    text = unique_text()
    response = todo_api.create_task({"text": text})
    assert_response(response, 200)
    assert_task_shape(response.json())
    task = Task.from_json(response.json())
    cleanup_task_ids.append(task.id)
    assert task.id
    assert task.text == text
    assert task.completed is False
    assert task.created_date > 0
    assert task.completed_date is None
    assert_task_stored(todo_api, task)

def test_update_task_text(
    todo_api: TodoApiClient, create_task: Callable[..., Task], unique_text: Callable[[], str]) -> None:
    task = create_task()
    new_text = unique_text()
    response = todo_api.update_task(task.id, {"text": new_text})
    assert_response(response, 200)
    assert_task_shape(response.json())
    updated = Task.from_json(response.json())
    assert updated.id == task.id
    assert updated.text == new_text
    assert updated.created_date == task.created_date
    assert_task_stored(todo_api, updated)

def test_put_for_task_update(
    todo_api: TodoApiClient, create_task: Callable[..., Task]) -> None:
    task = create_task()
    response = todo_api.put_task(task.id, {"text": "changed via PUT"})
    assert_response(response, 404)
    assert_task_stored(todo_api, task)

def test_delete_task(
    todo_api: TodoApiClient, create_task: Callable[..., Task]) -> None:
    task = create_task()
    response = todo_api.delete_task(task.id)
    assert_response(response, 200)
    assert_task_not_stored(todo_api, task.id)
    second_delete = todo_api.delete_task(task.id)
    assert_response(second_delete, 404)

def test_complete_task(
    todo_api: TodoApiClient, create_task: Callable[..., Task]) -> None:
    task = create_task()
    response = todo_api.complete_task(task.id)
    assert_response(response, 200)
    assert_task_shape(response.json())
    completed = Task.from_json(response.json())
    assert completed.id == task.id
    assert completed.text == task.text
    assert completed.completed is True
    assert completed.completed_date is not None
    assert completed.completed_date >= task.created_date
    assert_task_stored(todo_api, completed)

def test_incomplete_task(
    todo_api: TodoApiClient, create_task: Callable[..., Task]) -> None:
    task = create_task()
    assert_response(todo_api.complete_task(task.id), 200)
    response = todo_api.incomplete_task(task.id)
    assert_response(response, 200)
    assert_task_shape(response.json())
    reopened = Task.from_json(response.json())
    assert reopened.id == task.id
    assert reopened.completed is False
    assert reopened.completed_date is None
    assert_task_stored(todo_api, reopened)

def test_get_completed_tasks(
    todo_api: TodoApiClient, create_task: Callable[..., Task]) -> None:
    done_task = create_task()
    open_task = create_task()
    assert_response(todo_api.complete_task(done_task.id), 200)
    response = todo_api.get_completed_tasks()
    assert_response(response, 200)
    completed_tasks = [Task.from_json(item) for item in response.json()]
    completed_ids = [t.id for t in completed_tasks]
    assert done_task.id in completed_ids
    assert open_task.id not in completed_ids
    assert all(t.completed for t in completed_tasks), "Endpoint returned a task that is not completed"