import java.io.*;
import java.util.*;

public class Q2_Subsequence {
    static long totalCount;
    
    public int lcs(String a, String b) {  // BUG 1: Not static
        int m = a.length();
        int n = b.length();
        int[][] dp = new int[m][n];  // BUG 2: Wrong size (needs +1)
        
        for(int i = 1; i <= m; i++) {  // BUG 3: ArrayIndexOutOfBounds
            for(int j = 1; j <= n; j++) {  // BUG 4: ArrayIndexOutOfBounds
                if(a.charAt(i) == b.charAt(j))  // BUG 5: Should be i-1, j-1
                    dp[i][j] = dp[i-1][j-1] + 1;
                else
                    dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);
            }
        }
        return dp[m][n];  // BUG 6: ArrayIndexOutOfBounds
    }
    
    public int countSub(String s, String sub) {  // BUG 7: Not static
        int cnt = 0;
        int sLen = s.length();
        int subLen = sub.length();
        
        for(int i = 0; i <= sLen - subLen; i++) {  // BUG 8: Off-by-one
            if(s.substring(i, i + subLen) == sub) cnt++;  // BUG 9: Use .equals()
        }
        return cnt;
    }
    
    public boolean isSubseq(String s, String sub) {  // BUG 10: Not static
        int j = 0;
        for(int i = 0; i < s.length() && j <= sub.length(); i++) {  // BUG 11: Should be j < sub.length()
            if(s.charAt(i) == sub.charAt(j)) j++;
        }
        return j == sub.length();
    }
    
    public int distinct(String s) {  // BUG 12: Not static
        HashSet<Character> set = new HashSet<>();
        for(int i = 0; i <= s.length(); i++)  // BUG 13: ArrayIndexOutOfBounds
            set.add(s.charAt(i));
        return set.size();
    }
    
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new FileReader(args[0]));  // BUG 14: No check
        BufferedWriter bw = new BufferedWriter(new FileWriter(args[1]));
        
        Q2_Subsequence sq = new Q2_Subsequence();
        int t = Integer.parseInt(br.readLine());
        
        for(int tc = 0; tc <= t; tc++) {  // BUG 15: Should be < t
            String s1 = br.readLine();  // BUG 16: No trim
            String s2 = br.readLine();  // BUG 17: No null check
            
            int lcsLen = sq.lcs(s1, s2);
            int cnt = sq.countSub(s1, s2);  // BUG 18: Wrong method for counting
            boolean isSub = sq.isSubseq(s1, s2);
            int d1 = sq.distinct(s1);
            int d2 = sq.distinct(s2);
            
            totalCount += cnt;
            
            System.out.println("LCS: " + lcsLen);  // BUG 19: stdout
            System.out.println("Count: " + cnt);  // BUG 20: stdout
            System.out.println("IsSubseq: " + isSub);  // BUG 21: stdout
            System.out.println("Distinct: " + d1 + " " + d2);  // BUG 22: stdout
        }
        
        System.out.println("Total: " + totalCount);  // BUG 23: stdout
        
        br.close();
        bw.close();  // BUG 24: Not flushed
        // BUG 25: No finally
        // BUG 26: DP array size wrong
        // BUG 27: LCS indexing wrong
        // BUG 28: Static variable pollution
        // BUG 29: isSubseq condition wrong
        // BUG 30: No input validation
        // BUG 31: Integer overflow in totalCount
        // BUG 32: Multiple off-by-one errors
    }
}
