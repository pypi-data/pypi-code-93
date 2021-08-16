import pandas as pd

from ovretl.prices_utils.sum_multiple_billings_prices import sum_multiple_billings_prices


def add_initial_category_prices_to_shipments(
    shipments_with_prices: pd.DataFrame, prices_propositions_by_category_df: pd.DataFrame,
) -> pd.DataFrame:
    initial_prices = (
        prices_propositions_by_category_df.drop(["count"], axis=1, errors="ignore")
        .dropna(subset=["purchase_price_in_eur", "price_in_eur", "margin_price_in_eur", "proposition_id",], how="all",)
        .rename(
            columns={
                "purchase_price_in_eur": "initial_purchase_price_in_eur",
                "price_in_eur": "initial_price_in_eur",
                "margin_price_in_eur": "initial_margin_price_in_eur",
                "proposition_id": "initial_proposition_id",
            }
        )
    )

    shipments_with_prices = pd.merge(
        shipments_with_prices,
        initial_prices[
            [
                "initial_proposition_id",
                "category",
                "initial_margin_price_in_eur",
                "initial_price_in_eur",
                "initial_purchase_price_in_eur",
            ]
        ],
        on=("initial_proposition_id", "category"),
        how="left",
    )
    return shipments_with_prices


def add_category_prices_to_shipments(
    shipments_with_prices_ids: pd.Series,
    prices_final_check_by_category_df: pd.DataFrame,
    prices_billings_by_category_df: pd.DataFrame,
    prices_propositions_by_category_df: pd.DataFrame,
) -> pd.DataFrame:
    shipments_with_prices = pd.merge(
        shipments_with_prices_ids,
        prices_final_check_by_category_df.dropna(subset=["price_in_eur", "final_check_id"], how="any"),
        on="final_check_id",
        how="left",
    )

    shipments_with_prices_full = shipments_with_prices[~shipments_with_prices["price_in_eur"].isnull()]
    shipments_with_prices_uncomplete = shipments_with_prices[shipments_with_prices["price_in_eur"].isnull()].drop(
        [
            "category",
            "price_in_eur",
            "vat_price_in_eur",
            "margin_price_in_eur",
            "purchase_price_in_eur",
            "prices_origin",
        ],
        axis=1,
    )

    shipments_with_prices_uncomplete = pd.merge(
        shipments_with_prices_uncomplete,
        prices_billings_by_category_df.dropna(subset=["price_in_eur", "billing_id"], how="any"),
        on="billing_id",
        how="left",
    )

    shipments_with_prices = pd.concat([shipments_with_prices_full, shipments_with_prices_uncomplete], sort=False)
    shipments_with_prices_full = shipments_with_prices[~shipments_with_prices["price_in_eur"].isnull()]
    shipments_with_prices_uncomplete = shipments_with_prices[shipments_with_prices["price_in_eur"].isnull()].drop(
        [
            "category",
            "price_in_eur",
            "vat_price_in_eur",
            "margin_price_in_eur",
            "purchase_price_in_eur",
            "prices_origin",
        ],
        axis=1,
    )

    shipments_with_prices_uncomplete = pd.merge(
        shipments_with_prices_uncomplete,
        prices_propositions_by_category_df.dropna(subset=["price_in_eur", "proposition_id"], how="any"),
        on="proposition_id",
        how="left",
    )

    shipments_with_prices = pd.concat([shipments_with_prices_full, shipments_with_prices_uncomplete], sort=False)

    shipments_with_prices = add_initial_category_prices_to_shipments(
        shipments_with_prices=shipments_with_prices,
        prices_propositions_by_category_df=prices_propositions_by_category_df,
    )

    return sum_multiple_billings_prices(shipments_with_prices=shipments_with_prices)
