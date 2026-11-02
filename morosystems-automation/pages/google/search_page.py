from playwright.sync_api import Page
from config.settings import settings
from pages.base_page import BasePage
from pages.google.results_page import GoogleResultsPage

class GoogleBlockedError(Exception):
    """Google served its anti-bot ("unusual traffic") page instead of results."""

class GoogleSearchPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.search_box = page.locator('[name="q"]')
        self.captcha_form = page.locator("#captcha-form")

    def open(self) -> "GoogleSearchPage":
        self.goto(settings.google_url)
        return self

    def search(self, query: str) -> GoogleResultsPage:
        self.log.info("Searching for %r", query)
        self.search_box.fill(query)
        self.search_box.press("Enter")
        results_page = GoogleResultsPage(self.page)
        results_page.results.or_(self.captcha_form).first.wait_for()
        if self.captcha_form.is_visible():
            raise GoogleBlockedError("Google redirected the search to its /sorry/ anti-bot page")
        return results_page
