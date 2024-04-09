from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.bisnd_mcc import BisndMccSpider

test_response = file_response(
    join(dirname(__file__), "files", "bisnd_mcc.html"),
    url="https://www.mortonnd.org/?Type=B_BASIC&SEC={8182F8B8-3783-4C56-B690-F78FEE7CAC95}",  # noqa
)
spider = BisndMccSpider()

freezer = freeze_time(datetime(2024, 3, 14, 10, 15))
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
parsed_item = parsed_items[0]
freezer.stop()


def test_title():
    assert parsed_item["title"] == "Morton County Commission Meeting"


def test_description():
    assert parsed_item["description"] == ""


def test_start():
    assert parsed_item["start"] == datetime(2024, 12, 26, 17, 30)


def test_end():
    assert parsed_item["end"] is None


def test_time_notes():
    assert parsed_item["time_notes"] == ""


def test_id():
    assert (
        parsed_item["id"] == "bisnd_mcc/202412261730/x/morton_county_commission_meeting"
    )


def test_status():
    assert parsed_item["status"] == TENTATIVE


def test_location():
    assert parsed_item["location"] == {
        "address": "Morton County Commission Room",
        "name": "Morton County Courthouse, 210 2nd Ave NW, Mandan ND",
    }


def test_source():
    assert (
        parsed_item["source"]
        == "https://www.mortonnd.org/?Type=B_BASIC&SEC={8182F8B8-3783-4C56-B690-F78FEE7CAC95}"  # noqa
    )


def test_links():
    assert parsed_item["links"] == []


def test_classification():
    assert parsed_item["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
