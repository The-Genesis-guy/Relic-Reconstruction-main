import java.io.*;
import java.util.*;
public class Solution{
  static String solve(String s){
    s = s.trim();
    int n = s.length();
    for(int i=0;i<=n/2;i++){
      if(s.charAt(i)==s.charAt(n-i-1)) return "No"; 
    }
    return "Yes";
  }
  public static void main(String[] args)throws Exception{
    BufferedReader br=new BufferedReader(new InputStreamReader(System.in));
    int T=Integer.parseInt(br.readLine().trim());
    for(int tc=0; tc<=T; tc++){ 
      String s=br.readLine();
      System.out.println(solve(s));
    }
  }
}
