"""
Tests for the calorie calculation engine.
Run: pytest (from backend/ with venv active)
"""
import pytest
from app.services.calorie_engine import calculate_bmr, calculate_maintenance, run_calorie_engine


def test_bmr_male():
    # 70kg, 175cm, 25yo male: 10*70 + 6.25*175 - 5*25 + 5 = 1673.75
    assert calculate_bmr(70, 175, 25, "male") == pytest.approx(1673.75)


def test_bmr_female():
    # 60kg, 165cm, 30yo female: 10*60 + 6.25*165 - 5*30 - 161 = 1320.25
    assert calculate_bmr(60, 165, 30, "female") == pytest.approx(1320.25)


def test_maintenance_sedentary():
    assert calculate_maintenance(1743.75, "sedentary") == pytest.approx(1743.75 * 1.2, rel=1e-3)


def test_maintenance_athlete():
    assert calculate_maintenance(1743.75, "athlete") == pytest.approx(1743.75 * 1.9, rel=1e-3)


def test_full_engine_lose_goal():
    result = run_calorie_engine(70, 175, 25, "male", "moderate", "lose")
    assert "bmr" in result
    assert "maintenance_calories" in result
    assert "target_calories" in result
    assert result["target_calories"] == pytest.approx(result["maintenance_calories"] - 500)


def test_full_engine_gain_goal():
    result = run_calorie_engine(70, 175, 25, "male", "moderate", "gain")
    assert result["target_calories"] == pytest.approx(result["maintenance_calories"] + 300)


def test_full_engine_maintain_goal():
    result = run_calorie_engine(70, 175, 25, "male", "moderate", "maintain")
    assert result["target_calories"] == pytest.approx(result["maintenance_calories"])
