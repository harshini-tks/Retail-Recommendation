"""
Social Influence Tool
Analyses what peers/friends of the user are buying.
"""
from langchain.tools import tool
from src.services.social_service import get_social_insights
from src.utils.helpers import format_markdown_table

@tool
def get_social_recommendations(user_id: str) -> str:
    """
    Finds what the user's social network (friends, classmates, colleagues,
    family, neighbours) are buying based on shared area/school sales trends.

    Args:
        user_id: The user's unique identifier (e.g., 'U001')
    Returns:
        A summary of what peers in the user's network are purchasing.
    """
    insights = get_social_insights(user_id)
    if "error" in insights:
        return insights["error"]
        
    merged = insights["trending_products"]
    lines = [f"### Peer Insights for {user_id}"]
    lines.append(f"**Connections:** {', '.join(insights['connections'])}")
    lines.append("")
    lines.append("#### What your network is buying")

    headers = ["Product", "Brand", "Colour", "Price", "Demand"]
    rows = []
    for _, row in merged.iterrows():
        name = row.get("name", row["product_id"])
        colour = row.get("colour", "")
        brand = row.get("brand", "")
        price = row.get("price", "")
        sold = row["units_sold"]
        rows.append([name, brand, colour, f"₹{price}", f"**{sold}**"])
        
    lines.extend(format_markdown_table(headers, rows))

    styles = insights.get("style_preferences", [])
    if styles:
        lines.append("")
        lines.append(f" **Peer Style Preferences:** {', '.join(styles)}")

    return "\n".join(lines)
