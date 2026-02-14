"""
PROBLEM: Bank Transfer System (Multi-threaded)

Implement a thread-safe bank transfer system that can handle concurrent transfers.
Two accounts are performing simultaneous transfers to each other.

Scenario:
- Account A transfers $100 to Account B
- Account B transfers $50 to Account A
- Both happen simultaneously in different threads

INPUT: Initial balances for both accounts
OUTPUT: Final balances after transfers complete

EXPECTED BEHAVIOR:
Initial: A=$1000, B=$500
Transfer 1: A->B $100
Transfer 2: B->A $50
Final: A=$950, B=$550
Both transfers should complete successfully

BUG: The program sometimes hangs and never completes. Find and fix the bug!
"""

import threading
import time

class BankAccount:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.lock = threading.Lock()
    
    def transferTo(self, target, amount):
        # BUG HERE: Potential deadlock due to inconsistent lock ordering
        # Thread 1 locks A then B
        # Thread 2 locks B then A
        # This can cause circular wait condition
        
        with self.lock:
            print(f"{threading.current_thread().name}: Locked {self.name}")
            
            # Simulate some processing time
            time.sleep(0.1)
            
            with target.lock:
                print(f"{threading.current_thread().name}: Locked {target.name}")
                
                if self.balance >= amount:
                    self.balance -= amount
                    target.balance += amount
                    print(f"Transfer complete: {self.name} -> {target.name} ${amount}")
                else:
                    print(f"Insufficient funds in {self.name}")

def main():
    balanceA = float(input("Enter initial balance for Account A:\n"))
    balanceB = float(input("Enter initial balance for Account B:\n"))
    
    accountA = BankAccount("Account-A", balanceA)
    accountB = BankAccount("Account-B", balanceB)
    
    print("\nInitial balances:")
    print(f"{accountA.name}: ${accountA.balance}")
    print(f"{accountB.name}: ${accountB.balance}")
    
    # Create two threads for simultaneous transfers
    t1 = threading.Thread(
        target=lambda: accountA.transferTo(accountB, 100),
        name="Thread-1"
    )
    
    t2 = threading.Thread(
        target=lambda: accountB.transferTo(accountA, 50),
        name="Thread-2"
    )
    
    # Start both threads
    t1.start()
    t2.start()
    
    # Wait for threads with timeout
    t1.join(timeout=5)
    t2.join(timeout=5)
    
    if t1.is_alive() or t2.is_alive():
        print("\nWARNING: Deadlock detected! Threads did not complete.")
        print(f"Thread-1 alive: {t1.is_alive()}")
        print(f"Thread-2 alive: {t2.is_alive()}")
    else:
        print("\nFinal balances:")
        print(f"{accountA.name}: ${accountA.balance}")
        print(f"{accountB.name}: ${accountB.balance}")

if __name__ == "__main__":
    main()
