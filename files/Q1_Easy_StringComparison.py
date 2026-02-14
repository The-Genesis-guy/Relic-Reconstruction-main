"""
PROBLEM: Password Validator

This program validates if a user's password matches the stored password.
It should return True if passwords match, False otherwise.

INPUT: Two strings - storedPassword and userInput
OUTPUT: Boolean - True if match, False otherwise

EXPECTED BEHAVIOR:
validatePassword("secret123", "secret123") -> True
validatePassword("admin", "user") -> False
validatePassword("pass", "pass") -> True

BUG: The code has a subtle bug that causes it to fail in certain cases.
Find and fix the bug!
"""

def validatePassword(storedPassword, userInput):
    # Normalize inputs by trimming whitespace
    stored = storedPassword.strip()
    input_str = userInput.strip()
    
    # Check if both passwords are not None
    if stored is not None and input_str is not None:
        # Compare the passwords
        if stored is input_str:  # BUG HERE: Using 'is' instead of '=='
            return True
    
    return False

def main():
    stored = input("Enter stored password:\n")
    user_input = input("Enter user input:\n")
    
    result = validatePassword(stored, user_input)
    print(f"Password match: {result}")

if __name__ == "__main__":
    main()
