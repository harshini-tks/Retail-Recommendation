import pandas as pd
from src.utils.data_loader import load_sales_trends, load_products


def get_local_trends(area: str, school: str = "") -> dict:
    trends = load_sales_trends()
    products = load_products()

    area_trends = trends[trends["area"].str.lower() == area.lower()]

    school_trends = pd.DataFrame()
    if school:
        school_trends = area_trends[
            area_trends["school"].str.lower() == school.lower()
        ]

    focus = school_trends if not school_trends.empty else area_trends

    if focus.empty:
        return {"error": f"No trend data available for area '{area}'."}

    agg = focus.groupby("product_id")["units_sold"].sum().reset_index()
    agg = agg.sort_values("units_sold", ascending=False).head(5)
    merged = agg.merge(products, on="product_id", how="left")

    colour_agg = focus.groupby("colour")["units_sold"].sum().reset_index()
    colour_agg = colour_agg.sort_values("units_sold", ascending=False)
    top_colour = colour_agg.iloc[0]["colour"] if not colour_agg.empty else "N/A"

    return {
        "scope": f"{school}, {area}" if school else area,
        "top_colour": top_colour,
        "trending_products": merged
    }
