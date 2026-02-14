/**
 * PROBLEM: Password Validator
 * 
 * This program validates if a user's password matches the stored password.
 * It should return 1 if passwords match, 0 otherwise.
 * 
 * INPUT: Two strings - storedPassword and userInput
 * OUTPUT: Integer - 1 if match, 0 otherwise
 * 
 * EXPECTED BEHAVIOR:
 * validatePassword("secret123", "secret123") -> 1
 * validatePassword("admin", "user") -> 0
 * validatePassword("pass", "pass") -> 1
 * 
 * BUG: The code has a subtle bug that causes it to fail in certain cases.
 * Find and fix the bug!
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int validatePassword(char* storedPassword, char* userInput) {
    // Check if both passwords are not null
    if (storedPassword != NULL && userInput != NULL) {
        // Compare the passwords
        if (storedPassword == userInput) {  // BUG HERE: Comparing pointers instead of strings
            return 1;
        }
    }
    
    return 0;
}

int main() {
    char stored[100];
    char input[100];
    
    printf("Enter stored password:\n");
    fgets(stored, 100, stdin);
    stored[strcspn(stored, "\n")] = 0;  // Remove newline
    
    printf("Enter user input:\n");
    fgets(input, 100, stdin);
    input[strcspn(input, "\n")] = 0;  // Remove newline
    
    int result = validatePassword(stored, input);
    printf("Password match: %d\n", result);
    
    return 0;
}
