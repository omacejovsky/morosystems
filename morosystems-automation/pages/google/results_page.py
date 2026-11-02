from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class GoogleResultsPage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.results = page.locator("#search")
        self.organic_results = page.locator("#search a:has(h3):not(#tads a)")

    def first_organic_result_on(self, host: str) -> Locator:
        return self.organic_results.filter(has=self.page.locator("cite", has_text=host)).first

    def open_result(self, result: Locator) -> None:
        self.log.info("Opening search result %r", result.locator("h3").inner_text())
        result.click()
