"""
PROBLEM: ID Generator for Multiple Systems

Create unique IDs for different systems (Users, Products, Orders).
Each system should have its own independent ID counter starting from 1.

Requirements:
- User IDs: U0001, U0002, U0003, ...
- Product IDs: P0001, P0002, P0003, ...
- Order IDs: O0001, O0002, O0003, ...

INPUT: Type of entity (User/Product/Order) and count
OUTPUT: Generated IDs for each entity type

EXPECTED BEHAVIOR:
Generate 3 Users: U0001, U0002, U0003
Generate 2 Products: P0001, P0002
Generate 3 more Users: U0004, U0005, U0006
Generate 2 Orders: O0001, O0002

Each type maintains its own counter independently.

BUG: The code produces incorrect IDs. Find and fix the bug!
"""

class IDGenerator:
    counter = 0  # BUG HERE: Class variable shared across all instances
    
    def __init__(self, prefix):
        self.prefix = prefix
    
    def generateID(self):
        IDGenerator.counter += 1  # BUG: All instances share the same counter
        return f"{self.prefix}{IDGenerator.counter:04d}"
    
    def resetCounter(self):
        IDGenerator.counter = 0  # BUG: Resets counter for ALL instances
    
    def getCurrentCount(self):
        return IDGenerator.counter

def main():
    # Create separate generators for each entity type
    userGen = IDGenerator("U")
    productGen = IDGenerator("P")
    orderGen = IDGenerator("O")
    
    print("=== ID Generation System ===\n")
    
    # Generate User IDs
    userCount1 = int(input("Enter number of User IDs to generate:\n"))
    print(f"\nGenerating {userCount1} User IDs:")
    for i in range(userCount1):
        print(userGen.generateID())
    
    # Generate Product IDs
    productCount = int(input("\nEnter number of Product IDs to generate:\n"))
    print(f"\nGenerating {productCount} Product IDs:")
    for i in range(productCount):
        print(productGen.generateID())
    
    # Generate more User IDs
    userCount2 = int(input("\nEnter number of additional User IDs to generate:\n"))
    print(f"\nGenerating {userCount2} more User IDs:")
    for i in range(userCount2):
        print(userGen.generateID())
    
    # Generate Order IDs
    orderCount = int(input("\nEnter number of Order IDs to generate:\n"))
    print(f"\nGenerating {orderCount} Order IDs:")
    for i in range(orderCount):
        print(orderGen.generateID())
    
    # Show current counts
    print("\n=== Current Counters ===")
    print(f"User counter: {userGen.getCurrentCount()}")
    print(f"Product counter: {productGen.getCurrentCount()}")
    print(f"Order counter: {orderGen.getCurrentCount()}")
    
    print("\nBUG: All generators share the same counter!")
    print("Expected: Each should have independent counters")
    print(f"  User: {userCount1} + {userCount2} = {userCount1 + userCount2}")
    print(f"  Product: {productCount}")
    print(f"  Order: {orderCount}")

if __name__ == "__main__":
    main()
