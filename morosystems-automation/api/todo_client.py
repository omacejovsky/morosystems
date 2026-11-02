import logging
from typing import Optional

from playwright.sync_api import APIRequestContext, APIResponse

log = logging.getLogger(__name__)

class TodoApiClient:
    TASKS = "/tasks"

    def __init__(self, request: APIRequestContext) -> None:
        self._request = request

    def get_tasks(self) -> APIResponse:
        return self._send("GET", self.TASKS)

    def create_task(self, body: Optional[dict]) -> APIResponse:
        return self._send("POST", self.TASKS, body)

    def update_task(self, task_id: str, body: Optional[dict]) -> APIResponse:
        return self._send("POST", f"{self.TASKS}/{task_id}", body)

    def put_task(self, task_id: str, body: Optional[dict]) -> APIResponse:
        return self._send("PUT", f"{self.TASKS}/{task_id}", body)

    def delete_task(self, task_id: str) -> APIResponse:
        return self._send("DELETE", f"{self.TASKS}/{task_id}")

    def complete_task(self, task_id: str) -> APIResponse:
        return self._send("POST", f"{self.TASKS}/{task_id}/complete")

    def incomplete_task(self, task_id: str) -> APIResponse:
        return self._send("POST", f"{self.TASKS}/{task_id}/incomplete")

    def get_completed_tasks(self) -> APIResponse:
        return self._send("GET", f"{self.TASKS}/completed")

    def _send(self, method: str, path: str, body: Optional[dict] = None) -> APIResponse:
        response = self._request.fetch(path, method=method, data=body)
        log.info("%s %s body=%r -> %s", method, path, body, response.status)
        return response
