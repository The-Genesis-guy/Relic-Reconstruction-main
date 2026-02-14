// ===================================================
// PROBLEM 3: PATTERN MATCH COUNT - BUGGY C++
// ===================================================
#include <bits/stdc++.h>
using namespace std;

int main() {
    string t, p;
    getline(cin, t);
    getline(cin, p);
    int cnt = 0;
    
    for (size_t i = 0; i + t.size() <= p.size(); i++) {
        if (t.substr(i, p.size()) == p) {
            cnt++;
        }
    }
    
    cout << cnt << "\n";
}
