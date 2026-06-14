import pandas as pd
from src.utils.data_loader import load_products

def get_comparisons(product_id: str = "", product_name: str = "") -> tuple[pd.Series, pd.DataFrame]:
    """
    Finds a reference product and 2-3 alternatives.
    Returns (ref_row, alternatives_df). 
    If not found, returns (None, pd.DataFrame()).
    """
    products = load_products()

    ref = pd.DataFrame()
    if product_id:
        ref = products[products["product_id"] == product_id]
    if ref.empty and product_name:
        ref = products[
            products["name"].str.lower().str.contains(
                product_name.lower(), na=False
            )
        ]

    if ref.empty:
        return None, pd.DataFrame()

    ref_row = ref.iloc[0]
    category = ref_row["category"]
    style = ref_row["style"]
    ref_price = float(ref_row["price"])

    alts = products[
        (products["category"] == category)
        & (products["brand"] != ref_row["brand"])
        & (products["product_id"] != ref_row["product_id"])
        & (products["stock_status"] != "Out of Stock")
    ]

    style_alts = alts[alts["style"] == style]
    price_alts = alts[
        (alts["price"] >= ref_price * 0.5) & (alts["price"] <= ref_price * 1.5)
    ]
    budget_alt = alts[alts["price"] < ref_price]

    selected = pd.concat([style_alts.head(1), price_alts.head(1), budget_alt.head(1)])
    selected = selected.drop_duplicates(subset=["product_id"]).head(3)

    return ref_row, selected
