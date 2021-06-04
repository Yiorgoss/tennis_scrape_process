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

        url_list = response.css("ul.lnav_section").xpath("./li/a/@href")

        for url in url_list.getall():
            url = self.absolute_url_helper(url)
            yield response.follow(url, callback=self.parse_product_list)

    def parse_product_list(self, response):
        product_card_list = response.css("td.cat_border_cell")

        for card in product_card_list:
            # try and parse relevant info from catelog page
            # else try from product page
            l = ItemLoader(item=Item(), selector=card)

            url = card.css(".name::attr(href)").get()
            name = card.css(".name::text").get()

            l.add_css("url", ".name::attr(href)")
            l.add_css("name", ".name::text")

            prices_list = card.css(
                ".convert_price::text"
            ).getall()  # this will be an array of 1-3 values

            prices_string = ";".join(prices_list)
            # cant join with comma because greek prices use , instaed of .
            l.add_value("prices", prices_string)
            # l.add_value("prices", ["1", "2", "3"])

            sale_classes = card.css(".name").attrib["class"]
            l.add_value("sale_tags", sale_classes)

            yield l.load_item()

            # url = card.css(".name::attr(href)").get()
            # item["name"] = card.css(".name::text").get()
            # item["url"] = url

            # price, previous_price, price_for_two = self.prices_to_csv(prices_list)

            #    logger.warning(
            #        "Parsing from catalog page failed, attempting product page parse."
            #    )
            #    yield Request(url, callback=self.parse_product_page)

    def absolute_url_helper(self, url):
        # some urls contain domain others do not
        # this method just appends domain to the start
        if len(url.split("/")) < 3:
            url = self.start_urls[0] + url

        self.logger.debug("urlhelper called : %s returned", url)
        return url

    # def parse_product_page(self, response, category):
    #     # parse the individual product page
    #     # product info
    #     item = Item()

    #     item["url"] = response.url

    #     select = Selector(text=product)

    #     name = select.css(".name::text").get()
    #     select.css(".convert_price::text").getall()

    #     price_list = select.css(
    #         ".convert_price::text"
    #     ).getall()  # this will be an array of 1-3 values

    #     prices = price_to_csv(price_list)


# def sale_class_parser(self, class_name_list):
#     # remove name from class list and return value = 1 if exist
#     new, best, sale = 0, 0, 0

#     cname_list = class_name_list.replace("name", "").split(" ")

#     for item in cname_list:
#         if item == "w_new":
#             new = 1
#         if item == "w_best":
#             best = 1
#         if item == "w_sale":
#             sale = 1
#     return new, best, sale

# def prices_to_csv(self, price_list):
#    # prices come in any of 3 forms
#    # price, previous price, and price for two
#    price, prev_price, two_price = -1, -1, -1  # default to -1
#    if len(price_list) == 2:
#        if price_list[0] < price_list[1]:
#            # is of the form price and previous price
#            price = price_list[0]
#            prev_price = price_list[1]
#        if price_list[0] > price_list[1]:
#            # is of the form price and price for two
#            price = price_list[0]
#            two_price = price_list[1]
#    if len(price_list) == 3:
#        # is of the form price, previous price and price for two
#        price = price_list[0]
#        prev_price = price_list[1]
#        two_price = price_list[2]

#    return price, prev_price, two_price


# def parse(self, response):
#     # starting point
#     categories = response.xpath("//nav/ul/li/a")

#     # nav bar links
#     for item in categories:
#         url = item.xpath("@href").get()
#         category = item.xpath("text()").get()

#         url = self.absolute_url_helper(url)

#         yield Request(
#             url,
#             callback=self.parse_product_list,
#             cb_kwargs=dict(category=category),
#         )

# with open("output/tenniswarehouse_stock.csv", "a") as f:
#    f.write(line + "\n")

#        try:

#            prices_list = select.css(
#                ".convert_price::text"
#            ).getall()  # this will be an array of 1-3 values

#            new, best, sale = self.sale_class_parser(
#                select.css(".name").attrib["class"]
#            )

#            line = category + "," + name + ","

#            line += self.prices_to_csv(prices_list)
#            line += new + "," + best + "," + sale
#            line += url

#            with open("output/tenniswarehouse_stock.csv", "a") as f:
#                f.write(line + "\n")
#        except:
#            self.logger.warning(
#                "failed to parse from product page. Attempting product page."
#            )

# yield Request(
#    url,
#    callback=self.parse_product_page,
#    cb_kwargs=dict(category=category),
# )
