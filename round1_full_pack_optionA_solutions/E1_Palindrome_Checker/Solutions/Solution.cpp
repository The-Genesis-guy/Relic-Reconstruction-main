#include <iostream>
#include <string>
using namespace std;

int main() {
    int T;
    cin >> T;

    while (T--) {
        string s;
        cin >> s;

        int n = s.length();
        bool ok = true;

        for (int i = 0; i < n / 2; i++) {
            if (s[i] != s[n - i - 1]) {
                ok = false;
                break;
            }
        }

        if (ok)
            cout << "Yes\n";
        else
            cout << "No\n";
    }

    return 0;
}
