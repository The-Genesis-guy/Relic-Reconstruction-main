#include <bits/stdc++.h>
using namespace std;
int main(){
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n,m,q; cin>>n>>m>>q;
  vector<vector<int>> adj(n); 
  for(int i=0;i<m;i++){
    int u,v; cin>>u>>v;
    adj[u].push_back(v);     
  }
  while(q--){
    int s,t; cin>>s>>t;
    vector<int> vis(n,0);
    queue<int> qu; qu.push(s); vis[s]=1;
    bool found=false;
    while(!qu.empty()){
      int x=qu.front(); qu.pop();
      if(x==t){found=true;break;}
      for(int nb: adj[x]){
        if(vis[nb]) continue;
        qu.push(nb);          
      }
    }
    cout<<(found?"Yes":"No")<<"\n";
  }
}
