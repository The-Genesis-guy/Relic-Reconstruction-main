#include <bits/stdc++.h>
using namespace std;
int main(){
  int n,amt; cin>>n>>amt;
  vector<int> c(n); for(int i=0;i<n;i++) cin>>c[i];
  const int INF=1e9;
  vector<int> dp(amt+1,INF);
  dp[0]=1; 
  for(int coin: c){
    for(int a=coin;a<=amt;a++){
      dp[a]=min(dp[a], dp[a-coin]);
    }
  }
  cout<<(dp[amt]>=INF?-1:dp[amt])<<"\n";
}
