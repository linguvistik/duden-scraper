from argparse import ArgumentParser
from typing import get_args

from scrapy.crawler import CrawlerProcess

from duden_spider import (
    make_duden_spider,
    PartOfSpeech,
    LemmaFilters,
    LemmaFeature,
)


valid_part_of_speech = get_args(PartOfSpeech)
valid_features = get_args(LemmaFeature)

parser = ArgumentParser(description="Fetch Lemma information from duden.de")
parser.add_argument(
    "--output",
    "-o",
    type=str,
    help="Path to store the results csv file",
)
parser.add_argument(
    "--search", type=str, help="The search term to start the lemma search with."
)
parser.add_argument(
    "--part-of-speech",
    "-pos",
    nargs="*",
    choices=valid_part_of_speech,
    help=(
        "Restrict results to certain parts of speech."
        f" Allowed values: {valid_part_of_speech}"
    ),
)
parser.add_argument(
    "--starts-with",
    nargs="?",
    type=str,
    help="Restrict results to lemmas which start with the provided string",
)
parser.add_argument(
    "--does-not-start-with",
    nargs="*",
    type=str,
    help=(
        "Restrict results to lemmas which do not start with any of the"
        " provided strings"
    ),
)
parser.add_argument(
    "--extract",
    nargs="*",
    default=valid_features,
    choices=valid_features,
)


if __name__ == "__main__":
    args = parser.parse_args()
    filters: LemmaFilters = {}
    features: set[LemmaFeature]
    if args.part_of_speech:
        filters["part_of_speech"] = set(args.part_of_speech)
    if args.starts_with:
        filters["starts_with"] = args.starts_with
    if args.does_not_start_with:
        filters["does_not_start_with"] = args.does_not_start_with
    if args.extract:
        features = list(set(args.extract))
    else:
        features = list(valid_features)

    spider = make_duden_spider(
        output_path=args.output,
        search_term=args.search,
        filters=filters,
        features=features,
    )
    process = CrawlerProcess()
    process.crawl(spider)
    process.start()
