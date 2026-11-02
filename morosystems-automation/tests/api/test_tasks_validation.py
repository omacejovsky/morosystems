import uuid
from typing import Any, Callable, Optional

import pytest
from playwright.sync_api import APIRequestContext

from api.models import Task
from api.todo_client import TodoApiClient
from tests.api.assertions import assert_response, assert_task_stored

pytestmark = pytest.mark.api

TEXT_REQUIRED = "'text' field must be present in json"
WRONG_TYPE_BUG = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Backend bug: non-string 'text' is accepted (200) and stored, breaking the Task schema",
)
INVALID_BODIES = [
    pytest.param({}, TEXT_REQUIRED, id="missing-text"),
    pytest.param({"text": ""}, TEXT_REQUIRED, id="empty-text"),
    pytest.param({"text": 123}, None, id="number-text", marks=WRONG_TYPE_BUG),
    pytest.param({"text": True}, None, id="bool-text", marks=WRONG_TYPE_BUG),
    pytest.param({"text": ["a"]}, None, id="list-text", marks=WRONG_TYPE_BUG),
]
MALFORMED_JSON = '{"text": '

@pytest.fixture
def unknown_task_id() -> str:
    return f"nonexistent-{uuid.uuid4().hex}"

@pytest.mark.parametrize("body, error_text", INVALID_BODIES)
def test_create_task_rejects_invalid_body(
    todo_api: TodoApiClient, body: dict[str, Any], error_text: Optional[str], cleanup_task_ids: list[str]) -> None:
    response = todo_api.create_task(body)
    if response.ok:
        cleanup_task_ids.append(response.json()["id"])
    assert_response(response, 422, error_text)

@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Backend bug: POST /tasks without a body crashes with 500 and leaks a stack trace",
)
def test_create_task_rejects_missing_body(todo_api: TodoApiClient) -> None:
    response = todo_api.create_task(None)
    assert_response(response, 422, TEXT_REQUIRED)

@pytest.mark.parametrize("body, error_text", INVALID_BODIES)
def test_update_task_rejects_invalid_body(
    todo_api: TodoApiClient, create_task: Callable[..., Task], body: dict[str, Any], error_text: Optional[str]) -> None:
    task = create_task()
    response = todo_api.update_task(task.id, body)
    assert_response(response, 422, error_text)
    assert_task_stored(todo_api, task)

def test_malformed_json_returns_400(api_request_context: APIRequestContext) -> None:
    response = api_request_context.post(
        TodoApiClient.TASKS, data=MALFORMED_JSON, headers={"Content-Type": "application/json"}
    )
    assert_response(response, 400)

@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Backend bug: the 400 for malformed JSON is an HTML stack trace exposing internal file paths",
)
def test_malformed_json_error_hides_internals(api_request_context: APIRequestContext) -> None:
    response = api_request_context.post(
        TodoApiClient.TASKS, data=MALFORMED_JSON, headers={"Content-Type": "application/json"}
    )
    assert "node_modules" not in response.text(), "Error response exposes server file paths"

def test_update_unknown_task_returns_404(todo_api: TodoApiClient, unknown_task_id: str) -> None:
    response = todo_api.update_task(unknown_task_id, {"text": "does not matter"})
    assert_response(response, 404, "id not found, nothing to update")

def test_delete_unknown_task_returns_404(todo_api: TodoApiClient, unknown_task_id: str) -> None:
    response = todo_api.delete_task(unknown_task_id)
    assert_response(response, 404, "id not found, nothing to delete")

def test_complete_unknown_task_returns_404(todo_api: TodoApiClient, unknown_task_id: str) -> None:
    response = todo_api.complete_task(unknown_task_id)
    assert_response(response, 404, "id not found, nothing to complete")

def test_incomplete_unknown_task_returns_404(todo_api: TodoApiClient, unknown_task_id: str) -> None:
    response = todo_api.incomplete_task(unknown_task_id)
    assert_response(response, 404, "id not found, nothing to incomplete")
