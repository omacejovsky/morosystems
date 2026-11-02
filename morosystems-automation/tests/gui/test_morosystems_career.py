import pytest
from playwright.sync_api import Page, expect

from config.settings import settings
from pages.google.search_page import GoogleBlockedError, GoogleSearchPage
from pages.morosystems.career_page import CareerPage
from pages.morosystems.home_page import MoroSystemsHomePage
from pages.morosystems.morosystems_page import MoroSystemsPage

pytestmark = pytest.mark.gui

SEARCH_QUERY = "MoroSystems"
MOROSYSTEMS_HOST = "www.morosystems.cz"
CITY = "Brno"

def assert_positions_filtered_by(career_page: CareerPage, city: str) -> None:
    expect(career_page.selected_city).to_contain_text(city)
    expect(career_page.visible_positions.first).to_be_visible()

    for position in career_page.visible_positions.all():
        assert city in career_page.position_cities(position), (
            f"Visible position {position.inner_text()!r} is not offered in {city}"
        )
    for position in career_page.hidden_positions.all():
        assert city not in career_page.position_cities(position), (
            f"Position offered in {city} was hidden by the filter"
        )

def check_career_filter(moro_page: MoroSystemsPage) -> None:
    page = moro_page.page
    career_page = moro_page.go_to_career()
    expect(page).to_have_url(f"{settings.morosystems_url}{CareerPage.PATH}")
    expect(career_page.heading).to_be_visible()

    career_page.filter_by_city(CITY)
    assert_positions_filtered_by(career_page, CITY)

def test_google_search_start(google_search_page: GoogleSearchPage, page: Page) -> None:
    try:
        results_page = google_search_page.search(SEARCH_QUERY)
    except GoogleBlockedError as error:
        pytest.skip(f"Google blocked the automated browser with a CAPTCHA ({error})")

    expect(results_page.results).to_be_visible()
    assert "/search" in page.url
    assert f"q={SEARCH_QUERY}" in page.url

    moro_result = results_page.first_organic_result_on(MOROSYSTEMS_HOST)
    expect(moro_result).to_be_visible()

    results_page.open_result(moro_result)
    page.wait_for_url(f"{settings.morosystems_url}/**")
    check_career_filter(MoroSystemsPage(page))

def test_moro_homepage_start(home_page: MoroSystemsHomePage) -> None:
    expect(home_page.page).to_have_url(f"{settings.morosystems_url}/")
    expect(home_page.page).to_have_title(MoroSystemsHomePage.TITLE)
    check_career_filter(home_page)
