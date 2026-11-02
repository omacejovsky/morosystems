import logging
from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.log = logging.getLogger(type(self).__name__)

    def goto(self, url: str) -> None:
        self.log.info("Opening %s", url)
        self.page.goto(url)

    @property
    def url(self) -> str:
        return self.page.url
