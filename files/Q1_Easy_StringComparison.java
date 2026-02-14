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

import java.util.*;

public class Q1_Easy_StringComparison {
    
    public static boolean validatePassword(String storedPassword, String userInput) {
        // Normalize inputs by trimming whitespace
        String stored = storedPassword.trim();
        String input = userInput.trim();
        
        // Check if both passwords are not null
        if (stored != null && input != null) {
            // Compare the passwords
            if (stored == input) {  // BUG HERE: Using == instead of .equals()
                return true;
            }
        }
        
        return false;
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        System.out.println("Enter stored password:");
        String stored = sc.nextLine();
        
        System.out.println("Enter user input:");
        String input = sc.nextLine();
        
        boolean result = validatePassword(stored, input);
        System.out.println("Password match: " + result);
        
        sc.close();
    }
}
