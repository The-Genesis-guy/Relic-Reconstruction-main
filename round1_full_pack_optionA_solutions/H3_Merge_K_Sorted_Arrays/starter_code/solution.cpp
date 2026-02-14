#include <iostream>
#include <vector>
#include <queue>
#include <functional>
using namespace std;
struct Item{ long long v; int i,j; };
int main(){
  int K; cin>>K;
  vector<vector<long long>> a(K);
  priority_queue<Item, vector<Item>, function<bool(const Item&,const Item&)>> pq(
    [](const Item& x,const Item& y){ return x.v<y.v; } 
  );
  for(int i=0;i<K;i++){
    int n; cin>>n;
    a[i].resize(n);
    for(int j=0;j<n;j++) cin>>a[i][j];
    if(n>0) pq.push({a[i][0],i,1}); 
  }
  vector<long long> res;
  while(!pq.empty()){
    auto it=pq.top(); pq.pop();
    res.push_back(it.v);
    if(it.j<= (int)a[it.i].size()){ 
      pq.push({a[it.i][it.j], it.i, it.j+1});
    }
  }
  for(size_t i=0;i<res.size();i++) cout<<res[i]<<(i+1==res.size()?'\n':' ');
}
