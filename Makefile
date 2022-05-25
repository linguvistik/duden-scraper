.PHONY: pretty lint

pretty:
	black . -l 80


lint:
	pylint duden-scraper
