/**
 * PROBLEM: Password Validator
 * 
 * This program validates if a user's password matches the stored password.
 * It should return true if passwords match, false otherwise.
 * 
 * INPUT: Two strings - storedPassword and userInput
 * OUTPUT: Boolean - true if match, false otherwise
 * 
 * EXPECTED BEHAVIOR:
 * validatePassword("secret123", "secret123") -> true
 * validatePassword("admin", "user") -> false
 * validatePassword("pass", "pass") -> true
 * 
 * BUG: The code has a subtle bug that causes it to fail in certain cases.
 * Find and fix the bug!
 */

#include <iostream>
#include <string>
using namespace std;

bool validatePassword(const char* storedPassword, const char* userInput) {
    // Check if both passwords are not null
    if (storedPassword != nullptr && userInput != nullptr) {
        // Compare the passwords
        if (storedPassword == userInput) {  // BUG HERE: Comparing pointers instead of using strcmp
            return true;
        }
    }
    
    return false;
}

int main() {
    string stored, input;
    
    cout << "Enter stored password:" << endl;
    getline(cin, stored);
    
    cout << "Enter user input:" << endl;
    getline(cin, input);
    
    bool result = validatePassword(stored.c_str(), input.c_str());
    cout << "Password match: " << (result ? "true" : "false") << endl;
    
    return 0;
}
