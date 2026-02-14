#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;

    vector<pair<long long, long long>> intervals(n);

    for (int i = 0; i < n; i++) {
        cin >> intervals[i].first >> intervals[i].second;
    }

    // Sort by start
    sort(intervals.begin(), intervals.end());

    long long cs = intervals[0].first;
    long long ce = intervals[0].second;

    for (int i = 1; i < n; i++) {
        if (intervals[i].first <= ce) {
            ce = max(ce, intervals[i].second);
        } else {
            cout << cs << " " << ce << "\n";
            cs = intervals[i].first;
            ce = intervals[i].second;
        }
    }

    cout << cs << " " << ce << "\n";

    return 0;
}
