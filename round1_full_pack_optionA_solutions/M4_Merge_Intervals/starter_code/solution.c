#include <stdio.h>
#include <stdlib.h>
typedef struct{ long long s,e; } I;
int cmp(const void* a,const void* b){
  I* x=(I*)a; I* y=(I*)b;
  return (x->e > y->e) - (x->e < y->e); 
}
int main(){
  int n; scanf("%d",&n);
  I* it=malloc(sizeof(I)*n);
  for(int i=0;i<n;i++){ scanf("%lld %lld",&it[i].s,&it[i].e); }
  qsort(it,n,sizeof(I),cmp);
  long long cs=it[0].s, ce=it[0].e;
  for(int i=1;i<n;i++){
    if(it[i].s<=ce){
      if(it[i].e<ce) ce=it[i].e; 
    }else{
      printf("%lld %lld\n",cs,ce);
      cs=it[i].s; ce=it[i].e;
    }
  }
  printf("%lld %lld\n",cs,ce);
}
