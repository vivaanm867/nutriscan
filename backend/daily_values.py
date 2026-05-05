CALORIE_REFERENCE = 2000

DAILY_VALUES = {
    "totalFat": 78,              # grams
    "saturatedFat": 20,          # grams
    "cholesterol": 300,          # milligrams
    "sodium": 2300,              # milligrams
    "totalCarbohydrate": 275,    # grams
    "dietaryFiber": 28,          # grams
    "addedSugars": 50,           # grams
    "protein": 50,               # grams
    "vitaminD": 20,              # micrograms
    "calcium": 1300,             # milligrams
    "iron": 18,                  # milligrams
    "potassium": 4700,           # milligrams
}

NO_DAILY_VALUE = {
    "transFat",
    "totalSugars",
}


def calculate_daily_value(nutrient_key: str, amount):
    if amount is None:
        return None

    if nutrient_key in NO_DAILY_VALUE:
        return None

    if nutrient_key == "calories":
        return round((amount / CALORIE_REFERENCE) * 100)

    reference_amount = DAILY_VALUES.get(nutrient_key)

    if reference_amount is None:
        return None

    return round((amount / reference_amount) * 100)


def get_daily_reference(nutrient_key: str):
    """Get the daily reference value for a nutrient key."""
    if nutrient_key == "calories":
        return CALORIE_REFERENCE
    
    return DAILY_VALUES.get(nutrient_key)