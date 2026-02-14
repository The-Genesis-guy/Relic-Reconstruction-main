// PROBLEM 2: LONGEST SUBSTRING NO REPEAT - CORRECT C++
// =============================================
#include <iostream>
#include <vector>
using namespace std;

int main() {
    string s;
    
    if (!(cin >> s)) {
        cout << 0 << endl;
        return 0;
    }
    
    vector<int> last(256, -1);
    int l = 0, best = 0;
    
    for (int r = 0; r < s.length(); r++) {
        unsigned char c = s[r];
        
        if (last[c] >= l) {
            l = last[c] + 1;
        }
        
        last[c] = r;
        best = max(best, r - l + 1);
    }
    
    cout << best << endl;
    return 0;
}


// ===================================================