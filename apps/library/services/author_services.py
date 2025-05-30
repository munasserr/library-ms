from datetime import date

def calculate_age(birth, death=None):
    if not birth:
        return None
    end = death or date.today()
    age = end.year - birth.year - ((end.month, end.day) < (birth.month, birth.day))
    return age