import pandas as pd
import json
import os
from datetime import datetime
import streamlit as st
from config.settings import DATA_DIR

@st.cache_data(show_spinner=False)
def load_users() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "users.csv")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data(show_spinner=False)
def load_products() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "products.csv")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data(show_spinner=False)
def load_sales_trends() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "sales_trends.csv")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data(show_spinner=False)
def load_social_connections() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "social_connections.csv")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data(show_spinner=False)
def load_events() -> list:
    with open(DATA_DIR / "events_calendar.json", "r") as f:
        return json.load(f)

def get_all_areas() -> list:
    df = load_users()
    return sorted(df["area"].dropna().unique().tolist())

def get_all_schools() -> list:
    df = load_users()
    return sorted(df["school"].dropna().unique().tolist())

def get_user_by_id(user_id: str) -> dict | None:
    df = load_users()
    row = df[df["user_id"] == user_id]
    if row.empty:
        return None
    return row.iloc[0].to_dict()

def get_upcoming_events(days_ahead: int = 60) -> list:
    events = load_events()
    today = datetime.today()
    upcoming = []
    for e in events:
        try:
            event_date = datetime.strptime(e["date"], "%Y-%m-%d")
            delta = (event_date - today).days
            if 0 <= delta <= days_ahead:
                e["days_until"] = delta
                upcoming.append(e)
        except Exception:
            pass
    return sorted(upcoming, key=lambda x: x["days_until"])
