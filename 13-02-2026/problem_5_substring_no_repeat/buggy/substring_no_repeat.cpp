// ============================================
#include <bits/stdc++.h>
using namespace std;

int main() {
    string s;
    cin >> s;
    vector<int> st;
    st.push_back(0);
    int best = 0;
    
    for (int i = 0; i < (int)s.size(); i++) {
        if (s[i] == ')') {
            st.push_back(i);
        } else {
            st.pop_back();
            if (st.empty()) {
                st.push_back(i - 1);
            }
            best = max(best, i - st.back());
        }
    }
    
    cout << best << "\n";
}


// =============================================
// PROBLEM 2: LONGEST SUBSTRING NO REPEAT - BUGGY C++