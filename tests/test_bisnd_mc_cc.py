from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMISSION, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.bisnd_mc import BisndMCCCSpider

test_response = file_response(
    join(dirname(__file__), "files", "bisnd_mc_cc.json"),
    url="https://mandannd.api.civicclerk.com/v1/Events?$filter=categoryId+in+(26)+and+startDateTime+ge+2024-02-12T10:00:00Z+and+startDateTime+le+2024-09-12T10:00:00Z&$orderby=startDateTime",  # noqa
)
spider = BisndMCCCSpider()

freezer = freeze_time("2024-03-12")  # Adjust the date as needed
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "City Commission Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 2, 20, 17, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "bisnd_mc_cc/202402201700/x/city_commission_meeting"


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {"name": "", "address": None}


def test_source():
    assert (
        parsed_items[0]["source"] == "https://mandannd.portal.civicclerk.com/"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://mandannd.api.civicclerk.com/v1/Meetings/GetMeetingFileStream(fileId=96,plainText=false)",  # noqa
            "title": "February 20, 2024 City Commission Meeting Minutes",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


def test_all_day():
    assert parsed_items[0]["all_day"] is False
