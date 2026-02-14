#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    long long d, r;
    if (!(cin >> n >> d >> r)) return 0;

    vector<long long> p(n);
    for (int i = 0; i < n; i++) cin >> p[i];

    // TODO: determine if travel from 0 to d is possible using illuminated segments
    // Print "YES" or "NO".
    // cout << "YES\n";
    return 0;
}
