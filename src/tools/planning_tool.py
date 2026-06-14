from langchain.tools import tool
from src.services.planning_service import get_next_purchases
from src.utils.helpers import format_product_card

@tool
def plan_next_purchases(category: str, style: str, budget_max: float = 99999) -> str:
    """
    Suggests the next 2–3 likely purchases that complement a chosen
    product category, maintaining style consistency and budget fit.

    Args:
        category:   Category of the product just chosen (e.g., 'Topwear')
        style:      Style of the product (e.g., 'Casual', 'Ethnic')
        budget_max: User's maximum budget for future purchases
    Returns:
        A shopping plan with 2–3 complementary product suggestions.
    """
    picks = get_next_purchases(category, style, budget_max)
    
    if not picks:
        return "No complementary products found within your budget."
        
    lines = ["##### Next Likely Purchases"]
    for i, pick in enumerate(picks, 1):
        card_lines = format_product_card(
            idx=i, 
            product=pick, 
            reason="A natural complement to your current selections.", 
            header_level=""
        )
        lines.extend(card_lines)
        
    return "\n".join(lines)
