from dataclasses import dataclass, field
from typing import Optional
from src.utils.data_loader import get_user_by_id

@dataclass
class ShopperProfile:
    """Complete shopper profile used by the recommendation agent."""
    user_id: str
    name: str
    age: int
    gender: str
    area: str
    school: str
    style_pref: str
    budget_min: float
    budget_max: float
    brand_pref: str
    size: str
    colour_pref: str = ""
    category_pref: str = ""

    def to_dict(self) -> dict:
        return self.__dict__

    def summary(self) -> str:
        return (
            f"** Shopper Profile**\n"
            f"- Name: {self.name} | Age: {self.age} | Gender: {self.gender}\n"
            f"- Area: {self.area} | School/Org: {self.school}\n"
            f"- Style: {self.style_pref} | Size: {self.size}\n"
            f"- Budget: ₹{self.budget_min} – ₹{self.budget_max}\n"
            f"- Preferred Brand: {self.brand_pref}\n"
            f"- Favourite Colour: {self.colour_pref or 'No preference'}\n"
            f"- Category Interest: {self.category_pref or 'All'}"
        )


def build_profile_from_user_id(user_id: str) -> Optional[ShopperProfile]:
    """Load an existing user profile from the dataset."""
    data = get_user_by_id(user_id)
    if data is None:
        return None
    return ShopperProfile(
        user_id=data.get("user_id", user_id),
        name=str(data.get("name", "Unknown")),
        age=int(data.get("age", 0)),
        gender=str(data.get("gender", "N/A")),
        area=str(data.get("area", "")),
        school=str(data.get("school", "")),
        style_pref=str(data.get("style_pref", "Casual")),
        budget_min=float(data.get("budget_min", 300)),
        budget_max=float(data.get("budget_max", 5000)),
        brand_pref=str(data.get("brand_pref", "")),
        size=str(data.get("size", "M")),
        colour_pref=str(data.get("colour_pref", "")),
        category_pref=str(data.get("category_pref", "")),
    )

def build_profile_from_form(form_data: dict) -> ShopperProfile:
    """Build a ShopperProfile from UI form inputs (new user flow)."""
    return ShopperProfile(
        user_id="NEW_USER",
        name=str(form_data.get("name", "Guest Shopper")),
        age=int(form_data.get("age", 20)),
        gender=str(form_data.get("gender", "N/A")),
        area=str(form_data.get("area", "")),
        school=str(form_data.get("school", "")),
        style_pref=str(form_data.get("style_pref", "Casual")),
        budget_min=float(form_data.get("budget_min", 300)),
        budget_max=float(form_data.get("budget_max", 5000)),
        brand_pref=str(form_data.get("brand_pref", "")),
        size=str(form_data.get("size", "M")),
        colour_pref=str(form_data.get("colour_pref", "")),
        category_pref=str(form_data.get("category_pref", "")),
    )
