import scrapy
from scrapy import Request, FormRequest, Selector
from scraper.items import Item
from scrapy.loader import ItemLoader

import logging


class TWE_Spider(scrapy.Spider):
    name = "tenniswarehouse"

    start_urls = ["https://www.tenniswarehouse-europe.com"]

    unmatched = 0

    def start_requests(self):
        # set the cookie
        return [
            FormRequest(
                "https://www.tenniswarehouse-europe.com",
                formdata={"lang": "en", "vat": "GR"},
            )
        ]

    def parse(self, response):
        """
        Follows the urls on the main page
        """

        # left navigation menu with all the urls in the website - hopefully
        url_list = response.css("ul.lnav_section > li >a::attr(href)").getall()
        url_list.extend(response.css("div.lnav_heading > a::attr(href)").getall())
        # .xpath("./li/a/@href")

        for url in url_list:
            # start by going through the sub urls
            url = self.absolute_url_helper(url)

            yield response.follow(
                url,
                callback=self.page_layout_parser,
            )

    def page_layout_parser(self, response):

        # layout 1
        layout_selectors = response.css("td.cat_border_cell")

        if layout_selectors:
            # example layout 1 - https://www.tenniswarehouse-europe.com/catpage-BABOLATRAC-EN.html
            self.logger.info("Layout 1 matched")
            for selector in layout_selectors:
                # only enters if product_card_list returns something
                yield self.parse_layout_2(selector)

        # layout 2
        layout_selectors = response.css(".brands_block-cell")  # page layout 2
        if layout_selectors:
            # example layout 2 - https://www.tenniswarehouse-europe.com/catpage-PADEL.html
            self.logger.info(f"Layout 2 matched")
            for li in layout_selectors:
                url = li.xpath("./a/@href").get()
                self.logger.info(url)

                yield response.follow(
                    url,
                    callback=self.parse_layout_4,
                )

        # layout 4
        layout_selectors = response.css(".brand_tile")
        if layout_selectors:
            # example layout 4 - https://www.tenniswarehouse-europe.com/apparelmen.html
            self.logger.info(f"Layout 2 matched")
            for selector in layout_selectors:
                url = selector.xpath("ancestor::a/@href").get()
                if not url:
                    url = selector.xpath("@href").get()

                url = self.absolute_url_helper(url)

                yield response.follow(
                    url=url,
                    callback=self.parse_layout_4,
                )

        # layout 3
        layout_selectors = response.css("td.name + td, td.name").getall()
        # list of all names and prices then group two at a time

        if layout_selectors:
            # example layout 3 - https://www.tenniswarehouse-europe.com/catpage-GACGROM-EN.html
            self.logger.info("Layout 3 matched")
            url = response.url
            for row in self.group_by(layout_selectors, 2):
                # nice layouts
                yield self.parse_layout_3(
                    row[0], row[1], url
                )  # row[0] = name, row[1] = price

        self.unmatched += 1
        self.logger.info(f"Number of unmatched urls == {self.unmatched}")
        yield None

    def parse_layout_1(self, selector):
        # legacy code no longer in use
        l = ItemLoader(item=Item(), selector=selector)

        l.add_css("name", ".name::text")
        l.add_css("url", ".name::attr(href)")

        # get the text and just join
        prices_list = selector.css(".convert_price::text").getall()

        prices_string = ";".join(prices_list)
        # cant join with comma because greek prices use , instaed of .
        # if needed must also be changed in the Item methods
        l.add_value("prices", prices_string)
        # l.add_value("prices", ["1", "2", "3"])

        l.add_css("sale_tag", "span.producttag::text")

        return l.load_item()

    def parse_layout_2(self, selector):

        l = ItemLoader(item=Item(), selector=selector)

        name = selector.css(".name > a::text").get()
        url = selector.css(".name > a::attr(href)").get()

        if not name:
            # if not set means name/url under different element
            name = selector.css(".name::text").get()
        if not url:
            url = selector.css(".name::attr(href)").get()

        l.add_value("name", name)
        l.add_value("url", url)

        prices_list = selector.css(".convert_price::text").getall()
        prices_string = ";".join(prices_list)
        l.add_value("prices", prices_string)

        l.add_css("sale_tag", "span.producttag::text")

        if not name or not prices_list:
            DropItem("MissingValuesError", "Missing values")

        return l.load_item()

    def parse_layout_3(self, name, price, url):
        l = ItemLoader(item=Item())

        l.add_value("name", name)
        l.add_value("url", url)

        l.add_value("prices", price)
        l.add_value("sale_tag", "")

        return l.load_item()

    def parse_layout_4(self, response):
        product_list = response.css(".product_wrapper")

        for product in product_list:
            yield self.parse_layout_2(product)

    def group_by(self, arr, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(arr), n):
            yield arr[i : i + n]

    def absolute_url_helper(self, url):
        # some urls contain domain others do not
        # this method just appends domain to the start
        if len(url.split("/")) < 3:
            # self.logger.info(f"urlhelper called: {url}")
            url = self.start_urls[0] + url

        return url
