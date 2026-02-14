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

import java.util.*;

class BankAccount {
    private String name;
    private double balance;
    
    public BankAccount(String name, double balance) {
        this.name = name;
        this.balance = balance;
    }
    
    public String getName() {
        return name;
    }
    
    public double getBalance() {
        return balance;
    }
    
    // Transfer money from this account to another
    public void transferTo(BankAccount target, double amount) throws InterruptedException {
        // BUG HERE: Potential deadlock due to inconsistent lock ordering
        // Thread 1 locks A then B
        // Thread 2 locks B then A
        // This can cause circular wait condition
        
        synchronized(this) {
            System.out.println(Thread.currentThread().getName() + ": Locked " + this.name);
            
            // Simulate some processing time
            Thread.sleep(100);
            
            synchronized(target) {
                System.out.println(Thread.currentThread().getName() + ": Locked " + target.getName());
                
                if (this.balance >= amount) {
                    this.balance -= amount;
                    target.balance += amount;
                    System.out.println("Transfer complete: " + this.name + " -> " + 
                                     target.getName() + " $" + amount);
                } else {
                    System.out.println("Insufficient funds in " + this.name);
                }
            }
        }
    }
}

public class Q8_Hard_Deadlock {
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        System.out.println("Enter initial balance for Account A:");
        double balanceA = sc.nextDouble();
        
        System.out.println("Enter initial balance for Account B:");
        double balanceB = sc.nextDouble();
        
        BankAccount accountA = new BankAccount("Account-A", balanceA);
        BankAccount accountB = new BankAccount("Account-B", balanceB);
        
        System.out.println("\nInitial balances:");
        System.out.println(accountA.getName() + ": $" + accountA.getBalance());
        System.out.println(accountB.getName() + ": $" + accountB.getBalance());
        
        // Create two threads for simultaneous transfers
        Thread t1 = new Thread(() -> {
            try {
                accountA.transferTo(accountB, 100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "Thread-1");
        
        Thread t2 = new Thread(() -> {
            try {
                accountB.transferTo(accountA, 50);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "Thread-2");
        
        // Start both threads
        t1.start();
        t2.start();
        
        try {
            // Wait for both threads to complete (may deadlock!)
            t1.join(5000);  // 5 second timeout
            t2.join(5000);
            
            if (t1.isAlive() || t2.isAlive()) {
                System.out.println("\nWARNING: Deadlock detected! Threads did not complete.");
                System.out.println("Thread-1 alive: " + t1.isAlive());
                System.out.println("Thread-2 alive: " + t2.isAlive());
            } else {
                System.out.println("\nFinal balances:");
                System.out.println(accountA.getName() + ": $" + accountA.getBalance());
                System.out.println(accountB.getName() + ": $" + accountB.getBalance());
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        sc.close();
    }
}
