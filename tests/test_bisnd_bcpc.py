from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.bisnd_bcpc import BisndBcpcSpider

test_response = file_response(
    join(dirname(__file__), "files", "bisnd_bcpc.html"),
    url="https://www.burleigh.gov/government/boardscommittees/planning-zoning-commission/",  # noqa
)
spider = BisndBcpcSpider()

freezer = freeze_time("2024-03-27")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 13


def test_title():
    assert parsed_items[0]["title"] == "Planning & Zoning Commission Monthly Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    # all meetings start at 5:15pm
    assert parsed_items[0]["start"] == datetime(2024, 1, 10, 17, 15)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "bisnd_bcpc/202401101715/x/planning_zoning_commission_monthly_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Tom Baker Room",
        "address": "City/County Building, 221 N 5th St, Bismarck",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.burleigh.gov/government/boardscommittees/planning-zoning-commission/"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "January 10, 2024 Agenda Packet",
            "href": "https://www.burleigh.gov/media/acljydn1/2024-01-10-agenda-packet.pdf",  # noqa
        },
        {
            "title": "2024 Planning and Zoning Commission Minutes",
            "href": "https://www.burleigh.gov/media/kwnjqgjt/2024-minutes.pdf",
        },
        {
            "title": "Video coverage provided by Dakota Media Access.  Watch live on Government Access Cable Channels 2 or 602 HD.  Stream live or replay later at ",  # noqa
            "href": "https://dakotamediaaccess.org/government",
        },
        {
            "title": "Stream live radio coverage from KDAK FM 102.5 FM Radio at ",
            "href": "https://radioaccess.org/",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
