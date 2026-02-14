import java.io.*;import java.util.*;
public class Solution{
  public static void main(String[] args)throws Exception{
    FastScanner fs=new FastScanner(System.in);
    int n=fs.nextInt(), m=fs.nextInt(), q=fs.nextInt();
    ArrayList<Integer>[] adj=new ArrayList[n]; 
    for(int i=0;i<n;i++) adj[i]=new ArrayList<>();
    for(int i=0;i<m;i++){
      int u=fs.nextInt(), v=fs.nextInt();
      adj[u].add(v); 
    }
    while(q-- > 0){
      int s=fs.nextInt(), t=fs.nextInt();
      boolean[] vis=new boolean[n]; 
      ArrayDeque<Integer> qu=new ArrayDeque<>();
      qu.add(s); vis[s]=true;
      boolean found=false;
      while(!qu.isEmpty()){
        int x=qu.poll();
        if(x==t){found=true;break;}
        for(int nb: adj[x]){
          if(vis[nb]) continue;
          qu.add(nb); 
        }
      }
      System.out.println(found?"Yes":"No");
    }
  }
  static class FastScanner{
    private final InputStream in; private final byte[] buf=new byte[1<<16];
    private int ptr=0,len=0;
    FastScanner(InputStream is){in=is;}
    int read() throws IOException{ if(ptr>=len){ len=in.read(buf); ptr=0; if(len<=0) return -1;} return buf[ptr++];}
    int nextInt() throws IOException{
      int c; do{ c=read(); }while(c<=32);
      int sgn=1; if(c=='-'){sgn=-1;c=read();}
      int x=0; while(c>32){ x=x*10+(c-'0'); c=read(); }
      return x*sgn;
    }
  }
}
