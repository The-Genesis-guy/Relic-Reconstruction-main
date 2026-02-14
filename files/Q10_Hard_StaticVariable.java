/**
 * PROBLEM: ID Generator for Multiple Systems
 * 
 * Create unique IDs for different systems (Users, Products, Orders).
 * Each system should have its own independent ID counter starting from 1.
 * 
 * Requirements:
 * - User IDs: U0001, U0002, U0003, ...
 * - Product IDs: P0001, P0002, P0003, ...
 * - Order IDs: O0001, O0002, O0003, ...
 * 
 * INPUT: Type of entity (User/Product/Order) and count
 * OUTPUT: Generated IDs for each entity type
 * 
 * EXPECTED BEHAVIOR:
 * Generate 3 Users: U0001, U0002, U0003
 * Generate 2 Products: P0001, P0002
 * Generate 3 more Users: U0004, U0005, U0006
 * Generate 2 Orders: O0001, O0002
 * 
 * Each type maintains its own counter independently.
 * 
 * BUG: The code produces incorrect IDs. Find and fix the bug!
 */

import java.util.*;

class IDGenerator {
    private static int counter = 0;  // BUG HERE: Shared static counter across all instances
    private String prefix;
    
    public IDGenerator(String prefix) {
        this.prefix = prefix;
    }
    
    public String generateID() {
        counter++;  // BUG: All instances share the same counter
        return String.format("%s%04d", prefix, counter);
    }
    
    public void resetCounter() {
        counter = 0;  // BUG: Resets counter for ALL instances, not just this one
    }
    
    public int getCurrentCount() {
        return counter;
    }
}

public class Q10_Hard_StaticVariable {
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        // Create separate generators for each entity type
        IDGenerator userGen = new IDGenerator("U");
        IDGenerator productGen = new IDGenerator("P");
        IDGenerator orderGen = new IDGenerator("O");
        
        System.out.println("=== ID Generation System ===\n");
        
        // Generate User IDs
        System.out.println("Enter number of User IDs to generate:");
        int userCount1 = sc.nextInt();
        System.out.println("\nGenerating " + userCount1 + " User IDs:");
        for (int i = 0; i < userCount1; i++) {
            System.out.println(userGen.generateID());
        }
        
        // Generate Product IDs
        System.out.println("\nEnter number of Product IDs to generate:");
        int productCount = sc.nextInt();
        System.out.println("\nGenerating " + productCount + " Product IDs:");
        for (int i = 0; i < productCount; i++) {
            System.out.println(productGen.generateID());
        }
        
        // Generate more User IDs (should continue from where it left off)
        System.out.println("\nEnter number of additional User IDs to generate:");
        int userCount2 = sc.nextInt();
        System.out.println("\nGenerating " + userCount2 + " more User IDs:");
        for (int i = 0; i < userCount2; i++) {
            System.out.println(userGen.generateID());
        }
        
        // Generate Order IDs
        System.out.println("\nEnter number of Order IDs to generate:");
        int orderCount = sc.nextInt();
        System.out.println("\nGenerating " + orderCount + " Order IDs:");
        for (int i = 0; i < orderCount; i++) {
            System.out.println(orderGen.generateID());
        }
        
        // Show current counts
        System.out.println("\n=== Current Counters ===");
        System.out.println("User counter: " + userGen.getCurrentCount());
        System.out.println("Product counter: " + productGen.getCurrentCount());
        System.out.println("Order counter: " + orderGen.getCurrentCount());
        
        System.out.println("\nBUG: All generators share the same counter!");
        System.out.println("Expected: Each should have independent counters");
        System.out.println("  User: " + userCount1 + " + " + userCount2 + " = " + (userCount1 + userCount2));
        System.out.println("  Product: " + productCount);
        System.out.println("  Order: " + orderCount);
        
        sc.close();
    }
}
