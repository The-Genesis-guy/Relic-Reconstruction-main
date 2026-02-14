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

#include <iostream>
#include <iomanip>
#include <string>
#include <sstream>
using namespace std;

class IDGenerator {
private:
    static int counter;  // BUG HERE: Shared static counter across all instances
    string prefix;
    
public:
    IDGenerator(string p) : prefix(p) {}
    
    string generateID() {
        counter++;  // BUG: All instances share the same counter
        ostringstream oss;
        oss << prefix << setfill('0') << setw(4) << counter;
        return oss.str();
    }
    
    void resetCounter() {
        counter = 0;  // BUG: Resets counter for ALL instances
    }
    
    int getCurrentCount() {
        return counter;
    }
};

// Initialize static member
int IDGenerator::counter = 0;

int main() {
    // Create separate generators for each entity type
    IDGenerator userGen("U");
    IDGenerator productGen("P");
    IDGenerator orderGen("O");
    
    cout << "=== ID Generation System ===" << endl << endl;
    
    // Generate User IDs
    int userCount1;
    cout << "Enter number of User IDs to generate:" << endl;
    cin >> userCount1;
    cout << "\nGenerating " << userCount1 << " User IDs:" << endl;
    for (int i = 0; i < userCount1; i++) {
        cout << userGen.generateID() << endl;
    }
    
    // Generate Product IDs
    int productCount;
    cout << "\nEnter number of Product IDs to generate:" << endl;
    cin >> productCount;
    cout << "\nGenerating " << productCount << " Product IDs:" << endl;
    for (int i = 0; i < productCount; i++) {
        cout << productGen.generateID() << endl;
    }
    
    // Generate more User IDs
    int userCount2;
    cout << "\nEnter number of additional User IDs to generate:" << endl;
    cin >> userCount2;
    cout << "\nGenerating " << userCount2 << " more User IDs:" << endl;
    for (int i = 0; i < userCount2; i++) {
        cout << userGen.generateID() << endl;
    }
    
    // Generate Order IDs
    int orderCount;
    cout << "\nEnter number of Order IDs to generate:" << endl;
    cin >> orderCount;
    cout << "\nGenerating " << orderCount << " Order IDs:" << endl;
    for (int i = 0; i < orderCount; i++) {
        cout << orderGen.generateID() << endl;
    }
    
    // Show current counts
    cout << "\n=== Current Counters ===" << endl;
    cout << "User counter: " << userGen.getCurrentCount() << endl;
    cout << "Product counter: " << productGen.getCurrentCount() << endl;
    cout << "Order counter: " << orderGen.getCurrentCount() << endl;
    
    cout << "\nBUG: All generators share the same counter!" << endl;
    cout << "Expected: Each should have independent counters" << endl;
    cout << "  User: " << userCount1 << " + " << userCount2 << " = " << (userCount1 + userCount2) << endl;
    cout << "  Product: " << productCount << endl;
    cout << "  Order: " << orderCount << endl;
    
    return 0;
}
