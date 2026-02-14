/**
 * PROBLEM: Movie Ticket Price Calculator
 * 
 * Calculate ticket price based on day of the week and apply discounts.
 * Pricing structure:
 * - Monday-Thursday: $10 (Regular days)
 * - Friday: $12 (Weekend starts)
 * - Saturday-Sunday: $15 (Peak weekend)
 * 
 * Special discounts:
 * - Friday gets $2 discount (Final: $10)
 * - Weekend days get free popcorn (message only, no price change)
 * 
 * INPUT: Day number (1=Monday, 2=Tuesday, ..., 7=Sunday)
 * OUTPUT: Final ticket price and any special offers
 * 
 * EXPECTED BEHAVIOR:
 * Day 1 (Mon): $10, No special offer
 * Day 5 (Fri): $10 (after $2 discount), No special offer
 * Day 6 (Sat): $15, Free popcorn included
 * 
 * BUG: The code produces incorrect prices. Find and fix the bug!
 */

#include <iostream>
#include <string>
using namespace std;

void calculateTicketPrice(int day) {
    int basePrice = 0;
    string dayName = "";
    string specialOffer = "No special offer";
    
    switch(day) {
        case 1:
            dayName = "Monday";
            basePrice = 10;
            break;
        case 2:
            dayName = "Tuesday";
            basePrice = 10;
            break;
        case 3:
            dayName = "Wednesday";
            basePrice = 10;
            break;
        case 4:
            dayName = "Thursday";
            basePrice = 10;
            break;
        case 5:
            dayName = "Friday";
            basePrice = 12;
            // Apply Friday discount
            basePrice -= 2;
            // BUG HERE: Missing break - falls through to Saturday case
        case 6:
            if (dayName.empty()) dayName = "Saturday";
            if (basePrice == 0) basePrice = 15;
            specialOffer = "Free popcorn included";
            break;
        case 7:
            dayName = "Sunday";
            basePrice = 15;
            specialOffer = "Free popcorn included";
            break;
        default:
            cout << "Invalid day number" << endl;
            return;
    }
    
    cout << "Day: " << dayName << endl;
    cout << "Ticket Price: $" << basePrice << endl;
    cout << "Special Offer: " << specialOffer << endl;
}

int main() {
    int day;
    
    cout << "Enter day number (1=Mon, 2=Tue, ..., 7=Sun):" << endl;
    cin >> day;
    
    calculateTicketPrice(day);
    
    return 0;
}
