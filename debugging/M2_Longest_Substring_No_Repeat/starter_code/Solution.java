import java.io.*;import java.util.*;
public class Solution{
  public static void main(String[] args)throws Exception{
    String s=new BufferedReader(new InputStreamReader(System.in)).readLine();
    int[] last=new int[256]; Arrays.fill(last,-1);
    int l=0,best=0;
    for(int r=0;r<s.length();r++){
      int c=s.charAt(r);
      if(last[c]>=l) l=last[c];      
      last[c]=r;
      best=Math.max(best,r-l);       
    }
    System.out.println(best);
  }
}
