#include <bits/stdc++.h>
using namespace std;

int main() {
    string s;
    
    if (!(cin >> s)) {   // handle empty input
        cout << 0 << endl;
        return 0;
    }

    int n = s.length();
    stack<int> st;
    
    st.push(-1);   // base index
    int best = 0;

    for (int i = 0; i < n; i++) {
        if (s[i] == '(') {
            st.push(i);
        } else {
            st.pop();
            if (!st.empty()) {
                best = max(best, i - st.top());
            } else {
                st.push(i);
            }
        }
    }

    cout << best << endl;
    return 0;
}
