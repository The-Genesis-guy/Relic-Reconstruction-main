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

#include <iostream>
using namespace std;

char calculateGrade(int score1, int score2, int score3) {
    char grade;  // BUG HERE: Uninitialized variable
    double average = (score1 + score2 + score3) / 3.0;
    
    cout << "Average score: " << average << endl;
    
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
    
    cout << "Enter score 1:" << endl;
    cin >> score1;
    
    cout << "Enter score 2:" << endl;
    cin >> score2;
    
    cout << "Enter score 3:" << endl;
    cin >> score3;
    
    char finalGrade = calculateGrade(score1, score2, score3);
    cout << "Final Grade: " << finalGrade << endl;
    
    return 0;
}
