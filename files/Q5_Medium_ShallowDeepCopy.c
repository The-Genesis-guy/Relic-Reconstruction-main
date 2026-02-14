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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[50];
    int* grades;
    int numGrades;
} Student;

// BUG HERE: Shallow copy - only copies pointer, not the actual grade array
Student* createBackup(Student* original) {
    Student* backup = (Student*)malloc(sizeof(Student));
    strcpy(backup->name, original->name);
    backup->grades = original->grades;  // BUG: Copying pointer, not array content
    backup->numGrades = original->numGrades;
    return backup;
}

void displayInfo(Student* s, const char* label) {
    printf("%s: %s [", label, s->name);
    for (int i = 0; i < s->numGrades; i++) {
        printf("%d", s->grades[i]);
        if (i < s->numGrades - 1) printf(", ");
    }
    printf("]\n");
}

int main() {
    char name[50];
    int n;
    
    printf("Enter student name:\n");
    fgets(name, 50, stdin);
    name[strcspn(name, "\n")] = 0;
    
    printf("Enter number of grades:\n");
    scanf("%d", &n);
    
    Student* original = (Student*)malloc(sizeof(Student));
    strcpy(original->name, name);
    original->numGrades = n;
    original->grades = (int*)malloc(n * sizeof(int));
    
    printf("Enter %d grades:\n", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &original->grades[i]);
    }
    
    Student* backup = createBackup(original);
    
    printf("\nBefore modification:\n");
    displayInfo(original, "Original");
    displayInfo(backup, "Backup");
    
    printf("\nModifying backup's first grade to 95...\n");
    backup->grades[0] = 95;
    
    printf("\nAfter modification:\n");
    displayInfo(original, "Original");
    displayInfo(backup, "Backup");
    
    printf("\nExpected: Original should remain unchanged\n");
    printf("Bug: Both records are modified!\n");
    
    free(original->grades);
    free(original);
    free(backup);
    
    return 0;
}
