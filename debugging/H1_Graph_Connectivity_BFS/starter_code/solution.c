#include <stdio.h>
#include <stdlib.h>
typedef struct Node{int v; struct Node* next;} Node;
int main(){
  int n,m,q; if(scanf("%d %d %d",&n,&m,&q)!=3) return 0;
  Node** adj=(Node**)calloc(n,sizeof(Node*)); 
  for(int i=0;i<m;i++){
    int u,v; scanf("%d %d",&u,&v);
    Node* a=(Node*)malloc(sizeof(Node)); a->v=v; a->next=adj[u]; adj[u]=a; 
    
  }
  int* vis=(int*)calloc(n,sizeof(int)); 
  int* qarr=(int*)malloc(n*sizeof(int)); 
  while(q--){
    int s,t; scanf("%d %d",&s,&t);
    for(int i=0;i<n;i++) vis[i]=0;
    int head=0,tail=0; qarr[tail++]=s; vis[s]=1;
    int found=0;
    while(head<tail){
      int x=qarr[head++];
      if(x==t){found=1;break;}
      for(Node* p=adj[x]; p; p=p->next){
        int nb=p->v;
        if(!vis[nb]){ vis[nb]=1; qarr[tail++]=nb; }
      }
    }
    puts(found?"Yes":"No");
  }
}
