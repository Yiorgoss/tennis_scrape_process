import datetime

date = datetime.datetime.now().strftime("%Y-%m-%d")

BOT_NAME = "tennis-scraper"


SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"


# Obey robots.txt rules
ROBOTSTXT_OBEY = True

LOG_ENABLED = True
LOG_FILE = f"scrape-{date}.csv"
# Disable cookies (enabled by default)
# COOKIES_ENABLED = False
# COOKIES_DEBUG = True

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "scraper.pipelines.DuplicatesPipeline": 300,
}
