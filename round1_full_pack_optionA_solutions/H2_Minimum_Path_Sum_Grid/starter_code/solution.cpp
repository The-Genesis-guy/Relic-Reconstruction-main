#include <bits/stdc++.h>
using namespace std;
int main(){
  int r,c; cin>>r>>c;
  vector<vector<long long>> g(r, vector<long long>(c));
  for(int i=0;i<r;i++) for(int j=0;j<c;j++) cin>>g[i][j];
  vector<vector<long long>> dp(r, vector<long long>(c,0));
  dp[0][0]=0; 
  for(int j=1;j<c;j++) dp[0][j]=dp[0][j-1]+g[0][j];
  for(int i=1;i<r;i++) dp[i][0]=dp[i-1][0]+g[i][0];
  for(int i=1;i<r;i++) for(int j=1;j<c;j++)
    dp[i][j]=g[i][j]+max(dp[i-1][j],dp[i][j-1]); 
  cout<<dp[r-1][c-1]<<"\n";
}
