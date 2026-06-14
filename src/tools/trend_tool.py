"""
Trend Analysis Tool
Answers: What is the highest-selling design/colour in my area or school?
"""
from langchain.tools import tool
from src.services.trend_service import get_local_trends
from src.utils.helpers import format_markdown_table, format_trend_header

@tool
def analyze_local_trends(area: str, school: str = "") -> str:
    """
    Analyzes local sales trends for a given area and optional school.
    Returns top-selling products, colours, and categories.

    Args:
        area: Residential area of the user (e.g., 'Koramangala')
        school: School name of the user (optional)
    Returns:
        A human-readable summary of top trending items.
    """
    trends_data = get_local_trends(area, school)
    if "error" in trends_data:
        return trends_data["error"]
        
    merged = trends_data["trending_products"]
    top_colour = trends_data["top_colour"]
    scope = trends_data["scope"]

    lines = format_trend_header(scope, top_colour)
    lines.append("### Top Trending Products")
    
    headers = ["Product", "Style", "Price", "Sold"]
    rows = []
    for _, row in merged.iterrows():
        name = row.get("name", row["product_id"])
        colour = row.get("colour", "")
        style = row.get("style", "")
        price = row.get("price", "")
        sold = row["units_sold"]
        rows.append([f"{name} ({colour})", style, f"₹{price}", f"**{sold}**"])
        
    lines.extend(format_markdown_table(headers, rows))

    return "\n".join(lines)
