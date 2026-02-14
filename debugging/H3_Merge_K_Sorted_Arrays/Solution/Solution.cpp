#include <bits/stdc++.h>
using namespace std;

int main() {
    int K;
    if (!(cin >> K)) return 0;

    vector<int> len(K);
    int total = 0;

    // Read sizes
    for (int i = 0; i < K; i++) {
        cin >> len[i];
        total += len[i];
    }

    vector<int> all;
    all.reserve(total);

    // Read elements
    for (int i = 0; i < K; i++) {
        for (int j = 0; j < len[i]; j++) {
            int x;
            cin >> x;
            all.push_back(x);
        }
    }

    // Sort
    sort(all.begin(), all.end());

    // Print
    for (int x : all)
        cout << x << " ";

    return 0;
}
