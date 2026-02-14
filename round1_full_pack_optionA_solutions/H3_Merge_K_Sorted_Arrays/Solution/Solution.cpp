#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    int K;
    if (!(cin >> K)) return 0;

    vector<int> all;

    // Read each array
    for (int i = 0; i < K; i++) {
        int n;
        cin >> n;
        for (int j = 0; j < n; j++) {
            int x;
            cin >> x;
            all.push_back(x);
        }
    }

    // Sort
    sort(all.begin(), all.end());

    // Print
    for (int i = 0; i < all.size(); i++) {
        if (i > 0) cout << " ";
        cout << all[i];
    }
    cout << endl;

    return 0;
}
