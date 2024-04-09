from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.bisnd_bps import BisndBpsSpider

test_response = file_response(
    join(dirname(__file__), "files", "bisnd_bps.html"),
    url="https://www.bismarckschools.org/Page/401",
)
spider = BisndBpsSpider()

freezer = freeze_time("2024-04-02")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

"""
Arbitrary number of items. 90 is the returned number
of items from the spider as it is currently set to only
extract meetings from the current date until 2 years in the past.
"""


def test_count():
    assert len(parsed_items) == 90


def test_title():
    assert parsed_items[0]["title"] == "Regular"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 3, 25, 17, 15)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "bisnd_bps/202403251715/x/regular"


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Tom Baker Meeting Room",
        "address": "City/County Office Building, 221 N Fifth Street, Bismarck, ND",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.bismarckschools.org/Page/401"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://bismarckschools.sharepoint.com/:w:/s/SchoolBoard/AgendaMinutes/ETytiPQ_Nu5Fs_NRRfPkNEwB4EFg29r2InldB4P0pki26A",  # noqa
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
