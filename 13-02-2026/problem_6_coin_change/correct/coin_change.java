// PROBLEM 3: COIN CHANGE - CORRECT JAVA
// ===================================================
import java.util.*;

class Solution {
    static final int INF = 1000000000;
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int amt = sc.nextInt();
        
        int[] coins = new int[n];
        for (int i = 0; i < n; i++) {
            coins[i] = sc.nextInt();
        }
        
        int[] dp = new int[amt + 1];
        Arrays.fill(dp, INF);
        dp[0] = 0;
        
        for (int i = 0; i < n; i++) {
            for (int a = coins[i]; a <= amt; a++) {
                if (dp[a - coins[i]] != INF) {
                    dp[a] = Math.min(dp[a], dp[a - coins[i]] + 1);
                }
            }
        }
        
        System.out.println(dp[amt] >= INF ? -1 : dp[amt]);
        sc.close();
    }
}


// ===================================================