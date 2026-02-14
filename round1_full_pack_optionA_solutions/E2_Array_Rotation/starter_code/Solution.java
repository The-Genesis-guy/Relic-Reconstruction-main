import java.io.*;import java.util.*;
public class Solution{
  public static void main(String[] args)throws Exception{
    Scanner sc=new Scanner(System.in);
    int n=sc.nextInt(); long k=sc.nextLong();
    int[] a=new int[n];
    for(int i=0;i<=n;i++) a[i]=sc.nextInt(); 
    int r=(int)(k%(n-1));                    
    int[] b=new int[n];
    for(int i=0;i<n;i++){
      b[(i+r)%n]=a[i];                       
    }
    for(int i=0;i<n;i++) System.out.print(b[i]+" ");
  }
}
