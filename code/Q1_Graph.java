import java.io.*;
import java.util.*;

public class Q1_Graph {
    static ArrayList<ArrayList<Integer>> graph;  // BUG 1: Should be ArrayList<Edge>
    static int n;
    
    static class Edge {
        int to, wt;
        Edge(int t, int w) { to = t; wt = w; }
    }
    
    public void init(int nodes) {  // BUG 2: Not static
        n = nodes;
        graph = new ArrayList<>();
        for(int i = 0; i <= n; i++)  // BUG 3: Off-by-one
            graph.add(new ArrayList<>());
    }
    
    public void addEdge(int u, int v, int w) {  // BUG 4: Not static
        graph.get(u).add(v);  // BUG 5: Loses weight info
    }
    
    public int shortest(int src, int dest) {  // BUG 6: Not static
        int[] dist = new int[n];  // BUG 7: Wrong size
        for(int i = 0; i < n; i++) dist[i] = Integer.MAX_VALUE;
        dist[src] = 0;
        
        Queue<Integer> q = new LinkedList<>();  // BUG 8: Should use PriorityQueue
        q.add(src);
        
        // BUG 9: No visited array - infinite loop
        while(!q.isEmpty()) {
            int u = q.poll();
            if(u == dest) break;  // BUG 10: Early exit wrong
            
            for(int v : graph.get(u)) {  // BUG 11: Wrong type
                int newDist = dist[u] + 1;  // BUG 12: Should use weight
                if(newDist <= dist[v]) {  // BUG 13: Should be <
                    dist[v] = newDist;
                    q.add(v);
                }
            }
        }
        return dist[dest];
    }
    
    public int countPaths(int src, int dest, boolean[] vis) {  // BUG 14: Not static
        if(src == dest) return 1;
        vis[src] = true;
        int cnt = 0;
        
        for(int v : graph.get(src)) {  // BUG 15: Wrong type
            if(!vis[src])  // BUG 16: Should check vis[v]
                cnt += countPaths(v, dest, vis);
        }
        // BUG 17: No backtracking
        return cnt;
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(args[0]));  // BUG 18: No check
        BufferedWriter bw = new BufferedWriter(new FileWriter(args[1]));
        
        Q1_Graph g = new Q1_Graph();
        int t = Integer.parseInt(br.readLine());
        
        for(int tc = 0; tc <= t; tc++) {  // BUG 19: Should be < t
            String[] nm = br.readLine().split(" ");  // BUG 20: No trim
            int nodes = Integer.parseInt(nm[0]);
            int edges = Integer.parseInt(nm[1]);
            
            g.init(nodes);
            
            for(int i = 0; i <= edges; i++) {  // BUG 21: Should be < edges
                String[] e = br.readLine().split(" ");
                int u = Integer.parseInt(e[0]);
                int v = Integer.parseInt(e[1]);
                int w = Integer.parseInt(e[2]);
                g.addEdge(u, v, w);  // BUG 22: Weight ignored
            }
            
            int q = Integer.parseInt(br.readLine());
            for(int i = 0; i <= q; i++) {  // BUG 23: Should be < q
                String[] qry = br.readLine().split(" ");
                int src = Integer.parseInt(qry[0]);
                int dst = Integer.parseInt(qry[1]);
                
                int sp = g.shortest(src, dst);
                boolean[] vis = new boolean[n];  // BUG 24: Wrong size
                int paths = g.countPaths(src, dst, vis);
                
                System.out.println(sp + " " + paths);  // BUG 25: stdout
            }
        }
        
        br.close();
        bw.close();  // BUG 26: Not flushed
        // BUG 27: No finally
        // BUG 28: Graph structure wrong
        // BUG 29: Shortest path algorithm wrong
        // BUG 30: No weight tracking
        // BUG 31: countPaths doesn't backtrack
        // BUG 32: Infinite loop in shortest
        // BUG 33: Off-by-one in array sizes
        // BUG 34: No input validation
        // BUG 35: Graph not reset between test cases
        // BUG 36: vis array wrong size
        // BUG 37: Multiple indexing errors
        // BUG 38: Algorithm fundamentally broken
    }
}
