"""
PROBLEM: Grade Calculator

Calculate the final grade based on three exam scores.
The grading logic:
- If average >= 90: Grade A
- If average >= 80: Grade B
- If average >= 70: Grade C
- If average >= 60: Grade D
- Otherwise: Grade F

INPUT: Three integer scores (0-100)
OUTPUT: Final grade letter

EXPECTED BEHAVIOR:
scores: 95, 92, 88 -> Grade: A
scores: 75, 80, 78 -> Grade: B
scores: 50, 55, 60 -> Grade: D

BUG: The code produces incorrect or unpredictable results. Find and fix the bug!
"""

def calculateGrade(score1, score2, score3):
    # BUG HERE: grade not initialized before conditional checks
    average = (score1 + score2 + score3) / 3.0
    
    print(f"Average score: {average}")
    
    # Determine grade based on average
    if average >= 90:
        grade = 'A'
    elif average >= 80:
        grade = 'B'
    elif average >= 70:
        grade = 'C'
    elif average >= 60:
        grade = 'D'
    # BUG: Missing else clause - grade remains uninitialized if average < 60
    
    return grade

def main():
    score1 = int(input("Enter score 1:\n"))
    score2 = int(input("Enter score 2:\n"))
    score3 = int(input("Enter score 3:\n"))
    
    finalGrade = calculateGrade(score1, score2, score3)
    print(f"Final Grade: {finalGrade}")

if __name__ == "__main__":
    main()
