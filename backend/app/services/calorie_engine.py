"""
Calorie calculation engine using the Mifflin-St Jeor formula.

BMR (Basal Metabolic Rate) — calories burned at complete rest.
TDEE (Total Daily Energy Expenditure) — BMR × activity multiplier.
Target calories — adjusted for weight goal (lose/maintain/gain).
"""

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,    # desk job, no exercise
    "light": 1.375,      # 1-3 days/week
    "moderate": 1.55,    # 3-5 days/week
    "active": 1.725,     # 6-7 days/week
    "athlete": 1.9,      # twice/day training
}

# Calorie adjustment for goal
GOAL_ADJUSTMENTS = {
    "lose": -500,       # 500 kcal deficit → ~0.5 kg/week loss
    "maintain": 0,
    "gain": +300,       # 300 kcal surplus → lean bulk
}


def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    Mifflin-St Jeor formula.
    weight: kg | height: cm | age: years
    """
    base = 10 * weight + 6.25 * height - 5 * age
    return base + 5 if gender == "male" else base - 161


def calculate_maintenance(bmr: float, activity_level: str) -> float:
    """TDEE = BMR × activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier, 2)


def calculate_target(maintenance: float, goal: str) -> float:
    """Apply goal-based calorie adjustment."""
    adjustment = GOAL_ADJUSTMENTS.get(goal, 0)
    return round(maintenance + adjustment, 2)


def run_calorie_engine(weight: float, height: float, age: int,
                       gender: str, activity_level: str, goal: str) -> dict:
    """
    Full pipeline: returns bmr, maintenance, and target calories.
    Called when user saves/updates their profile.
    """
    bmr = calculate_bmr(weight, height, age, gender)
    maintenance = calculate_maintenance(bmr, activity_level)
    target = calculate_target(maintenance, goal)
    return {
        "bmr": round(bmr, 2),
        "maintenance_calories": maintenance,
        "target_calories": target,
    }
