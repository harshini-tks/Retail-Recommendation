import pandas as pd
from src.utils.data_loader import load_social_connections, load_users, load_products, load_sales_trends

def get_social_insights(user_id: str) -> dict:
    connections = load_social_connections()
    users = load_users()
    trends = load_sales_trends()
    products = load_products()

    peers_df = connections[connections["user_id"] == user_id]
    peer_ids = peers_df["peer_user_id"].tolist()

    if not peer_ids:
        return {"error": f"No social connections found for user {user_id}."}

    peer_profiles = users[users["user_id"].isin(peer_ids)]
    if peer_profiles.empty:
        return {"error": "Could not load peer profiles."}

    peer_areas = peer_profiles["area"].dropna().unique().tolist()
    peer_schools = peer_profiles["school"].dropna().unique().tolist()

    peer_trends = trends[
        (trends["area"].isin(peer_areas)) | (trends["school"].isin(peer_schools))
    ]

    if peer_trends.empty:
        return {"error": "No trend data available for your peers' areas."}

    agg = peer_trends.groupby("product_id")["units_sold"].sum().reset_index()
    agg = agg.sort_values("units_sold", ascending=False).head(5)
    merged = agg.merge(products, on="product_id", how="left")

    styles = []
    if "style_pref" in peer_profiles.columns:
        styles = peer_profiles["style_pref"].value_counts().head(2).index.tolist()

    return {
        "connections": peer_profiles['name'].tolist(),
        "trending_products": merged,
        "style_preferences": styles
    }
