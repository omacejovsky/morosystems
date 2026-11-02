import uuid
from typing import Callable, Iterator, Optional
import pytest
from playwright.sync_api import APIRequestContext, Error, Playwright
from api.models import Task
from api.todo_client import TodoApiClient
from config.settings import settings

@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> Iterator[APIRequestContext]:
    context = playwright.request.new_context(
        base_url=settings.todo_api_url,
        timeout=settings.api_timeout_ms,
    )
    try:
        context.get("/v3/api-docs")
    except Error as error:
        context.dispose()
        pytest.fail(
            f"todo-be is not reachable at {settings.todo_api_url} "
            f"(start it with `docker compose up -d --wait`): {error}",
            pytrace=False,
        )
    yield context
    context.dispose()


@pytest.fixture
def todo_api(api_request_context: APIRequestContext) -> TodoApiClient:
    return TodoApiClient(api_request_context)

@pytest.fixture
def unique_text() -> Callable[[], str]:
    return lambda: f"autotest-{uuid.uuid4().hex[:12]}"

@pytest.fixture
def cleanup_task_ids(todo_api: TodoApiClient) -> Iterator[list[str]]:
    task_ids: list[str] = []
    yield task_ids
    for task_id in task_ids:
        todo_api.delete_task(task_id)

@pytest.fixture
def create_task(
    todo_api: TodoApiClient, unique_text: Callable[[], str], cleanup_task_ids: list[str]) -> Callable[..., Task]:

    def _create(text: Optional[str] = None) -> Task:
        response = todo_api.create_task({"text": unique_text() if text is None else text})
        assert response.ok, f"Precondition failed, could not create task: {response.status}"
        task = Task.from_json(response.json())
        cleanup_task_ids.append(task.id)
        return task

    return _create