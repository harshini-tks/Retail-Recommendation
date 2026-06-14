import pandas as pd
from src.utils.data_loader import load_products

NEXT_PURCHASE_MAP = {
    "Topwear": ["Bottomwear", "Footwear", "Accessories"],
    "Bottomwear": ["Footwear", "Topwear", "Accessories"],
    "Footwear": ["Accessories", "Topwear"],
    "Accessories": ["Topwear", "Bottomwear"],
    "Ethnic Wear": ["Footwear", "Accessories"],
}

def get_next_purchases(category: str, style: str, budget_max: float = 99999) -> list[pd.Series]:
    """
    Suggests next complementary purchases based on category/style mappings.
    Returns a list of Pandas Series objects representing the products.
    """
    products = load_products()
    next_cats = NEXT_PURCHASE_MAP.get(category, ["Footwear", "Accessories"])
    
    plan_count = 0
    picks = []

    for cat in next_cats[:3]:
        cat_products = products[
            (products["category"] == cat)
            & (products["stock_status"] != "Out of Stock")
            & (products["price"] <= budget_max)
        ]
        style_match = cat_products[cat_products["style"].str.lower() == style.lower()]
        pool = style_match if not style_match.empty else cat_products

        if pool.empty:
            continue

        pick = pool.sample(1, random_state=plan_count).iloc[0]
        plan_count += 1
        
        pick_dict = pick.copy()
        pick_dict['recommended_category'] = cat
        picks.append(pick_dict)

        if plan_count >= 3:
            break
            
    return picks
