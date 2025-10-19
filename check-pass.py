import re
def check_password_strength(password):
    score = 0
    feedback = []

    if len(password) >= 12:
        score += 2
        feedback.append(" Good length")
    elif len(password) >= 8:
        score += 1
        feedback.append(" Consider making it longer")
    else:
        feedback.append(" Too short!")

    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append(" Add uppercase letters")

    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append(" Add lowercase letters")

    if re.search(r'\d', password):
        score += 1
    else:
        feedback.append(" Add numbers")

    if re.search(r'[@$!^%|*?&]', password):
        score += 1
    else:
        feedback.append(" Add special characters (@, $, %, etc.)")

    weak_list = ["password", "123456", "qwerty", "admin", "letmein"]
    if password.lower() in weak_list:
        feedback.append(" Common password — too weak!")
        score = 0

    if score >= 6:
        strength = " Strong"
    elif 3 <= score < 6:
        strength = " Moderate"
    else:
        strength = " Weak"

    print("\nPassword Strength Report:")
    print(f"Score: {score}/6 → {strength}")
    print("\n".join(feedback))


if __name__ == "__main__":
    user_password = input("Enter a password to check: ")
    check_password_strength(user_password)
