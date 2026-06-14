from src.services.profile_service import ShopperProfile
from src.services.llm_service import get_llm
from src.utils.helpers import safe_tool, safe_llm_call
from src.tools.trend_tool import analyze_local_trends
from src.tools.social_tool import get_social_recommendations
from src.tools.event_tool import get_event_recommendations
from src.tools.recommendation_tool import get_product_recommendations
from src.tools.planning_tool import plan_next_purchases
from src.tools.comparison_tool import compare_products
from src.utils.data_loader import load_products
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

class RecommendationAgent:
    def __init__(self):
        self.llm = get_llm(temperature=0.4)

    # Public entry point
    def run_incremental(self, profile: ShopperProfile):
        """
        Execute the pipeline and yield results as they become available.
        Yields tuples of (key, value).
        """
        results = {"profile_summary": profile.summary(), "disclaimer": (
            "**Disclaimer:** All recommendations are AI-generated suggestions based on "
            "synthetic data. No guaranteed savings are implied. Recommendations are personalised "
            "but not exhaustive. Products shown are for demonstration purposes only. "
            "User data is handled ethically and not shared with third parties."
        )}
        yield "profile_summary", results["profile_summary"]
        yield "disclaimer", results["disclaimer"]

        # Run independent tools in parallel
        with ThreadPoolExecutor(max_workers=6) as executor:
            tasks = {
                executor.submit(safe_tool, analyze_local_trends, {"area": profile.area, "school": profile.school}, "Trend data unavailable."): "trend_insights",
                executor.submit(safe_tool, get_event_recommendations, {"area": profile.area, "days_ahead": 90}, "Event data unavailable."): "event_insights",
                executor.submit(safe_tool, get_product_recommendations, {
                    "user_id": profile.user_id if profile.user_id != "NEW_USER" else "",
                    "style_pref": profile.style_pref, "budget_min": profile.budget_min,
                    "budget_max": profile.budget_max, "brand_pref": profile.brand_pref,
                    "colour_pref": profile.colour_pref, "category_pref": profile.category_pref,
                }, "Recommendations unavailable."): "recommendations",
                executor.submit(safe_tool, plan_next_purchases, {
                    "category": profile.category_pref or "Topwear", "style": profile.style_pref,
                    "budget_max": profile.budget_max,
                }, "Purchase plan unavailable."): "purchase_plan"
            }

            if profile.user_id != "NEW_USER":
                tasks[executor.submit(safe_tool, get_social_recommendations, {"user_id": profile.user_id}, "Social data unavailable.")] = "social_insights"
            else:
                results["social_insights"] = "Social insights not available for new users."
                yield "social_insights", results["social_insights"]

            # Yield tool results as they finish
            for future in as_completed(tasks):
                key = tasks[future] #result name
                try:
                    val = future.result()
                    results[key] = val
                    yield key, val
                except Exception as e:
                    yield key, f"Error: {e}"

        # LLM reasoning synthesis (Streamed)
        yield "llm_reasoning_stream", self._stream_llm_reasoning(profile, results)

    def _stream_llm_reasoning(self, profile: ShopperProfile, results: dict):
        """Ask the LLM to synthesise all tool outputs into a coherent narrative (Streaming)."""
        prompt = f"""You are RA7, a personalised retail shopping assistant AI.
Based on the profile and context below, write a friendly narrative summary.
Limit to 200 words.

=== SHOPPER PROFILE ===
{profile.summary()}

=== DATA CONTEXT ===
Trends: {results.get("trend_insights", "N/A")}
Social: {results.get("social_insights", "N/A")}
Events: {results.get("event_insights", "N/A")}
Top Recs: {results.get("recommendations", "N/A")}

Write a warm, personalised paragraph for {profile.name}:"""
        
        for chunk in self.llm.stream(prompt):
            if hasattr(chunk, "content"):
                yield chunk.content  # High-tech model: Extract the content
            else:
                yield str(chunk)   # Basic model: Just treat the whole thing as text

    def _generate_llm_reasoning(self, profile: ShopperProfile, results: dict) -> str:
        """Ask the LLM to synthesise all tool outputs into a coherent narrative."""
        prompt = f"""You are RA7, a personalised retail shopping assistant AI.

Based on the shopper profile and context below, write a concise, friendly, and insightful 
shopping recommendation narrative (200-250 words). Highlight key reasons for the recommendations,
mention upcoming events if relevant, and suggest next steps. Do NOT hallucinate prices or products 
not mentioned below. Always label these as suggestions only.

=== SHOPPER PROFILE ===
{profile.summary()}

=== LOCAL TRENDS ===
{results.get("trend_insights", "N/A")}

=== PEER INSIGHTS ===
{results.get("social_insights", "N/A")}

=== UPCOMING EVENTS ===
{results.get("event_insights", "N/A")}

=== TOP RECOMMENDATIONS ===
{results.get("recommendations", "N/A")}

=== PURCHASE PLAN ===
{results.get("purchase_plan", "N/A")}

Write a warm, personalised paragraph that ties all of these together for {profile.name}:
"""
        return safe_llm_call(
            self.llm,
            prompt,
            fallback=(
                "LLM reasoning currently unavailable. "
                "Start Ollama with `ollama serve` and pull llama3 with `ollama pull llama3`. "
                "The structured tool outputs above are still fully functional."
            ),
        )
