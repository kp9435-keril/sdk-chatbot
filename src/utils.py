def get_suggestions_from_csv(response: str):
    """
    Parse the CSV response and return a list of suggestions.
    """
    suggestions = []
    lines = response.split(",")
    for line in lines:
        suggestion = line.strip()
        if suggestion:
            suggestions.append(suggestion)
    return suggestions