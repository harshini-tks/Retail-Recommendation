"""
Event Awareness Tool
Checks upcoming festivals, school events, and seasonal sales
and maps them to relevant product categories.
"""
from langchain.tools import tool
from src.services.event_service import get_event_suggestions
from src.utils.helpers import format_event_card

@tool
def get_event_recommendations(area: str, days_ahead: int = 60) -> str:
    """
    Checks upcoming events relevant to the user's area and recommends
    product categories aligned with those occasions.

    Args:
        area: User's residential area (e.g., 'Koramangala')
        days_ahead: How many days ahead to look for events (default 60)
    Returns:
        A summary of upcoming events and relevant product categories.
    """
    suggestions = get_event_suggestions(area, days_ahead)

    if not suggestions:
        return f"No upcoming events found in the next {days_ahead} days for {area}."

    lines = [f"### Upcoming Occasions for {area}"]
    for item in suggestions:
        event = item["event"]
        sample = item["sample_products"]
        
        name = event["name"]
        event_type = event.get("type", "")
        days = event.get("days_until", "?")
        categories = event.get("category_relevance", [])

        lines.extend(format_event_card(name, days, event_type, categories, sample))

    return "\n".join(lines)
