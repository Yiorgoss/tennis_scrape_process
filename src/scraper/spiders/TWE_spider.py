import scrapy
from scrapy import Request, FormRequest, Selector
from scraper.items import Item
from scrapy.loader import ItemLoader

import logging


class TWE_Spider(scrapy.Spider):
    name = "tenniswarehouse"

    start_urls = ["https://www.tenniswarehouse-europe.com"]
    allowed_domains = ["tenniswarehouse-europe.com"]

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
        url_list = response.css("ul.lnav_section > li >a::attr(href)")
        # .xpath("./li/a/@href")

        for url in url_list.getall():
            # start by going through the sub urls
            url = self.absolute_url_helper(url)
            yield response.follow(
                url,
                callback=self.parse_product_list,
            )
        url_list = response.css("div.lnav_heading > a::attr(href)")
        for url in url_list.getall():
            url = self.absolute_url_helper(url)
            yield response.follow(
                url,
                callback=self.parse_product_list,
            )

    def parse_product_list(self, response):
        product_card_list = response.css("td.cat_border_cell")

        if not product_card_list:
            # does not contain a grid with products
            self.logger.info("No product_list in - %s" % response.url)
            yield

        for card in product_card_list:
            # try and parse relevant info from catelog page
            # else try from product page
            l = ItemLoader(item=Item(), selector=card)

            l.add_css("name", ".name::text")
            l.add_css("url", ".name::attr(href)")

            # get the text and just join
            prices_list = card.css(".convert_price::text").getall()

            prices_string = ";".join(prices_list)
            # cant join with comma because greek prices use , instaed of .
            # if needed must also be changed in the Item methods
            l.add_value("prices", prices_string)
            # l.add_value("prices", ["1", "2", "3"])

            sale_classes = card.css(".name").attrib["class"]
            l.add_value("sale_tags", sale_classes)

            yield l.load_item()

    def cycle_layout_parser(self, response):
        """search for specific classname
        if it exists then that is the layout to parse
        there are 3 different possible layouts

        if the selector returns nothing then it must be the other layout
        """
        self.logger.info(
            "======================================================================================================================="
        )

        self.logger.info("Trying to cycle layout parser...")
        li_list = response.css("ul.brand_icon_list > li")  # layout 1

        if len(li_list) > 0:
            # example layout 1 - https://www.tenniswarehouse-europe.com/stringbrands.html
            self.logger.info(f"Layout 1 matched {url}")
            for li in li_list:
                url = li.xpath("./a/@href")

                yield response.follow(
                    url,
                    callback=self.alternate_parse_product_list,
                )

        self.logger.info("Trying to cycle layout parser...")
        li_list = response.css(".brand_tile")  # layout 2
        if len(li_list) > 0:
            # example layout 2 - https://www.tenniswarehouse-europe.com/apparelmen.html
            self.logger.info(f"Layout 2 matched {url}")
            for li in li_list:
                url = xpath("ancestor::a/@href").get()
                if not url:
                    url = li.xpath("@href")

                url = absolute_url_helper(url)

                yield response.follow(
                    url=url,
                    callback=self.alternate_parse_product_list,
                )

        self.logger.info("Trying to cycle layout parser...")
        li_list = response.css(".brands_block-cell")  # layout 3
        if len(li_list) > 0:
            # example layout 3 - https://www.tenniswarehouse-europe.com/catpage-PADEL.html
            self.logger.info(f"Layout 3 matched {url}")
            for li in li_list:
                url = li.xpath("@href")

                yield response.follow(
                    url=url,
                    callback=self.alternate_parse_product_list,
                )
        self.logger.info("No Layout Found")
        # if there is no match
        # simply try alternate parser and exit
        yield self.alternate_parse_product_list(response)

    def alternate_parse_product_list(self, response):
        """an parser for a alternate layout to the one in parse_product_list"""
        card_list = response.css(".product_wrapper")
        for card in card_list:
            l = ItemLoader(item=Item(), selector=card)

            name = card.css(".name > a::text")
            url = card.css(".name > a::attr(href)")

            if not name:
                # if not set means name/url under different element
                name = card.css(".name::text")
                url = card.css(".name::attr(href)")

            l.add_css("name", name)
            l.add_css("url", url)

            prices_list = card.css(".convert_price::text").getall()
            prices_string = ";".join(prices_list)
            l.add_value("prices", prices_string)

            l.add_css("sale_tags", "span.producttag::text")

            yield l.load_item()

    def absolute_url_helper(self, url):
        # some urls contain domain others do not
        # this method just appends domain to the start
        if len(url.split("/")) < 3:
            self.logger.info(f"urlhelper called: {url}")
            url = self.start_urls[0] + url

        return url
