from typing import Literal, TypedDict
from urllib.parse import urljoin

from scrapy import Request, Spider
from scrapy.selector import Selector

from csv_writer import CSVWriter

PartOfSpeech = Literal["Verb", "Adjektiv", "Substantiv"]


class LemmaFilters(TypedDict, total=False):
    part_of_speech: set[PartOfSpeech]
    starts_with: str
    does_not_start_with: list[str]


LemmaFeature = Literal["url", "title", "part_of_speech", "hyphenation"]


SOFT_HYPHEN = "\xad"


class DudenSpider(Spider):
    """Extract Information from duden.de

    Spider has 2 levels: 1st one handles search results, 2nd one lemma page.
    """

    name = "duden spide"
    base_url = "https://www.duden.de/"
    filters: LemmaFilters
    features: list[LemmaFeature]

    def parse(self, search_result_page):
        lemma_outline_path = "*//section[@class='vignette']"
        outlines = search_result_page.xpath(lemma_outline_path)
        for lemma_outline in outlines:
            if self._lemma_outline_is_relevant(lemma_outline):
                url = urljoin(
                    self.base_url,
                    self._extract_relative_lemma_url(lemma_outline),
                )
                yield Request(
                    url=url,
                    callback=self.parse_lemma_page,
                )
        next_relative_url = self._extract_next_page_url(search_result_page)
        if next_relative_url:
            yield Request(
                url=urljoin(
                    search_result_page.request.url,
                    next_relative_url,
                ),
                callback=self.parse,
            )

    @staticmethod
    def _extract_next_page_url(search_result_page) -> str:
        next_page_link_path = "//a[@class='pager__item' and @rel='next']/@href"
        result = search_result_page.xpath(next_page_link_path).extract()
        if not result:
            return None

        return result[0]

    @staticmethod
    def _clean_soft_hyphens(s: str) -> str:
        return s.replace(SOFT_HYPHEN, "")

    def _lemma_outline_is_relevant(self, lemma_outline: Selector) -> bool:
        """Outline is relevant if it does not contradict filters"""

        lemma_title = self._extract_lemma_title(lemma_outline)
        if "starts_with" in self.filters:
            if not lemma_title.startswith(self.filters["starts_with"]):
                return False

        if "does_not_start_with" in self.filters:
            if any(
                lemma_title.startswith(forbidden_beginning)
                for forbidden_beginning in self.filters["does_not_start_with"]
            ):
                return False

        if "part_of_speech" in self.filters:
            description = self._extract_lemma_description(lemma_outline)
            if not any(
                description.startswith(relevant_part_of_speech)
                for relevant_part_of_speech in self.filters["part_of_speech"]
            ):
                return False

        return True

    def _extract_lemma_title(self, lemma_outline: Selector) -> str:
        title_path = "h2[@class='vignette__title']/a/strong/text()"
        result = lemma_outline.xpath(title_path).extract()[0]
        return self._clean_soft_hyphens(result)

    @staticmethod
    def _extract_lemma_description(lemma_outline: Selector) -> str:
        description_path = "p[@class='vignette__snippet']/text()"
        return lemma_outline.xpath(description_path).extract()[0].strip()

    @staticmethod
    def _extract_relative_lemma_url(lemma_outline: Selector) -> str:
        url_path = "a[@class='vignette__link']/@href"
        relative_url = lemma_outline.xpath(url_path).extract()[0]
        return relative_url

    def parse_lemma_page(self, lemma_page) -> None:
        result = {}
        if "url" in self.features:
            result["url"] = lemma_page.request.url
        if "title" in self.features:
            result["title"] = self._extract_title(lemma_page)
        if "hyphenation" in self.features:
            result["hyphenation"] = self._extract_hyphenation(lemma_page)
        if "part_of_speech" in self.features:
            result["part_of_speech"] = self._extract_pos(lemma_page)
        self.csv_writer.writerow(result)

    @staticmethod
    def _extract_pos(lemma_page) -> str | None:
        pos_path = (
            "//article/dl["
            "dt["
            "@class='tuple__key' "
            "and contains(text(), 'Wortart')"
            "]"
            "]/dd[@class='tuple__val']/text()"
        )
        pos = lemma_page.xpath(pos_path).extract()
        if not pos:
            return None
        return pos[0]

    def _extract_raw_title(self, lemma_page) -> str:
        title_path = "//div[@class='lemma']/h1/span/text()"
        return lemma_page.xpath(title_path).extract()[0]

    def _extract_title(self, lemma_page) -> str:
        raw_title = self._extract_raw_title(lemma_page)
        return self._clean_soft_hyphens(raw_title)

    def _extract_hyphenation(self, lemma_page) -> str:
        raw_title = self._extract_raw_title(lemma_page)
        hyphenation = raw_title.replace(SOFT_HYPHEN, " | ")
        return hyphenation


def make_duden_spider(
    output_path: str,
    search_term: str,
    features: list[LemmaFeature],
    filters: LemmaFilters | None = None,
) -> DudenSpider:
    filters = filters or {}
    spider = DudenSpider
    spider.filters = filters
    spider.features = features

    spider.start_urls = [
        f"https://www.duden.de/suchen/dudenonline/{search_term}"
    ]
    spider.csv_writer = CSVWriter(output_path, fields=features)
    return spider
