from urllib.parse import urljoin

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
        "name": "Tom Baker Room",
        "address": "City/County Building, 221 N 5th St, Bismarck",
    }

    def parse(self, response):
        """
        Parse meeting items from agency website.
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
                    links=self._parse_links(response, links, item),
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_date(self, item):
        """Parse start date. Used in multiple functions."""
        return item.css("td:first_child::text").get()

    def _parse_start(self, item, time):
        """
        Parse start datetime as a naive datetime object.
        Combine the date from the table with the time found in a paragraph.
        """
        date = self._parse_date(item)
        parsed_datetime = parse(f"{date} {time}")

        return parsed_datetime

    def _parse_links(self, response, links, item):
        """
        Parse links. Agenda and Minutes links are sometimes present.
        Video and radio coverage links are always given.
        """
        output = links.copy()
        date = self._parse_date(item)
        # get minutes link
        year = date.split()[-1]
        minutes_href = (
            response.xpath(
                f'//a[contains(text(), "{year} Planning and Zoning Commission Minutes")]'  # noqa
            )
            .css("::attr(href)")
            .get()
        )
        if minutes_href:
            minutes_url = urljoin(response.url, minutes_href)
            output.insert(
                0,
                {
                    "title": f"{year} Planning and Zoning Commission Minutes",
                    "href": minutes_url,
                },
            )
        # get agenda link
        agenda_href = (
            response.xpath(f'//a[contains(text(), "{date} Agenda")]')
            .css("::attr(href)")
            .get()
        )
        if agenda_href:
            agenda_url = urljoin(response.url, agenda_href)
            output.insert(0, {"title": f"{date} Agenda Packet", "href": agenda_url})

        return output
