#include <bits/stdc++.h>
using namespace std;
int main(){
  int n; cin>>n;
  vector<pair<long long,long long>> it(n);
  for(int i=0;i<n;i++) cin>>it[i].first>>it[i].second;
  sort(it.begin(), it.end(), [](auto &a, auto &b){ return a.second<b.second; });
  long long cs=it[0].first, ce=it[0].second;
  for(int i=1;i<n;i++){
    if(it[i].first<=ce) ce=min(ce,it[i].second); 
    else{ cout<<cs<<" "<<ce<<"\n"; cs=it[i].first; ce=it[i].second; }
  }
  cout<<cs<<" "<<ce<<"\n";
}
