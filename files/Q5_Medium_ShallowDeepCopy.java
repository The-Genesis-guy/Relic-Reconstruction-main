/**
 * PROBLEM: Student Record Manager
 * 
 * Create a backup copy of student records before modifying them.
 * The program should maintain original records intact while allowing modifications to copies.
 * 
 * INPUT: Student name and grades
 * OUTPUT: Original and modified student records
 * 
 * EXPECTED BEHAVIOR:
 * Original: Alice [85, 90, 88]
 * After modification:
 *   Original: Alice [85, 90, 88] (unchanged)
 *   Modified: Alice [95, 90, 88] (first grade changed)
 * 
 * BUG: The code incorrectly modifies the original record. Find and fix the bug!
 */

import java.util.*;

class Student {
    String name;
    int[] grades;
    
    public Student(String name, int[] grades) {
        this.name = name;
        this.grades = grades;
    }
    
    // BUG HERE: Shallow copy - only copies reference, not the array content
    public Student createBackup() {
        Student backup = new Student(this.name, this.grades);
        return backup;
    }
    
    public void displayInfo(String label) {
        System.out.print(label + ": " + name + " [");
        for (int i = 0; i < grades.length; i++) {
            System.out.print(grades[i]);
            if (i < grades.length - 1) System.out.print(", ");
        }
        System.out.println("]");
    }
}

public class Q5_Medium_ShallowDeepCopy {
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        System.out.println("Enter student name:");
        String name = sc.nextLine();
        
        System.out.println("Enter number of grades:");
        int n = sc.nextInt();
        
        int[] grades = new int[n];
        System.out.println("Enter " + n + " grades:");
        for (int i = 0; i < n; i++) {
            grades[i] = sc.nextInt();
        }
        
        Student original = new Student(name, grades);
        Student backup = original.createBackup();
        
        System.out.println("\nBefore modification:");
        original.displayInfo("Original");
        backup.displayInfo("Backup");
        
        // Modify the backup's first grade
        System.out.println("\nModifying backup's first grade to 95...");
        backup.grades[0] = 95;
        
        System.out.println("\nAfter modification:");
        original.displayInfo("Original");
        backup.displayInfo("Backup");
        
        System.out.println("\nExpected: Original should remain unchanged");
        System.out.println("Bug: Both records are modified!");
        
        sc.close();
    }
}
