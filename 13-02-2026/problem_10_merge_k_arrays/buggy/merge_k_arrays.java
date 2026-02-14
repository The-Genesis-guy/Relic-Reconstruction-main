// =============================================
import java.io.*;
import java.util.*;

public class Solution {
    public static void main(String[] args) throws Exception {
        FastScanner fs = new FastScanner(System.in);
        int r = fs.nextInt(), c = fs.nextInt();
        long[][] g = new long[r][c];
        
        for (int i = 0; i < r; i++) {
            for (int j = 0; j < c; j++) {
                g[i][j] = fs.nextLong();
            }
        }
        
        long[][] dp = new long[r][c];
        dp[0][0] = 0;
        
        for (int j = 1; j < c; j++) {
            dp[0][j] = dp[0][j - 1] + g[0][j];
        }
        
        for (int i = 1; i < r; i++) {
            dp[i][0] = dp[i - 1][0] + g[i][0];
        }
        
        for (int i = 1; i < r; i++) {
            for (int j = 1; j < c; j++) {
                dp[i][j] = g[i][j] + Math.max(dp[i - 1][j], dp[i][j - 1]);
            }
        }
        
        System.out.println(dp[r - 1][c - 1]);
    }
    
    static class FastScanner {
        private final InputStream in;
        private final byte[] buf = new byte[1 << 16];
        private int ptr = 0, len = 0;
        
        FastScanner(InputStream is) {
            in = is;
        }
        
        int read() throws IOException {
            if (ptr >= len) {
                len = in.read(buf);
                ptr = 0;
                if (len <= 0) return -1;
            }
            return buf[ptr++];
        }
        
        int nextInt() throws IOException {
            int c;
            do {
                c = read();
            } while (c <= 32);
            int sgn = 1;
            if (c == '-') {
                sgn = -1;
                c = read();
            }
            int x = 0;
            while (c > 32) {
                x = x * 10 + (c - '0');
                c = read();
            }
            return x * sgn;
        }
        
        long nextLong() throws IOException {
            int c;
            do {
                c = read();
            } while (c <= 32);
            int sgn = 1;
            if (c == '-') {
                sgn = -1;
                c = read();
            }
            long x = 0;
            while (c > 32) {
                x = x * 10 + (c - '0');
                c = read();
            }
            return x * sgn;
        }
    }
}


// ===================================================
// PROBLEM 3: MERGE K SORTED ARRAYS - BUGGY JAVA
// ===================================================
import java.io.*;
import java.util.*;

public class Solution {
    static class Item {
        int v, i, j;
        Item(int v, int i, int j) {
            this.v = v;
            this.i = i;
            this.j = j;
        }
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int K = Integer.parseInt(br.readLine().trim());
        ArrayList<int[]> arrays = new ArrayList<>();
        PriorityQueue<Item> pq = new PriorityQueue<>((a, b) -> b.v - a.v);
        
        for (int i = 0; i < K; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            int n = Integer.parseInt(st.nextToken());
            int[] arr = new int[n];
            for (int j = 0; j < n; j++) {
                arr[j] = Integer.parseInt(st.nextToken());
            }
            arrays.add(arr);
            if (n > 0) {
                pq.add(new Item(arr[0], i, 1));
            }
        }
        
        StringBuilder sb = new StringBuilder();
        
        while (!pq.isEmpty()) {
            Item it = pq.poll();
            sb.append(it.v).append(' ');
            int[] arr = arrays.get(it.i);
            if (it.j <= arr.length) {
                pq.add(new Item(arr[it.j], it.i, it.j + 1));
            }
        }
        
        System.out.print(sb.toString().trim());
    }
}