from playwright.sync_api import Locator, Page

from config.settings import settings
from pages.morosystems.morosystems_page import MoroSystemsPage


class CareerPage(MoroSystemsPage):
    PATH = "/kariera/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Koho hledáme")
        self.city_select = page.locator(".inp-custom-select")
        self.city_select_toggle = self.city_select.locator(".inp-custom-select__select")
        self.positions = page.locator(".c-positions__item")

    def open(self) -> "CareerPage":
        self.goto(settings.morosystems_url + self.PATH)
        return self

    def city_option(self, city: str) -> Locator:
        return self.city_select.locator(f'.inp-custom-select__item[data-filter="{city}"]')

    def filter_by_city(self, city: str) -> "CareerPage":
        self.log.info("Filtering positions by city %r", city)
        self.city_select_toggle.click()
        self.city_option(city).click()
        return self

    @property
    def selected_city(self) -> Locator:
        return self.city_select_toggle

    @property
    def visible_positions(self) -> Locator:
        return self.positions.filter(visible=True)

    @property
    def hidden_positions(self) -> Locator:
        return self.positions.filter(visible=False)

    @staticmethod
    def position_cities(position: Locator) -> list[str]:
        text = position.locator(".c-positions__info").inner_text()
        return [city.strip() for city in text.split(",") if city.strip()]
