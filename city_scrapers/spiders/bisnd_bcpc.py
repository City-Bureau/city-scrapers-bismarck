from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class BisndBcpcSpider(CityScrapersSpider):
    name = "bisnd_bcpc"
    agency = "Burleigh County Planning Commission"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.burleigh.gov/government/boardscommittees/planning-zoning-commission/"  # noqa
    ]
    location = {
        "name": "Tom Baker Room, City/County Building",
        "address": "221 N 5th St, Bismarck",
    }

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        time = response.css(".tbltitle p::text").get()
        link1 = response.css(".info p")[6].css("a::attr(href)").get()
        link2 = response.css(".info p")[7].css("a::attr(href)").get()
        title1 = response.css(".info p::text")[7].get()
        title2 = response.css(".info p::text")[8].get()
        links = [
            {"title": title1.replace("\xa0", " "), "href": link1},
            {"title": title2, "href": link2},
        ]

        for item in response.css("table")[1].css("tr"):
            if not item.css("td"):
                continue
            else:
                meeting = Meeting(
                    title="Planning & Zoning Commission Monthly Meeting",
                    description="",
                    classification=COMMISSION,
                    start=self._parse_start(item, time),
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=self.location,
                    links=links,
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_start(self, item, time):
        """Parse start datetime as a naive datetime object."""
        date_str = item.css("td:first_child::text").get()
        parsed_datetime = parse(f"{date_str} {time}")

        return parsed_datetime

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]
