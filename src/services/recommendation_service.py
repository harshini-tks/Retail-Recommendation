import pandas as pd
from src.utils.data_loader import load_products, load_users

def get_product_recommendations_data(
    user_id: str = "",
    style_pref: str = "",
    budget_min: float = 0,
    budget_max: float = 99999,
    brand_pref: str = "",
    size: str = "",
    colour_pref: str = "",
    category_pref: str = "",
) -> tuple[pd.DataFrame, dict]:
    """
    Core business logic to pull users, products, filter by budget and stock,
    and score products based on style, brand, and colour preferences.
    """
    products = load_products()

    if user_id:
        users = load_users()
        u = users[users["user_id"] == user_id]
        if not u.empty:
            row = u.iloc[0]
            style_pref = style_pref or str(row.get("style_pref", ""))
            budget_min = budget_min or float(row.get("budget_min", 0))
            budget_max = budget_max or float(row.get("budget_max", 99999))
            brand_pref = brand_pref or str(row.get("brand_pref", ""))
            colour_pref = colour_pref or str(row.get("colour_pref", ""))

    df = products[products["stock_status"] != "Out of Stock"].copy()
    df = df[(df["price"] >= budget_min) & (df["price"] <= budget_max)]

    df["score"] = 0
    
    if style_pref:
        df.loc[df["style"].str.lower() == style_pref.lower(), "score"] += 4
    if brand_pref:
        df.loc[df["brand"].str.lower() == brand_pref.lower(), "score"] += 3
    if colour_pref:
        df.loc[df["colour"].str.lower() == colour_pref.lower(), "score"] += 2
        
    df.loc[df["stock_status"] == "In Stock", "score"] += 1

    df = df.sort_values("score", ascending=False).head(5)
    
    prefs = {
        "style_pref": style_pref,
        "brand_pref": brand_pref,
        "colour_pref": colour_pref,
        "category_pref": category_pref
    }
    
    return df, prefs
