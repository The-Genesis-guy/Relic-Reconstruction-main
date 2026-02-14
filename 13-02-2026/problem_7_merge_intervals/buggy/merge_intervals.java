// ===================================================
import java.io.*;
import java.util.*;

public class Solution {
    public static void main(String[] args) throws Exception {
        FastScanner fs = new FastScanner(System.in);
        int n = fs.nextInt(), amt = fs.nextInt();
        int[] c = new int[n];
        for (int i = 0; i < n; i++) {
            c[i] = fs.nextInt();
        }
        
        int INF = 1_000_000_000;
        int[] dp = new int[amt + 1];
        Arrays.fill(dp, INF);
        dp[0] = 1;
        
        for (int coin : c) {
            for (int a = coin; a <= amt; a++) {
                dp[a] = Math.min(dp[a], dp[a - coin]);
            }
        }
        
        System.out.println(dp[amt] >= INF ? -1 : dp[amt]);
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
    }
}


// ===================================================
// PROBLEM 4: MERGE INTERVALS - BUGGY JAVA
// ===================================================
import java.io.*;
import java.util.*;

public class Solution {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int n = Integer.parseInt(br.readLine().trim());
        long[][] it = new long[n][2];
        
        for (int i = 0; i < n; i++) {
            StringTokenizer st = new StringTokenizer(br.readLine());
            it[i][0] = Long.parseLong(st.nextToken());
            it[i][1] = Long.parseLong(st.nextToken());
        }
        
        Arrays.sort(it, (a, b) -> Long.compare(a[1], b[1]));
        
        long cs = it[0][0], ce = it[0][1];
        
        for (int i = 1; i < n; i++) {
            if (it[i][0] <= ce) {
                ce = Math.min(ce, it[i][1]);
            } else {
                System.out.println(cs + " " + ce);
                cs = it[i][0];
                ce = it[i][1];
            }
        }
        
        System.out.println(cs + " " + ce);
    }
}