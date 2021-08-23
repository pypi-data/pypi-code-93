#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `grabclient` package."""

import pytest
# from grabclient.client import GrabClient
# from grabclient.common import Package, ServiceType, Origin, Destination, QuoteParam, \
#     Dimensions, Currency, Coordinates, CurrencyCode
# from grabclient.requests import DeliveryQuoteRequest
#
# import dotenv
# import os
#
# dotenv.load_dotenv()


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # grab_url = os.getenv("GRAB_SANDBOX_URL")
    # grab_oauth_url = os.getenv("GRAB_OAUTH_URL")
    # client_id = os.getenv("CLIENT_ID")
    # client_secret = os.getenv("CLIENT_SECRET")
    # redis_url = os.getenv("REDIS_URL")
    # redis_password = os.getenv("REDIS_PASSWORD")
    # client = GrabClient((client_id, client_secret), grab_url, grab_oauth_url, redis_url, True, redis_password)
    # dimensions = Dimensions(
    #     height=0,
    #     width=0,
    #     depth=0,
    #     weight=0,
    # )
    # currency = Currency(
    #     code=CurrencyCode.idr,
    #     symbol="Rp.",
    #     exponent=0,
    # )
    # package = Package(name="Fish Burger", description="Fish Burger with mayonnaise sauce", quantity=2, price=5,
    #                   dimensions=dimensions, currency=currency)
    # quotes = [package]
    #
    # coor = Coordinates(
    #     latitude= 1.2345876,
    #     longitude= 3.4567098
    # )
    # destination = Destination(
    #     address= "1 ABC St, Singapore 078881",
    #     keywords= "XYZ Tower",
    #     coordinates=coor
    # )
    # origin = Origin(
    #     address="1 IJK View, Singapore 018936",
    #     keywords="PQR Tower",
    #     coordinates=coor
    # )
    # request = DeliveryQuoteRequest(
    #     service_type=ServiceType.instant,
    #     origin=origin,
    #     destination=destination,
    #     packages=quotes,
    # )
    # client.check_rate(req=request)
    pass


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    pass
