import random
import string

def execute(**kwargs):
    length = kwargs.get('length', 12)
    include_digits = kwargs.get('include_digits', True)
    include_special = kwargs.get('include_special', True)

    chars = string.ascii_letters
    if include_digits:
        chars += string.digits
    if include_special:
        chars += string.punctuation

    if not chars:
        return "Error: No characters selected for the password."

    password = ''.join(random.choice(chars) for _ in range(length))
    return password
