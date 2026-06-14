import pandas as pd
from src.utils.data_loader import get_upcoming_events, load_products

def get_event_suggestions(area: str, days_ahead: int = 60) -> list[dict]:
    events = get_upcoming_events(days_ahead=days_ahead)
    products = load_products()

    relevant = [
        e for e in events
        if e.get("area", "All") == "All"
        or e.get("area", "").lower() == area.lower()
    ]

    results = []
    for event in relevant[:5]:
        categories = event.get("category_relevance", [])
        cat_products = products[products["category"].isin(categories)]
        cat_products = cat_products[cat_products["stock_status"] != "Out of Stock"]
        sample = cat_products.sample(min(2, len(cat_products)), random_state=42) if not cat_products.empty else pd.DataFrame()
        
        results.append({
            "event": event,
            "sample_products": sample
        })
    return results
