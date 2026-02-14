#include <stdio.h>
#include <string.h>
int main(){
  char s[200005]; scanf("%s",s);
  int n=strlen(s);
  int st[200005], top=-1;
  st[++top]=0;                 
  int best=0;
  for(int i=0;i<n;i++){
    if(s[i]=='(') st[++top]=i;
    else{
      top--;
      if(top!=-1){
        int len=i-st[top];
        if(len>best) best=len;
      }else{
        st[++top]=0;           
      }
    }
  }
  printf("%d\n",best);
}
