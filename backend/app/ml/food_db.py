"""
Legacy food DB module — delegates to FoodService (dataset + rapidfuzz).
"""
from app.services.food_service import food_service


def search_foods(query: str, limit: int = 10) -> list[dict]:
    if not food_service.loaded:
        food_service.initialize()
    return food_service.search(query, limit)


def get_food_by_name(name: str) -> dict | None:
    if not food_service.loaded:
        food_service.initialize()
    return food_service.get_by_name(name)
