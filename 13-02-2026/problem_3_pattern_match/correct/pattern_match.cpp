// PROBLEM 3: PATTERN MATCH COUNT - CORRECT C++
// ===================================================
#include <iostream>
#include <string>
using namespace std;

int main() {
    string t, p;
    getline(cin, t);
    getline(cin, p);
    
    int n = t.length();
    int m = p.length();
    int count = 0;
    
    for (int i = 0; i <= n - m; i++) {
        if (t.substr(i, m) == p) {
            count++;
        }
    }
    
    cout << count << endl;
    return 0;
}