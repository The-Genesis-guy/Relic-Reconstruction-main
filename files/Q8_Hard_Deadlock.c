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

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <string.h>

typedef struct {
    char name[20];
    double balance;
    pthread_mutex_t lock;
} BankAccount;

typedef struct {
    BankAccount* from;
    BankAccount* to;
    double amount;
} TransferData;

void initAccount(BankAccount* acc, const char* name, double balance) {
    strcpy(acc->name, name);
    acc->balance = balance;
    pthread_mutex_init(&acc->lock, NULL);
}

void transferMoney(BankAccount* from, BankAccount* to, double amount) {
    // BUG HERE: Potential deadlock due to inconsistent lock ordering
    // Thread 1 locks A then B
    // Thread 2 locks B then A
    // This can cause circular wait condition
    
    pthread_mutex_lock(&from->lock);
    printf("Thread %lu: Locked %s\n", pthread_self(), from->name);
    
    // Simulate some processing time
    usleep(100000);  // 100ms
    
    pthread_mutex_lock(&to->lock);
    printf("Thread %lu: Locked %s\n", pthread_self(), to->name);
    
    if (from->balance >= amount) {
        from->balance -= amount;
        to->balance += amount;
        printf("Transfer complete: %s -> %s $%.2f\n", from->name, to->name, amount);
    } else {
        printf("Insufficient funds in %s\n", from->name);
    }
    
    pthread_mutex_unlock(&to->lock);
    pthread_mutex_unlock(&from->lock);
}

void* transferThread(void* arg) {
    TransferData* data = (TransferData*)arg;
    transferMoney(data->from, data->to, data->amount);
    return NULL;
}

int main() {
    double balanceA, balanceB;
    
    printf("Enter initial balance for Account A:\n");
    scanf("%lf", &balanceA);
    
    printf("Enter initial balance for Account B:\n");
    scanf("%lf", &balanceB);
    
    BankAccount accountA, accountB;
    initAccount(&accountA, "Account-A", balanceA);
    initAccount(&accountB, "Account-B", balanceB);
    
    printf("\nInitial balances:\n");
    printf("%s: $%.2f\n", accountA.name, accountA.balance);
    printf("%s: $%.2f\n", accountB.name, accountB.balance);
    
    TransferData transfer1 = {&accountA, &accountB, 100};
    TransferData transfer2 = {&accountB, &accountA, 50};
    
    pthread_t t1, t2;
    
    // Create threads
    pthread_create(&t1, NULL, transferThread, &transfer1);
    pthread_create(&t2, NULL, transferThread, &transfer2);
    
    // Wait for threads (may deadlock!)
    struct timespec timeout;
    timeout.tv_sec = 5;
    timeout.tv_nsec = 0;
    
    int r1 = pthread_timedjoin_np(t1, NULL, &timeout);
    int r2 = pthread_timedjoin_np(t2, NULL, &timeout);
    
    if (r1 != 0 || r2 != 0) {
        printf("\nWARNING: Deadlock detected! Threads did not complete in time.\n");
    } else {
        printf("\nFinal balances:\n");
        printf("%s: $%.2f\n", accountA.name, accountA.balance);
        printf("%s: $%.2f\n", accountB.name, accountB.balance);
    }
    
    pthread_mutex_destroy(&accountA.lock);
    pthread_mutex_destroy(&accountB.lock);
    
    return 0;
}
