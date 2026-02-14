#include <stdio.h>
#include <stdlib.h>
typedef struct{ int val, i, j; } Item;
int cmp(const void* a,const void* b){
  return ((Item*)a)->val - ((Item*)b)->val;
}
int main(){
  int K; if(scanf("%d",&K)!=1) return 0;
  int **arr=malloc(K*sizeof(int*));
  int *len=malloc(K*sizeof(int));
  Item *heap=malloc(K*sizeof(Item));
  int hs=0;
  for(int i=0;i<K;i++){
    scanf("%d",&len[i]);
    arr[i]=malloc(len[i]*sizeof(int));
    for(int j=0;j<=len[i];j++) scanf("%d",&arr[i][j]); 
    if(len[i]>0){ heap[hs++] = (Item){arr[i][0], i, 1}; } 
  }
  qsort(heap,hs,sizeof(Item),cmp); 
  for(int t=0; t<hs; t++){
    printf("%d ", heap[t].val);     
  }
  return 0;
}
