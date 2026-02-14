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

#include <stdio.h>
#include <string.h>

typedef struct {
    char prefix;
} IDGenerator;

void initGenerator(IDGenerator* gen, char prefix) {
    gen->prefix = prefix;
}

char* generateID(IDGenerator* gen, char* buffer) {
    static int counter = 0;  // BUG HERE: Shared static counter across all function calls
    counter++;  // BUG: All generators share the same counter
    sprintf(buffer, "%c%04d", gen->prefix, counter);
    return buffer;
}

int getCurrentCount() {
    static int counter = 0;  // Access to same static variable
    return counter;
}

int main() {
    IDGenerator userGen, productGen, orderGen;
    char id[10];
    
    initGenerator(&userGen, 'U');
    initGenerator(&productGen, 'P');
    initGenerator(&orderGen, 'O');
    
    printf("=== ID Generation System ===\n\n");
    
    // Generate User IDs
    int userCount1;
    printf("Enter number of User IDs to generate:\n");
    scanf("%d", &userCount1);
    printf("\nGenerating %d User IDs:\n", userCount1);
    for (int i = 0; i < userCount1; i++) {
        printf("%s\n", generateID(&userGen, id));
    }
    
    // Generate Product IDs
    int productCount;
    printf("\nEnter number of Product IDs to generate:\n");
    scanf("%d", &productCount);
    printf("\nGenerating %d Product IDs:\n", productCount);
    for (int i = 0; i < productCount; i++) {
        printf("%s\n", generateID(&productGen, id));
    }
    
    // Generate more User IDs
    int userCount2;
    printf("\nEnter number of additional User IDs to generate:\n");
    scanf("%d", &userCount2);
    printf("\nGenerating %d more User IDs:\n", userCount2);
    for (int i = 0; i < userCount2; i++) {
        printf("%s\n", generateID(&userGen, id));
    }
    
    // Generate Order IDs
    int orderCount;
    printf("\nEnter number of Order IDs to generate:\n");
    scanf("%d", &orderCount);
    printf("\nGenerating %d Order IDs:\n", orderCount);
    for (int i = 0; i < orderCount; i++) {
        printf("%s\n", generateID(&orderGen, id));
    }
    
    // Show issue
    printf("\n=== Current Counter ===\n");
    printf("Shared counter value: %d\n", getCurrentCount());
    
    printf("\nBUG: All generators share the same static counter!\n");
    printf("Expected: Each should have independent counters\n");
    printf("  User: %d + %d = %d\n", userCount1, userCount2, userCount1 + userCount2);
    printf("  Product: %d\n", productCount);
    printf("  Order: %d\n", orderCount);
    
    return 0;
}
