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

#include <stdio.h>
#include <string.h>

void calculateTicketPrice(int day) {
    int basePrice = 0;
    char dayName[20] = "";
    char specialOffer[50] = "No special offer";
    
    switch(day) {
        case 1:
            strcpy(dayName, "Monday");
            basePrice = 10;
            break;
        case 2:
            strcpy(dayName, "Tuesday");
            basePrice = 10;
            break;
        case 3:
            strcpy(dayName, "Wednesday");
            basePrice = 10;
            break;
        case 4:
            strcpy(dayName, "Thursday");
            basePrice = 10;
            break;
        case 5:
            strcpy(dayName, "Friday");
            basePrice = 12;
            // Apply Friday discount
            basePrice -= 2;
            // BUG HERE: Missing break - falls through to Saturday case
        case 6:
            if (strlen(dayName) == 0) strcpy(dayName, "Saturday");
            if (basePrice == 0) basePrice = 15;
            strcpy(specialOffer, "Free popcorn included");
            break;
        case 7:
            strcpy(dayName, "Sunday");
            basePrice = 15;
            strcpy(specialOffer, "Free popcorn included");
            break;
        default:
            printf("Invalid day number\n");
            return;
    }
    
    printf("Day: %s\n", dayName);
    printf("Ticket Price: $%d\n", basePrice);
    printf("Special Offer: %s\n", specialOffer);
}

int main() {
    int day;
    
    printf("Enter day number (1=Mon, 2=Tue, ..., 7=Sun):\n");
    scanf("%d", &day);
    
    calculateTicketPrice(day);
    
    return 0;
}
