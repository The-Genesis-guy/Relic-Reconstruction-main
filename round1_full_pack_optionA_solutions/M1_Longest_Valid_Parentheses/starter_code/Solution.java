import java.io.*;import java.util.*;
public class Solution{
  public static void main(String[] args)throws Exception{
    String s=new BufferedReader(new InputStreamReader(System.in)).readLine();
    int[] st=new int[s.length()+5];
    int top=0; st[top]=0; 
    int best=0;
    for(int i=0;i<s.length();i++){
      char c=s.charAt(i);
      if(c==')') st[++top]=i; 
      else{
        top--;
        if(top>=0) best=Math.max(best, i-st[top]);
        else st[++top]=0;     
      }
    }
    System.out.println(best);
  }
}
