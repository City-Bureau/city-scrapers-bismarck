from datetime import datetime

from city_scrapers_core.constants import (
    BOARD,
    CITY_COUNCIL,
    COMMISSION,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.relativedelta import relativedelta
from scrapy import Request


class MCMixinMeta(type):
    """
    Metaclass that enforces the implementation of required static
    variables in child classes.
    """

    def __init__(cls, name, bases, dct):
        required_static_vars = ["agency", "name", "category_id"]
        missing_vars = [var for var in required_static_vars if var not in dct]

        if missing_vars:
            missing_vars_str = ", ".join(missing_vars)
            raise NotImplementedError(
                f"{name} must define the following static variable(s): {missing_vars_str}."  # noqa
            )
        super().__init__(name, bases, dct)


class MCMixin(CityScrapersSpider, metaclass=MCMixinMeta):
    """
    Spider mixin for City of Mandan in Mandan, ND. This mixin
    is intended to be used as a base class for spiders that scrape meeting
    data from the city's website.
    """

    base_url = "https://mandannd.api.civicclerk.com"
    timezone = "America/Chicago"
    name = None
    agency = None
    category_id = None

    def start_requests(self):
        """
        Construct and yield a request to the API endpoint.
        """
        # Calculate dates for one month prior and one year ahead
        today = datetime.today()
        one_month_prior = today - relativedelta(months=1)
        half_year_ahead = today + relativedelta(months=6)

        # Format dates like "2024-03-01T00:00:00.000Z"
        meeting_date_from = one_month_prior.strftime("%Y-%m-%dT%H:00:00Z")
        meeting_date_to = half_year_ahead.strftime("%Y-%m-%dT%H:00:00Z")

        # build the URL
        url = f"{self.base_url}/v1/Events?$filter=categoryId+in+({self.category_id})+and+startDateTime+ge+{meeting_date_from}+and+startDateTime+le+{meeting_date_to}&$orderby=startDateTime"  # noqa

        yield Request(url, callback=self.parse)

    def parse(self, response):
        """
        Parse a list of meetings from the response.
        """
        items = response.json()
        if not items or len(items) == 0 or "value" not in items:
            self.logger.warning("No meetings found")
            return
        for item in items["value"]:
            meeting = Meeting(
                title=item["eventName"],
                description=item["eventDescription"],
                classification=self._parse_classification(item["categoryName"]),
                start=self._parse_start(item["startDateTime"]),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item["eventLocation"]),
                links=self._parse_links(item),
                source="https://mandannd.portal.civicclerk.com/",
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_classification(self, name):
        """
        Parse or generate classification from allowed options.
        """
        if "city council" in name.lower():
            return CITY_COUNCIL
        if "board" in name.lower():
            return BOARD
        if "commission" in name.lower():
            return COMMISSION
        if "committee" in name.lower():
            return COMMITTEE
        return NOT_CLASSIFIED

    def _parse_start(self, start):
        """
        Parse the start date and time.
        """
        return datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")

    def _parse_location(self, location):
        """
        Parse or generate location.
        """
        if not location:
            return {
                "name": "",
                "address": "",
            }
        # build location from address1, city, state, zipCode
        address = location["address1"]
        address_fields = ["address2", "city", "state", "zipCode"]
        for field in address_fields:
            if location[field]:
                address += f", {location[field].strip()}"
        return {
            "name": "",
            "address": address,
        }

    def _parse_links(self, item):
        """
        Parse published files into links.
        """
        links = []
        if "publishedFiles" in item and len(item["publishedFiles"]) > 0:
            for file in item["publishedFiles"]:
                links.append(
                    {
                        "title": file["name"],
                        "href": f"{self.base_url}/v1/Meetings/GetMeetingFileStream(fileId={file['fileId']},plainText=false)",  # noqa
                    }
                )
        return links
