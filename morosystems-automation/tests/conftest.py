import base64

import pytest
import pytest_html
from playwright.sync_api import Error

def pytest_html_report_title(report) -> None:
    report.title = "MoroSystems – Automation Test Report"

@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    report = yield
    page = item.funcargs.get("page")
    if report.when == "call" and report.failed and page:
        try:
            screenshot = base64.b64encode(page.screenshot(full_page=True)).decode()
        except Error:
            return report
        report.extras = [
            *getattr(report, "extras", []),
            pytest_html.extras.url(page.url, name="Page at failure"),
            pytest_html.extras.png(screenshot, name="Screenshot at failure"),
        ]
    return report
