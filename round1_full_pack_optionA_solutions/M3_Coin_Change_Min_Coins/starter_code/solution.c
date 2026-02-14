#include <stdio.h>
#define INF 1000000000
int min(int a,int b){return a<b?a:b;}
int main(){
  int n,amt; scanf("%d %d",&n,&amt);
  int c[55]; for(int i=0;i<n;i++) scanf("%d",&c[i]);
  static int dp[100005];
  for(int i=0;i<=amt;i++) dp[i]=INF;
  dp[0]=1; 
  for(int i=0;i<n;i++){
    for(int a=c[i]; a<=amt; a++){
      dp[a]=min(dp[a], dp[a-c[i]]); 
    }
  }
  printf("%d\n", dp[amt]>=INF?-1:dp[amt]);
}
