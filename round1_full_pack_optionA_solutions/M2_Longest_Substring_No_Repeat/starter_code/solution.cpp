#include <bits/stdc++.h>
using namespace std;
int main(){
  string s; getline(cin,s);
  vector<int> last(256,-1);
  int l=0,best=0;
  for(int r=0;r<(int)s.size();r++){
    unsigned char c=s[r];
    if(last[c]>=l) l=last[c];     
    last[c]=r;
    best=max(best,r-l);           
  }
  cout<<best<<"\n";
}
