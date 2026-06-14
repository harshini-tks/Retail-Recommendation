from langchain.tools import tool
from src.services.llm_service import get_llm
from src.services.recommendation_service import get_product_recommendations_data
from src.tools.comparison_tool import compare_products
from src.utils.helpers import format_product_card, safe_llm_call

@tool
def get_product_recommendations(
    user_id: str = "",
    style_pref: str = "",
    budget_min: float = 0,
    budget_max: float = 99999,
    brand_pref: str = "",
    size: str = "",
    colour_pref: str = "",
    category_pref: str = "",
) -> str:
    """
    Recommends personalised products based on shopper profile, budget, and style.
    """
    df, prefs = get_product_recommendations_data(
        user_id, style_pref, budget_min, budget_max, brand_pref, size, colour_pref, category_pref
    )
    
    # 1. Profile Context
    profile_ctx = f"Style: {style_pref}, Budget Max: {budget_max}, Brand Pref: {brand_pref}, Category: {category_pref}, Colour Pref: {colour_pref}"
    
    # 2. Batch Reasoning via LLM
    product_list_str = "\n".join([f"- {row['name']} ({row['brand']}): {row['style']} style, {row['colour']}, Price: ₹{row['price']}" for _, row in df.iterrows()])
    
    reasoning_prompt = f"""You are RA7, a professional retail stylist.
For the following 5 products and user profile, generate a short (max 12 words) POSITIVE reason why this product was selected for this user.
Focus on the strongest fit (design, budget, brand, or color).

RULES:
1. NEVER say a product 'doesn't fit' or mention a mismatch.
2. If style differs, focus on its versatility or great price point.
3. Use a friendly, endorsing tone.

USER PROFILE: {profile_ctx}

PRODUCTS:
{product_list_str}

Return your response as a numbered list only."""
    
    llm = get_llm(temperature=0.2)
    batch_reasons_raw = safe_llm_call(llm, reasoning_prompt, fallback="")
    
    # Parse LLM response into a list
    ai_reasons = []
    if batch_reasons_raw:
        ai_reasons = [line.split(".", 1)[-1].strip() for line in batch_reasons_raw.strip().split("\n") if "." in line]

    if df.empty:
        return "No products found matching the given criteria. Try widening your budget."

    style_pref = prefs["style_pref"]
    brand_pref = prefs["brand_pref"]
    colour_pref = prefs["colour_pref"]
    
    lines = ["### Personalised Product Recommendations"]
    for i, (_, row) in enumerate(df.iterrows()):
        # Use AI-generated reason if available, else fallback to template
        if i < len(ai_reasons):
            reason_str = ai_reasons[i]
        else:
            reasons = []
            if style_pref and row["style"].lower() == style_pref.lower():
                reasons.append(f"matches your {style_pref} style")
            if brand_pref and row["brand"].lower() == brand_pref.lower():
                reasons.append(f"your preferred brand {brand_pref}")
            reason_str = "; ".join(reasons) if reasons else "Selected for your specific profile and budget."

        card_lines = format_product_card(idx=i+1, product=row, reason=reason_str, header_level="####")
        lines.extend(card_lines)
        lines.append("")
        
        try:
            alt_res = compare_products.invoke({"product_id": row["product_id"]})
            # Remove the first 2 lines of alternate which is exactly the same as the current product to save space
            alt_lines = alt_res.split("\n")[3:]
            lines.append("##### Alternatives")
            lines.extend(alt_lines)
        except Exception:
            pass

    lines.append("")
    lines.append("> **How we calculate your score (Max 10):** Style (+4), Brand (+3), Color (+2), In Stock (+1).")
    lines.append(" *Recommendations are suggestions only. Prices & availability may vary.*")
    return "\n".join(lines)
