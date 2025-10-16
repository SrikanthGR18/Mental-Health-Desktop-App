def get_tip(stress_level, cause="general"):
    tips = {
        "low": "You're doing great! Keep maintaining your healthy routine and positive mindset. Consistency is key.",
        "medium": "A good time to pause. Consider a short walk, some deep breathing exercises, or listening to calm music.",
        "high": "It's important to take this seriously. Please consider talking to your counselor, a trusted friend, or family member."
    }
    return tips.get(stress_level, "Stay mindful of your well-being.")