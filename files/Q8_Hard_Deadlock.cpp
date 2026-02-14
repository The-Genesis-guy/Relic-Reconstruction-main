/**
 * PROBLEM: Bank Transfer System (Multi-threaded)
 * 
 * Implement a thread-safe bank transfer system that can handle concurrent transfers.
 * Two accounts are performing simultaneous transfers to each other.
 * 
 * Scenario:
 * - Account A transfers $100 to Account B
 * - Account B transfers $50 to Account A
 * - Both happen simultaneously in different threads
 * 
 * INPUT: Initial balances for both accounts
 * OUTPUT: Final balances after transfers complete
 * 
 * EXPECTED BEHAVIOR:
 * Initial: A=$1000, B=$500
 * Transfer 1: A->B $100
 * Transfer 2: B->A $50
 * Final: A=$950, B=$550
 * Both transfers should complete successfully
 * 
 * BUG: The program sometimes hangs and never completes. Find and fix the bug!
 */

#include <iostream>
#include <thread>
#include <mutex>
#include <chrono>
#include <string>
using namespace std;

class BankAccount {
private:
    string name;
    double balance;
    mutex accountLock;
    
public:
    BankAccount(string n, double b) : name(n), balance(b) {}
    
    string getName() { return name; }
    double getBalance() { return balance; }
    
    void transferTo(BankAccount& target, double amount) {
        // BUG HERE: Potential deadlock due to inconsistent lock ordering
        // Thread 1 locks A then B
        // Thread 2 locks B then A
        // This can cause circular wait condition
        
        lock_guard<mutex> lock1(this->accountLock);
        cout << this_thread::get_id() << ": Locked " << this->name << endl;
        
        // Simulate some processing time
        this_thread::sleep_for(chrono::milliseconds(100));
        
        lock_guard<mutex> lock2(target.accountLock);
        cout << this_thread::get_id() << ": Locked " << target.getName() << endl;
        
        if (this->balance >= amount) {
            this->balance -= amount;
            target.balance += amount;
            cout << "Transfer complete: " << this->name << " -> " 
                 << target.getName() << " $" << amount << endl;
        } else {
            cout << "Insufficient funds in " << this->name << endl;
        }
    }
};

int main() {
    double balanceA, balanceB;
    
    cout << "Enter initial balance for Account A:" << endl;
    cin >> balanceA;
    
    cout << "Enter initial balance for Account B:" << endl;
    cin >> balanceB;
    
    BankAccount accountA("Account-A", balanceA);
    BankAccount accountB("Account-B", balanceB);
    
    cout << "\nInitial balances:" << endl;
    cout << accountA.getName() << ": $" << accountA.getBalance() << endl;
    cout << accountB.getName() << ": $" << accountB.getBalance() << endl;
    
    // Create two threads for simultaneous transfers
    thread t1([&]() {
        accountA.transferTo(accountB, 100);
    });
    
    thread t2([&]() {
        accountB.transferTo(accountA, 50);
    });
    
    // Try to join with timeout (C++ doesn't have direct timeout join)
    auto start = chrono::steady_clock::now();
    bool t1_done = false, t2_done = false;
    
    while (chrono::duration_cast<chrono::seconds>(
           chrono::steady_clock::now() - start).count() < 5) {
        if (t1.joinable()) {
            // Check if we can join (this is a simplified check)
            this_thread::sleep_for(chrono::milliseconds(100));
        }
    }
    
    if (t1.joinable() || t2.joinable()) {
        cout << "\nWARNING: Potential deadlock detected!" << endl;
        cout << "Threads may not have completed in time." << endl;
        // Force join anyway
        if (t1.joinable()) t1.join();
        if (t2.joinable()) t2.join();
    }
    
    cout << "\nFinal balances:" << endl;
    cout << accountA.getName() << ": $" << accountA.getBalance() << endl;
    cout << accountB.getName() << ": $" << accountB.getBalance() << endl;
    
    return 0;
}
