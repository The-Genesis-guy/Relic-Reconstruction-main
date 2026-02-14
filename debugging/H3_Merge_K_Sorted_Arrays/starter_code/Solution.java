import java.io.*;import java.util.*;
public class Solution{
  static class Item{ int v,i,j; Item(int v,int i,int j){this.v=v;this.i=i;this.j=j;} }
  public static void main(String[] args)throws Exception{
    BufferedReader br=new BufferedReader(new InputStreamReader(System.in));
    int K=Integer.parseInt(br.readLine().trim());
    ArrayList<int[]> arrays=new ArrayList<>();
    PriorityQueue<Item> pq=new PriorityQueue<>((a,b)->b.v-a.v); 
    for(int i=0;i<K;i++){
      StringTokenizer st=new StringTokenizer(br.readLine());
      int n=Integer.parseInt(st.nextToken());
      int[] arr=new int[n];
      for(int j=0;j<n;j++) arr[j]=Integer.parseInt(st.nextToken());
      arrays.add(arr);
      if(n>0) pq.add(new Item(arr[0],i,1)); 
    }
    StringBuilder sb=new StringBuilder();
    while(!pq.isEmpty()){
      Item it=pq.poll();
      sb.append(it.v).append(' ');
      int[] arr=arrays.get(it.i);
      if(it.j<=arr.length){ 
        pq.add(new Item(arr[it.j], it.i, it.j+1));
      }
    }
    System.out.print(sb.toString().trim());
  }
}
