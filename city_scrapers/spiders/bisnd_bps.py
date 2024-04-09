import html
import json
import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from lxml import html as lhtml
from scrapy import Selector


class BisndBpsSpider(CityScrapersSpider):
    name = "bisnd_bps"
    agency = "Bismarck Public Schools"
    timezone = "America/Chicago"
    start_urls = ["https://www.bismarckschools.org/Page/401"]

    """
    Meetings' time and location is taken from organization's following webpage:
    https://www.bismarckschools.org/Page/398
    """
    meeting_time = time(17, 15)

    location = {
        "name": "Tom Baker Meeting Room",
        "address": "City/County Office Building, 221 N Fifth Street, Bismarck, ND",
    }

    def parse(self, response):

        extracted_input = response.css(
            '.ui-widget-detail input[type="hidden"]::attr(value)'
        ).extract_first()

        parsable_data = self._parsed_data(extracted_input)

        for item in parsable_data:
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes=self._parse_time_notes(item),
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        selected_title = item[3]
        html_title_str = lhtml.fromstring(selected_title)
        title = html_title_str.text_content().strip()
        return title if title is not None else ""

    def _parse_classification(self, item):
        title = "".join(item[3].split(">")[1].split("<")[:-1])
        return COMMITTEE if "committee" in title.lower() else BOARD

    def _parse_start(self, item):
        extracted_date = [
            html.unescape("".join(element.split(">")[1].split("<")[:-1]))
            for element in item[:3]
        ]
        result = " ".join(extracted_date)
        parsed_date = result if "(" not in result else result.split(" (")[0]
        date_obj = datetime.strptime(parsed_date, "%Y %B %d")

        return datetime.combine(date_obj, self.meeting_time)

    def _parse_time_notes(self, item):
        """
        Meeting detail for non 'Regular' type meetings
        are accessable from the meeting agenda.
        The notes are added to further clarify the meeting details.
        """
        title = self._parse_title(item)
        if "regular" not in title.lower():
            return "Meetings that are not of type 'Regular' are held at specific locations with specific timing, please refer to the meeting agenda for more details."  # noqa
        return ""

    def _parse_links(self, item):
        extracted_links = [link for link in item[3:]]
        parsed_links = []
        for link in extracted_links:
            sel = Selector(text=link if link is not None else "")
            href = sel.css("a::attr(href)").get()
            title = sel.css("a::text").get()
            if href is not None and title is not None:
                # Remove extra spaces from title
                title = " ".join(title.split())
                parsed_links.append({"href": href, "title": title})
            else:
                continue
        return parsed_links

    def _parsed_data(self, data):
        """
        Some of the extracted meeting data coming from the webpage comes
        in a format that is not easily parsable. As some of the meetings are
        added with multiple dates into single entries. This function filters
        out the meetings that are older than 2 years from the current date and then
        splits the entries with multiple dates into multiple entries with single dates.
        """
        data = json.loads(data)

        # Filter out meetings that are older than a year
        filtered_meetings = [
            item
            for item in data[1:]
            if int("".join(item[0].split(">")[1].split("<")[:-1]))
            >= datetime.now().year - 2
        ]

        new_parsable_data = []

        for item in filtered_meetings:
            dates = re.findall(r"\b\d+(?![^(]*\))\b", item[2])
            if len(dates) < 2:
                new_parsable_data.append(item)
                continue

            sel = Selector(text=item[5] if item[5] is not None else "")
            links = sel.css("p a::attr(href)").getall()
            link_texts = sel.css("p a::text").getall()

            for date in dates:
                new_item = item.copy()
                new_item[2] = f"<p>{date}</p>"
                link_found = False
                for link, link_text in zip(links, link_texts):
                    if date in link_text:
                        new_item[5] = f'<p><a href="{link}">{link_text}</a></p>'
                        link_found = True
                        break
                if not link_found:
                    new_item[5] = None
                new_parsable_data.append(new_item)

        return new_parsable_data
