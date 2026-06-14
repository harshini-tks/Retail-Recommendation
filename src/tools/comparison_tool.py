"""
Comparative Suggestion Tool
Given a product, provides 2–3 alternatives comparing style, price, and brand.
"""
from langchain.tools import tool
from src.services.comparison_service import get_comparisons
from src.utils.helpers import format_markdown_table

@tool
def compare_products(product_id: str = "", product_name: str = "") -> str:
    """
    For a given product (by ID or name), finds 2–3 alternatives
    in the same category and compares them on style, price, and brand.

    Args:
        product_id:   Product ID (e.g., 'P001')
        product_name: Product name (partial match supported)
    Returns:
        A comparison table of the original product vs alternatives.
    """
    ref_row, selected = get_comparisons(product_id, product_name)

    if ref_row is None:
        return f"Product '{product_id or product_name}' not found in catalog."
    
    category = ref_row["category"]
    ref_price = float(ref_row["price"])

    if selected.empty:
        return f"No alternatives found for {ref_row['name']} in category {category}."

    lines = [
        f"**Comparative Suggestions for: {ref_row['name']}**",
        f"   (Original: {ref_row['brand']} | {ref_row['style']} | ₹{ref_price} | {ref_row['colour']})",
        "",
    ]
    
    headers = ["#", "Product", "Brand", "Style", "Colour", "Price", "Stock"]
    rows = []

    for i, (_, alt) in enumerate(selected.iterrows(), 1):
        diff = float(alt["price"]) - ref_price
        diff_str = f"+₹{diff:.0f}" if diff >= 0 else f"-₹{abs(diff):.0f}"
        rows.append([
            str(i), alt['name'], alt['brand'], alt['style'], 
            alt['colour'], f"₹{alt['price']} ({diff_str})", alt['stock_status']
        ])
        
    lines.extend(format_markdown_table(headers, rows))

    return "\n".join(lines)
