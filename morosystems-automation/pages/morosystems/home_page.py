from config.settings import settings
from pages.morosystems.morosystems_page import MoroSystemsPage


class MoroSystemsHomePage(MoroSystemsPage):
    TITLE = "MoroSystems - smysluplná IT řešení a technologické inovace"

    def open(self) -> "MoroSystemsHomePage":
        self.goto(settings.morosystems_url)
        return self
