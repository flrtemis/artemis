import random
import string

def execute(**kwargs):
    count = kwargs.get('count', 1)
    use_digits = kwargs.get('use_digits', True)
    
    emails = []
    base_chars = string.ascii_lowercase
    if use_digits:
        base_chars += string.digits
    
    for _ in range(count):
        # Generate a random username length between 8 and 15
        length = random.randint(8, 15)
        username = ''.join(random.choice(base_chars) for _ in range(length))
        emails.append(f"{username}@gmail.com")
    
    if count == 1:
        return emails[0]
    return emails
