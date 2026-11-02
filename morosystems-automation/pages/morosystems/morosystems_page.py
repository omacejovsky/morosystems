from playwright.sync_api import Page
from pages.base_page import BasePage

class MoroSystemsPage(BasePage):

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.main_menu = page.locator("nav.m-main")
        self.about_menu = self.main_menu.locator(".item-about")
        self.career_link = self.about_menu.get_by_role("link", name="Kariéra", exact=True)

    def go_to_career(self) -> "CareerPage":
        from pages.morosystems.career_page import CareerPage
        self.log.info("Navigating to Kariéra via the 'O nás' menu")
        self.about_menu.hover()
        self.career_link.click()
        return CareerPage(self.page)
