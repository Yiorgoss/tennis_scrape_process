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
                callback=self.parse_products_list,
                cb_kwargs=dict(category=category),
            )

    def absoluteUrlHelper(self, url):
        # some urls contain domain others do not
        # this method just appends domain to the start
        if len(url.split("/")) < 3:
            url = self.start_urls[0] + url

        self.logger.info("urlhelper called : %s returned", url)
        return url

    def parse_product_list(self, response, category):
        # drop advert rows and follow product urls
        product_url_list = response.xpath(
            "//table/tr/td/[contains(concat(' ',normalize-space(@class),' '),' cat_border_cell ')]/div/div/a/@href"
        )

        for url in product_card_list:
            yield Request(
                url, callback=self.parse_product_page, cb_kwargs=dict(category=category)
            )

    def parse_product_page(self, response, category):
        pass
