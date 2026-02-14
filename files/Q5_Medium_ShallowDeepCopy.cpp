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

#include <iostream>
#include <vector>
#include <string>
using namespace std;

class Student {
public:
    string name;
    vector<int>* grades;  // Using pointer to simulate shallow copy issue
    
    Student(string n, vector<int>* g) : name(n), grades(g) {}
    
    // BUG HERE: Shallow copy - only copies pointer, not vector content
    Student* createBackup() {
        Student* backup = new Student(this->name, this->grades);
        return backup;
    }
    
    void displayInfo(string label) {
        cout << label << ": " << name << " [";
        for (size_t i = 0; i < grades->size(); i++) {
            cout << (*grades)[i];
            if (i < grades->size() - 1) cout << ", ";
        }
        cout << "]" << endl;
    }
};

int main() {
    string name;
    int n;
    
    cout << "Enter student name:" << endl;
    getline(cin, name);
    
    cout << "Enter number of grades:" << endl;
    cin >> n;
    
    vector<int>* grades = new vector<int>(n);
    cout << "Enter " << n << " grades:" << endl;
    for (int i = 0; i < n; i++) {
        cin >> (*grades)[i];
    }
    
    Student* original = new Student(name, grades);
    Student* backup = original->createBackup();
    
    cout << "\nBefore modification:" << endl;
    original->displayInfo("Original");
    backup->displayInfo("Backup");
    
    cout << "\nModifying backup's first grade to 95..." << endl;
    (*backup->grades)[0] = 95;
    
    cout << "\nAfter modification:" << endl;
    original->displayInfo("Original");
    backup->displayInfo("Backup");
    
    cout << "\nExpected: Original should remain unchanged" << endl;
    cout << "Bug: Both records are modified!" << endl;
    
    delete grades;
    delete original;
    delete backup;
    
    return 0;
}
