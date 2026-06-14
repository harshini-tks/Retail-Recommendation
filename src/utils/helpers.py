import pandas as pd

def safe_tool(tool_fn, args: dict, fallback: str) -> str:
    try:
        return tool_fn.invoke(args)
    except Exception as exc:
        return f"{fallback} (Error: {exc})"

def safe_llm_call(llm, prompt: str, fallback: str = "") -> str:
    try:
        return llm.invoke(prompt)
    except Exception as exc:
        if fallback:
            return fallback
        return (
            f"LLM unavailable ({exc}). "
            "Please ensure Ollama is running: `ollama serve` and model is pulled."
        )

def format_event_card(event_name: str, days_until: str | int, event_type: str, categories: list[str], sample_products) -> list[str]:
    """Formats an event and its sample products into a markdown block."""
    lines = [
        "",
        f"  **{event_name}**",
        f"**When:** {days_until} days from now  ",
        f"**Type:** {event_type}  ",
        f"**Look for:** {', '.join(categories)}"
    ]
    if not sample_products.empty:
        lines.append("    **Suggested items:**")
        for _, p in sample_products.iterrows():
            lines.append(f"   - {p['name']} ({p['brand']}) — ₹{p['price']}")
    return lines

def format_trend_header(scope: str, top_colour: str) -> list[str]:
    return [
        f" **Local Trends for {scope}**",
        f" Top Colour: **{top_colour}**",
        ""
    ]

def format_product_card(idx: int, product: dict | object, reason: str = "", header_level: str = "####") -> list[str]:
    """Formats a single product as a markdown card (list of lines)."""
    def _get(key, default=""):
        if hasattr(product, "get") and callable(product.get):
            val = product.get(key, None)
            if pd.notna(val) if pd is not None and hasattr(pd, "notna") else val is not None:
                return val
        if hasattr(product, "__getitem__"):
            try:
                return product[key]
            except (KeyError, TypeError):
                pass
        return getattr(product, key, default) if hasattr(product, key) else default

    name_line = f"{header_level} {idx}. {_get('name')} ({_get('brand')})  " if header_level else f"**{idx}. {_get('name')} ({_get('brand')})**  "
    
    lines = [
        "",
        "---",
        name_line,
        f"**Price:** ₹{_get('price')}  ",
        f"**Category:** {_get('category', 'N/A')} | **Style:** {_get('style', 'N/A')}  ",
        f"**Colour:** {_get('colour', 'N/A')} | **Stock:** {_get('stock_status', 'In Stock')}  ",
        #f"**Match Score:** {int(_get('score', 0))}/10  ",
    ]
        
    if reason:
        lines.append(f"**Why:** {reason}  ")
        
    return lines

def format_markdown_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Formats a markdown table from a list of headers and list of row lists."""
    lines = [
        f"| {' | '.join(headers)} |",
        f"| {' | '.join([':---' for _ in headers])} |"
    ]
    for row in rows:
        lines.append(f"| {' | '.join(str(item) for item in row)} |")
    return lines
