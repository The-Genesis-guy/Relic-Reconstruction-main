"""
PROBLEM: Student Record Manager

Create a backup copy of student records before modifying them.
The program should maintain original records intact while allowing modifications to copies.

INPUT: Student name and grades
OUTPUT: Original and modified student records

EXPECTED BEHAVIOR:
Original: Alice [85, 90, 88]
After modification:
  Original: Alice [85, 90, 88] (unchanged)
  Modified: Alice [95, 90, 88] (first grade changed)

BUG: The code incorrectly modifies the original record. Find and fix the bug!
"""

class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades
    
    # BUG HERE: Shallow copy - only copies reference, not list content
    def createBackup(self):
        backup = Student(self.name, self.grades)
        return backup
    
    def displayInfo(self, label):
        grades_str = ", ".join(map(str, self.grades))
        print(f"{label}: {self.name} [{grades_str}]")

def main():
    name = input("Enter student name:\n")
    n = int(input("Enter number of grades:\n"))
    
    grades = []
    print(f"Enter {n} grades:")
    for i in range(n):
        grades.append(int(input()))
    
    original = Student(name, grades)
    backup = original.createBackup()
    
    print("\nBefore modification:")
    original.displayInfo("Original")
    backup.displayInfo("Backup")
    
    print("\nModifying backup's first grade to 95...")
    backup.grades[0] = 95
    
    print("\nAfter modification:")
    original.displayInfo("Original")
    backup.displayInfo("Backup")
    
    print("\nExpected: Original should remain unchanged")
    print("Bug: Both records are modified!")

if __name__ == "__main__":
    main()
