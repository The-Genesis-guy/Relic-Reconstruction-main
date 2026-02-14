"""
PROBLEM: Movie Ticket Price Calculator

Calculate ticket price based on day of the week and apply discounts.
Pricing structure:
- Monday-Thursday: $10 (Regular days)
- Friday: $12 (Weekend starts)
- Saturday-Sunday: $15 (Peak weekend)

Special discounts:
- Friday gets $2 discount (Final: $10)
- Weekend days get free popcorn (message only, no price change)

INPUT: Day number (1=Monday, 2=Tuesday, ..., 7=Sunday)
OUTPUT: Final ticket price and any special offers

EXPECTED BEHAVIOR:
Day 1 (Mon): $10, No special offer
Day 5 (Fri): $10 (after $2 discount), No special offer
Day 6 (Sat): $15, Free popcorn included

BUG: The code produces incorrect prices. Find and fix the bug!
"""

def calculateTicketPrice(day):
    basePrice = 0
    dayName = ""
    specialOffer = "No special offer"
    
    # Python doesn't have switch-case (before 3.10) or traditional fall-through
    # Simulating fall-through bug with conditional logic
    
    if day == 1:
        dayName = "Monday"
        basePrice = 10
    elif day == 2:
        dayName = "Tuesday"
        basePrice = 10
    elif day == 3:
        dayName = "Wednesday"
        basePrice = 10
    elif day == 4:
        dayName = "Thursday"
        basePrice = 10
    elif day == 5:
        dayName = "Friday"
        basePrice = 12
        # Apply Friday discount
        basePrice -= 2
        # BUG HERE: Intentionally proceeding to Saturday logic (simulating fall-through)
        # The following lines simulate fall-through behavior
        day = 6  # This simulates fall-through by changing day
        
    if day == 6:  # BUG: Using 'if' instead of 'elif' causes Friday to execute this too
        if dayName == "":
            dayName = "Saturday"
        if basePrice == 0:
            basePrice = 15
        specialOffer = "Free popcorn included"
    elif day == 7:
        dayName = "Sunday"
        basePrice = 15
        specialOffer = "Free popcorn included"
    elif day > 7 or day < 1:
        print("Invalid day number")
        return
    
    print(f"Day: {dayName}")
    print(f"Ticket Price: ${basePrice}")
    print(f"Special Offer: {specialOffer}")

def main():
    day = int(input("Enter day number (1=Mon, 2=Tue, ..., 7=Sun):\n"))
    calculateTicketPrice(day)

if __name__ == "__main__":
    main()
