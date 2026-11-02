import logging

import pytest
from playwright.sync_api import Locator, Page

from pages.google.search_page import GoogleSearchPage
from pages.morosystems.home_page import MoroSystemsHomePage

log = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    return {
        **browser_context_args,
        "locale": "cs-CZ",
        "viewport": {"width": 1440, "height": 900},
    }

@pytest.fixture(autouse=True)
def reject_cookie_dialogs(page: Page) -> None:
    google_consent = page.get_by_role("button", name="Odmítnout vše", exact=True).or_(
        page.get_by_role("button", name="Reject all", exact=True)
    )
    morosystems_cookies = page.get_by_role("button", name="Pouze nutné", exact=True)

    for reject_button in (google_consent, morosystems_cookies):
        page.add_locator_handler(reject_button, _reject_cookies)

def _reject_cookies(reject_button: Locator) -> None:
    log.info("Rejecting cookies: %r", reject_button.inner_text())
    reject_button.dispatch_event("click")

@pytest.fixture
def google_search_page(page: Page) -> GoogleSearchPage:
    return GoogleSearchPage(page).open()

@pytest.fixture
def home_page(page: Page) -> MoroSystemsHomePage:
    return MoroSystemsHomePage(page).open()
