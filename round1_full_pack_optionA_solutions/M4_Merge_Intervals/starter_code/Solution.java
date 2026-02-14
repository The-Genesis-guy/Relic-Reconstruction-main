import java.io.*;import java.util.*;
public class Solution{
  public static void main(String[] args)throws Exception{
    BufferedReader br=new BufferedReader(new InputStreamReader(System.in));
    int n=Integer.parseInt(br.readLine().trim());
    long[][] it=new long[n][2];
    for(int i=0;i<n;i++){
      StringTokenizer st=new StringTokenizer(br.readLine());
      it[i][0]=Long.parseLong(st.nextToken());
      it[i][1]=Long.parseLong(st.nextToken());
    }
    Arrays.sort(it,(a,b)->Long.compare(a[1],b[1])); 
    long cs=it[0][0], ce=it[0][1];
    for(int i=1;i<n;i++){
      if(it[i][0]<=ce) ce=Math.min(ce,it[i][1]); 
      else{ System.out.println(cs+" "+ce); cs=it[i][0]; ce=it[i][1]; }
    }
    System.out.println(cs+" "+ce);
  }
}
