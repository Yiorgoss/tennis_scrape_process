from scrapy.exceptions import DropItem

import datetime


class DuplicatesPipeline(object):
    """simple pipeline to check for any duplicate items,
    checking is done via name attribute"""

    def __init__(self):
        self.names = dict()

    def process_item(self, item, spider):

        item_name = item["name"][0]  # scrapy places item in list
        if item_name in self.names:
            self.names[item_name] += 1  # count number duplicates
            raise DropItem("DuplicateError", "Duplicate dropped: %s" % item["name"])
        else:
            self.names[item_name] = 1
            return item

    def close_spider(self, spider):
        """record the name and number of any duplicate items"""
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        with open(f"output/logs/sum_duplicate-{date}).csv", "a+") as f:
            f.write(f"Duplicate count for -- {date}\n")

            for item in self.names.items():
                f.write("{item[0],item[1]}")
