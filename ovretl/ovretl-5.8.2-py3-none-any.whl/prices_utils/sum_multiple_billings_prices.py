import pandas as pd


def sum_multiple_billings_prices(shipments_with_prices: pd.DataFrame):
    return (
        shipments_with_prices.groupby(["shipment_id", "category"])
        .agg(
            {
                "price_in_eur": "sum",
                "vat_price_in_eur": "sum",
                "margin_price_in_eur": "sum",
                "purchase_price_in_eur": "sum",
                "initial_price_in_eur": "sum",
                "initial_purchase_price_in_eur": "sum",
                "initial_margin_price_in_eur": "sum",
                "prices_origin": "first",
                "foresea_name": "first",
            }
        )
        .reset_index()
    )
