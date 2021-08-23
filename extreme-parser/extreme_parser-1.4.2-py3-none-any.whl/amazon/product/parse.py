import re
from typing import Union

import pandas
import parsel

from extreme_parser.amazon.product.model import Product
from extreme_parser.util.parse import parse_number


def parse(html: str, p: Product):
    sel = parsel.Selector(text=html)
    parse_weight(p, selector=sel)
    parse_brand(p, selector=sel)
    parse_price(p, selector=sel)
    parse_in_stock(p, selector=sel)
    parse_ship(p, selector=sel)
    parse_delivery(p, selector=sel)


def parse_weight(p: Product, html: str = None, selector: parsel.Selector = None):
    def s1() -> str:
        table = selector.xpath(
            "//table[@id='productDetails_detailBullets_sections1']|"
            "//table[@id='productDetails_techSpec_section_1']"
        ).get()
        if table is None:
            return ""
        table = pandas.read_html(table)
        if len(table) <= 0:
            return ""
        table = table[0].set_index(0)
        if "Item Weight" not in table[1]:
            return ""
        s = table[1]["Item Weight"]
        return s

    def s2() -> str:
        ul = selector.xpath("//div[@id='detailBullets_feature_div']/ul")
        s = ul.xpath("//span[contains(text(), 'Item Weight')]/following-sibling::span[1]/text()").get()
        s = s or ul.xpath(
            "substring-after(//span[contains(text(), 'Product Dimensions')]/following-sibling::span[1]/text(), '; ')"
        ).get("")
        return s

    weight_str = s1() or s2()
    if weight_str == "":
        p.weight = None
        return
    weight: Union[None, int, float] = parse_number(weight_str)
    if weight is None:
        p.weight = None
        return

    if weight_str.endswith("ounces") or weight_str.endswith("Ounces"):
        p.weight = weight * 0.0625
    elif weight_str.endswith("pounds") or weight_str.endswith("Pounds"):
        p.weight = float(weight)
    else:
        p.weight = None
        return


def parse_brand(p: Product, html: str = None, selector: parsel.Selector = None):
    def s1() -> str:
        table = selector.xpath("//div[@id='productOverview_feature_div']//table").get()
        if table is None:
            return ""
        table = pandas.read_html(table)
        if len(table) <= 0:
            return ""
        table = table[0].set_index(0)
        if "Brand" not in table[1]:
            return ""
        s = table[1]["Brand"]
        return s

    def s2() -> str:
        s = selector.xpath("//a[@id='bylineInfo']/text()").re_first("Brand: (.*)")
        s = s or selector.xpath("//a[@id='bylineInfo']/text()").re_first("Visit the (.*) Store")
        return s

    brand = s1() or s2()
    if brand == "":
        p.brand = None
        return

    p.brand = brand


def parse_price(p: Product, html: str = None, selector: parsel.Selector = None):
    s = selector.xpath("//span[@id='priceblock_ourprice']/text()").get()
    s = s or selector.xpath("//span[@id='priceblock_saleprice']/text()").get()
    s = s or selector.xpath("//span[@id='priceblock_dealprice']/text()").get()
    s = s or selector.xpath("//div[@id='buyNew_noncbb']/span/text()").get()
    s = s or selector.xpath("//*[@id='color_name_0_price']/span/text()[last()]").get()
    if s is None:
        p.price_min = None
        p.price_max = None
        return

    prices: Union[None, list] = parse_number(s, first=False)
    if prices is None or len(prices) == 0:
        p.price_min = None
        p.price_max = None
    elif len(prices) == 1:
        p.price_min = None
        p.price_max = float(prices[0])
    else:
        p.price_min = float(prices[0])
        p.price_max = float(prices[1])


def parse_in_stock(p: Product, html: str = None, selector: parsel.Selector = None):
    in_stock = selector.xpath("//div[@id='availability']/span/text()").get()
    if in_stock is None:
        p.in_stock = None
        return

    in_stock = in_stock.strip()
    if (
        in_stock == "In Stock." or
        in_stock.startswith("Only") or
        in_stock.startswith("Usually") or
        in_stock.startswith("Available")
    ):
        p.in_stock = True
    elif in_stock in ["In stock soon.", "Currently unavailable.", "Temporarily out of stock.", ""]:
        p.in_stock = False
    else:
        p.in_stock = None


def parse_ship(p: Product, html: str = None, selector: parsel.Selector = None):
    table = selector.xpath("//table[@id='tabular-buybox-container']").get()
    if table is None:
        p.ship = None
        return
    table = pandas.read_html(table)
    if len(table) <= 0:
        p.ship = None
        return
    table = table[0].set_index(0)
    if "Ships from" not in table[1]:
        p.ship = None
        return
    p.ship = table[1]["Ships from"]


def parse_delivery(p: Product, html: str = None, selector: parsel.Selector = None):
    delivery = selector.xpath("string(//div[@id='contextualIngressPtLabel_deliveryShortLine'])").get()
    if delivery is None:
        p.delivery = None
        return
    if delivery == "Select delivery location":
        p.delivery = "US"
        return
    if not delivery.startswith("Deliver to"):
        p.delivery = None
        return

    delivery = re.search(r"Deliver to\s(.*)", delivery)
    if delivery is None:
        p.delivery = None
    else:
        p.delivery = delivery.group(1)
