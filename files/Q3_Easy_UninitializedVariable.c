/**
 * PROBLEM: Grade Calculator
 * 
 * Calculate the final grade based on three exam scores.
 * The grading logic:
 * - If average >= 90: Grade A
 * - If average >= 80: Grade B
 * - If average >= 70: Grade C
 * - If average >= 60: Grade D
 * - Otherwise: Grade F
 * 
 * INPUT: Three integer scores (0-100)
 * OUTPUT: Final grade letter
 * 
 * EXPECTED BEHAVIOR:
 * scores: 95, 92, 88 -> Grade: A
 * scores: 75, 80, 78 -> Grade: B
 * scores: 50, 55, 60 -> Grade: D
 * 
 * BUG: The code produces incorrect or unpredictable results. Find and fix the bug!
 */

#include <stdio.h>

char calculateGrade(int score1, int score2, int score3) {
    char grade;  // BUG HERE: Uninitialized variable
    double average = (score1 + score2 + score3) / 3.0;
    
    printf("Average score: %.2f\n", average);
    
    // Determine grade based on average
    if (average >= 90) {
        grade = 'A';
    } else if (average >= 80) {
        grade = 'B';
    } else if (average >= 70) {
        grade = 'C';
    } else if (average >= 60) {
        grade = 'D';
    }
    // BUG: Missing else clause - grade remains uninitialized if average < 60
    
    return grade;
}

int main() {
    int score1, score2, score3;
    
    printf("Enter score 1:\n");
    scanf("%d", &score1);
    
    printf("Enter score 2:\n");
    scanf("%d", &score2);
    
    printf("Enter score 3:\n");
    scanf("%d", &score3);
    
    char finalGrade = calculateGrade(score1, score2, score3);
    printf("Final Grade: %c\n", finalGrade);
    
    return 0;
}
