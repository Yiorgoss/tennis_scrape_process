import scrapy
from scrapy import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join, Identity

from w3lib.html import remove_tags
import re


def price_string_to_float(price_string_list):
    # remove everything that isnt a number or a decimal
    result = []

    price_list = price_string_list.split(",")

    for price_string in price_list:

        trim = re.compile(r"[^\d\.]+")
        trimmed = trim.sub("", price_string).strip()

        result.append(float(trimmed))

    return result


def sale_tag_parser(string):
    # determine if this is from a class name or from text
    string = string.strip()
    if len(string.split(" ")) == 1:
        # single class name
        return single_sale_tag_parser(string)
    else:
        # multiple tags or no tags
        return multiple_sale_tag_parser(string)


def single_sale_tag_parser(string):
    new, best, sale = "0", "0", "0"
    if string == "New":
        new = "1"
    elif string == "Best Seller":
        best = "1"
    elif string == "Sale":
        sale == "1"

    return new, best, sale


def multiple_sale_tag_parser(class_names):
    # remove name classname check if there are anymore
    # will be zero or more of the following 3
    new, best, sale = "0", "0", "0"
    cname_list = class_names.replace("name", "").strip().split(" ")

    if not isinstance(cname_list, list):
        cname_list = [cname_list]

    for cname in cname_list:
        if cname == "w_new":
            new = 1
        if cname == "w_best":
            best = 1
        if cname == "w_sale":
            sale = 1

    return new, best, sale


def remove_currency(value):
    # anything that isnt a number or a decimal or item split char gtfo
    trim = re.compile(r"[^\d\.;]+")
    trimmed = trim.sub("", value)

    return trimmed


def clean_string(value):

    value = value.replace(" ", "")
    value = value.replace(",", ".")

    value = remove_currency(value)
    return value


def price_parser(price_list_string):
    # prices come in any of 3 forms
    # price, previous price, and price for two

    price, prev_price, two_price = 0, 0, 0

    price_list = price_list_string.split(";")
    price_list = [float(i) for i in price_list]

    if len(price_list) >= 1:
        # incase there is no price value
        price = price_list[0]

    if len(price_list) == 2:
        # when there are two kinds of price
        if price < price_list[1]:
            # price < other_price
            # implying price and previous_price
            prev_price = price_list[1]
        else:
            # price > other_price
            # implying price and quantity price (price for two)
            two_price = price_list[1]

    if len(price_list) == 3:
        # one of each price
        prev_price = price_list[1]
        two_price = price_list[2]

    price_arr = [price, prev_price, two_price]
    if len(price_arr) == 2:
        raise Exception(price_arr)
    # return ",".join(str(x) for x in price_arr)
    return price_arr


def racquet_replace(string):
    return string.replace("racket", "racquet")


class Item(scrapy.Item):
    name = Field(
        input_processor=MapCompose(
            remove_tags,
            str.lower,
            racquet_replace,
            str.strip,
        ),
    )

    prices = Field(
        input_processor=MapCompose(
            clean_string,
            price_parser,
        ),
    )
    sale_tag = Field(
        input_processor=MapCompose(
            remove_tags,
            str.strip,
        ),
    )

    url = Field(
        input_processor=MapCompose(
            remove_tags,
            str.strip,
        )
    )
