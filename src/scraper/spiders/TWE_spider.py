import scrapy
from scrapy import Request, FormRequest


class TWE_Spider(scrapy.Spider):
    name = "tennis-warehouse-europe"

    start_urls = ["https://www.tenniswarehouse-europe.com"]
    allowed_domains = ["tenniswarehouse-europe.com"]

    def start_requests(self):
        # set the cookie
        self.logger.info("Setting cookie")
        return [
            FormRequest(
                "https://www.tenniswarehouse-europe.com",
                formdata={"lang": "en", "vat": "GR"},
            )
        ]

    def parse(self, response):
        self.logger.info("Parse called on %s", response.url)
        categories = response.xpath("//nav/li/a")

        # nav bar links
        for item in categories:
            url = item.xpath("@href").get()
            category = item.xpath("text()").get()

            absoluteUrlHelper(url)

            self.logger.info("\t %s : %s", category, url)
            yield Request(
                url,
                callback=self.parse_products,
                cb_kwargs=dict(category=category),
            )

    def absoluteUrlHelper(self, url):
        # some urls contain domain others do not
        # this method just appends domain to the start
        if len(url.split("/")) < 3:
            url = self.start_urls[0] + url

        self.logger.info("urlhelper called : %s returned", url)
        return url

    def parse_products(self, response, category):
        # only keep rows with rackets
        product_card_list = response.xpath("//table/tr/td[@class='cat_border_cell']")

        print(product_card_list[0])
