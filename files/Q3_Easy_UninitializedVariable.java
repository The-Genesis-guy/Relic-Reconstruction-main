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

import java.util.*;

public class Q3_Easy_UninitializedVariable {
    
    public static char calculateGrade(int score1, int score2, int score3) {
        char grade;  // BUG HERE: Uninitialized variable
        double average = (score1 + score2 + score3) / 3.0;
        
        System.out.println("Average score: " + average);
        
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
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        System.out.println("Enter score 1:");
        int score1 = sc.nextInt();
        
        System.out.println("Enter score 2:");
        int score2 = sc.nextInt();
        
        System.out.println("Enter score 3:");
        int score3 = sc.nextInt();
        
        char finalGrade = calculateGrade(score1, score2, score3);
        System.out.println("Final Grade: " + finalGrade);
        
        sc.close();
    }
}
