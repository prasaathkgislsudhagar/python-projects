import random
import string

def generate_password(length=12):
    if length < 6:
        print("Password too short! Minimum 6 characters.")
        return ""
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "@$!^%|*?&"


    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special)
    ]



    all_chars = lowercase + uppercase + digits + special
    password += random.choices(all_chars, k=length - 4)
    random.shuffle(password)



    return "".join(password)


if __name__ == "__main__":
    try:
        length = int(input("Enter desired password length: "))
        new_password = generate_password(length)
        if new_password:
            print(f"Generated Password: {new_password}")
    except ValueError:
        print("Please enter a valid number.")
