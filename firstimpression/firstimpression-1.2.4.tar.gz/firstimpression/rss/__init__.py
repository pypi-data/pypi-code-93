from firstimpression.api.request import request
import xml.etree.ElementTree as ET


def get_feed(url):
    response = request(url)
    return ET.fromstring(response.content)
