import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int n = sc.nextInt();
        int m = sc.nextInt();
        int q = sc.nextInt();

        List<Integer>[] adj = new ArrayList[n + 1];
        for (int i = 1; i <= n; i++)
            adj[i] = new ArrayList<>();

        // Read edges (undirected)
        for (int i = 0; i < m; i++) {
            int u = sc.nextInt();
            int v = sc.nextInt();
            adj[u].add(v);
            adj[v].add(u);
        }

        while (q-- > 0) {
            int s = sc.nextInt();
            int t = sc.nextInt();

            boolean[] vis = new boolean[n + 1];
            Queue<Integer> queue = new LinkedList<>();

            queue.add(s);
            vis[s] = true;

            boolean found = false;

            while (!queue.isEmpty()) {
                int x = queue.poll();

                if (x == t) {
                    found = true;
                    break;
                }

                for (int nb : adj[x]) {
                    if (!vis[nb]) {
                        vis[nb] = true;
                        queue.add(nb);
                    }
                }
            }

            System.out.println(found ? "Yes" : "No");
        }

        sc.close();
    }
}
