import requests
import json

# Get the token from login
login_data = {
    'email': 'temporalmailid2334@gmail.com',
    'password': 'TestPassword123!'
}

login_response = requests.post('http://localhost:8000/api/auth/login', json=login_data)
token = login_response.json()['access_token']

# Add meal data
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

meals = [
    {
        'food_name': 'Chicken Biryani',
        'quantity': 250,
        'unit': 'g',
        'calories': 450,
        'protein': 25,
        'carbs': 45,
        'fats': 15,
        'meal_type': 'lunch'
    },
    {
        'food_name': 'Paneer Butter Masala',
        'quantity': 200,
        'unit': 'g',
        'calories': 380,
        'protein': 18,
        'carbs': 20,
        'fats': 22,
        'meal_type': 'dinner'
    },
    {
        'food_name': 'Idli with Sambar',
        'quantity': 150,
        'unit': 'g',
        'calories': 200,
        'protein': 8,
        'carbs': 35,
        'fats': 3,
        'meal_type': 'breakfast'
    },
    {
        'food_name': 'Dosa with Chutney',
        'quantity': 180,
        'unit': 'g',
        'calories': 320,
        'protein': 12,
        'carbs': 40,
        'fats': 12,
        'meal_type': 'breakfast'
    },
    {
        'food_name': 'Samosa',
        'quantity': 100,
        'unit': 'g',
        'calories': 280,
        'protein': 6,
        'carbs': 30,
        'fats': 14,
        'meal_type': 'snacks'
    }
]

print('Adding meal data to database...')
for meal in meals:
    response = requests.post('http://localhost:8000/api/meals/', json=meal, headers=headers)
    if response.status_code == 201:
        meal_data = response.json()
        print(f"Added: {meal_data['food_name']} ({meal_data['calories']} cal)")
    else:
        print(f"Failed to add {meal['food_name']}: {response.status_code}")
        print(f"Error: {response.json()}")

# Retrieve meals
print("\n\nRetrieving meals from database...")
response = requests.get('http://localhost:8000/api/meals/', headers=headers)
if response.status_code == 200:
    meals_data = response.json()
    print(f"\nTotal meals stored: {len(meals_data)}")
    print("\nMeal Details:")
    print("-" * 80)
    for meal in meals_data:
        print(f"ID: {meal['id']}")
        print(f"  Food: {meal['food_name']}")
        print(f"  Quantity: {meal['quantity']} {meal['unit']}")
        print(f"  Calories: {meal['calories']} kcal")
        print(f"  Protein: {meal['protein']}g | Carbs: {meal['carbs']}g | Fats: {meal['fats']}g")
        print(f"  Type: {meal['meal_type']}")
        print(f"  Created: {meal['created_at']}")
        print()
else:
    print(f"Failed to retrieve meals: {response.status_code}")
    print(f"Error: {response.json()}")
